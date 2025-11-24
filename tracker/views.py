"""
Views for Sleep Tracker
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import UserProfile, SleepSession, SleepGoal, SleepReminder, SleepStatistics
from .serializers import (
    UserProfileSerializer, SleepSessionSerializer,
    SleepSessionCreateSerializer, SleepGoalSerializer,
    SleepReminderSerializer, SleepStatisticsSerializer
)
from .tasks import sync_sleep_to_calendar
from .google_calendar import GoogleCalendarService


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for UserProfile
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def connect_google_calendar(self, request, pk=None):
        """Connect Google Calendar for the user"""
        profile = self.get_object()
        try:
            calendar_service = GoogleCalendarService(profile)
            calendar_service.authenticate()
            return Response({
                'message': 'Google Calendar connected successfully',
                'enabled': True
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class SleepSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SleepSession
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return SleepSessionCreateSerializer
        return SleepSessionSerializer

    def get_queryset(self):
        queryset = SleepSession.objects.filter(user=self.request.user)

        #Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(sleep_time__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(sleep_time__date__lte=end_date)

        return queryset

    def perform_create(self, serializer):
        """Create sleep session and optionally sync to calendar"""
        sleep_session = serializer.save(user=self.request.user)

        # Check if Google Calendar sync is enabled
        if hasattr(self.request.user, 'profile') and self.request.user.profile.google_calendar_enabled:
            #Trigger async task to sync to calendar
            sync_sleep_to_calendar.delay(sleep_session.id)

    def perform_update(self, serializer):
        """Update sleep session and optionally sync to calendar"""
        sleep_session = serializer.save()

        # Check if Google Calendar sync is enabled
        if hasattr(self.request.user, 'profile') and self.request.user.profile.google_calendar_enabled:
            sync_sleep_to_calendar.delay(sleep_session.id)

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent sleep sessions (last 7 days)"""
        seven_days_ago = timezone.now() - timedelta(days=7)
        sessions = self.get_queryset().filter(sleep_time_gte=seven_days_ago)
        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's sleep session"""
        today = timezone.now().date()
        sessions = self.get_queryset().filter(sleep_time_date=today)
        serializer = self.get_serializer(sessions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def sync_to_calendar(self, request, pk=None):
        """Manually sync a sleep session to Google Calendar"""
        sleep_session = self.get_object()

        if not hasattr(request.user, 'profile') or not request.user.profile.google_calendar_enabled:
            return Response(
                {'error': 'Google Calendar not connected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            sync_sleep_to_calendar.delay(sleep_session.id)
            return Response({'message': 'Sync initiated'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SleepGoalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SleepGoal
    """
    serializer_class = SleepGoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SleepGoal.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'])
    def active(self, request):
        goals = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(goals, many=True)
        return Response(serializer.data)


class SleepReminderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SleepReminder
    """
    serializer_class = SleepReminderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SleepReminder.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active reminders"""
        reminders = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(reminders, many=True)
        return Response(serializer.data)


class SleepStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for SleepStatistics (read-only)
    """
    serializer_class = SleepStatisticsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = SleepStatistics.objects.filter(user=self.request.user)

        # Filter by period type if provided
        period_type = self.request.query_params.get('period_type')
        if period_type:
            queryset = queryset.filter(period_type=period_type)

        return queryset

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get overall statistics summary"""
        # Get last 30 days of sessions
        thirty_days_ago = timezone.now() - timedelta(days=30)
        sessions = SleepSession.objects.filter(
            user=request.user,
            sleep_time__gte=thirty_days_ago
        )

        if not sessions.exists():
            return Response({
                'message': 'No sleep data available',
                'sessions_count': 0
            })

        total_hours = sum(s.duration_hours or 0 for s in sessions)
        avg_hours = total_hours / sessions.count()
        
        quality_sessions = sessions.filter(quality_rating__isnull=False)
        avg_quality = None
        if quality_sessions.exists():
            avg_quality = sum(s.quality_rating for s in quality_sessions) / quality_sessions.count()

        return Response({
            'period': '30_days',
            'total_sessions': sessions.count(),
            'total_sleep_hours': round(total_hours, 2),
            'average_sleep_hours': round(avg_hours, 2),
            'average_quality': round(avg_quality, 2) if avg_quality else None,
            'start_date': thirty_days_ago.date(),
            'end_date': timezone.now().date()
        })


# Template views
@login_required
def dashboard(request):
    """Dashboard view"""
    return render(request, 'tracker/dashboard.html')


@login_required
def sleep_log(request):
    """Sleep log view"""
    return render(request, 'tracker/sleep_log.html')
