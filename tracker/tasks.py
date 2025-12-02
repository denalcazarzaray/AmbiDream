"""
Celery tasks for AmbiDream 
"""
from celery import shared_task
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from .models import SleepReminder, SleepSession, SleepStatistics, UserProfile
from .notifications import EmailNotificationService
from .google_calendar import GoogleCalendarService


@shared_task
def send_bedtime_reminders():
    """"
    Send bedtime reminders to users
    """
    current_time = timezone.now().time()
    reminders = SleepReminder.objects.filter(
        reminder_type='bedtime',
        is_active=True,
        reminder_time__hour=current_time.hour,
        reminder_time_minute=current_time.minute
    )

    sent_count = 0
    for reminder in reminders:
        if reminder.user.profile.notification_enabled:
            result = EmailNotificationService.send_bedtime_reminder(
            reminder.user,
            reminder.reminder_time
            )
        if result:
            reminder.last_sent = timezone.now()
            reminder.save()
            sent_count += 1

    return f"Sent {sent_count} bedtime reminders"

@shared_task
def send_wake_reminders():
    """"
    Send wake time reminders to users
    """
    current_time = timezone.now().time()
    reminders = SleepReminder.objects.filter(
        reminder_type='wake',
        is_active=True,
        reminder_time_hour=current_time.hour,
        reminder_time_minute=current_time.minute
    )

    sent_count = 0
    for reminder in reminders:
        if reminder.user.profile.notification_enabled:
            result = EmailNotificationService.send_wake_reminder(
                reminder.user,
                reminder.reminder_time
            )
            if result:
                reminder.last_sent = timezone.now()
                reminder.save()
                sent_count += 1

    return f"Sent {sent_count} wake reminders"

@shared_task
def send_log_reminders():
    """
    Send reminders to log sleep sessions
    """
    current_time = timezone.now().time()
    reminders = SleepReminder.objects.filter(
        reminder_type='log',
        is_active=True,
        reminder_time_hour=current_time.hour,
        reminder_time_minute=current_time.minute
    )

    sent_count = 0
    for reminder in reminders:
        if reminder.user.profile.notification_enabled:
            # Check if user has logged sleep for yesterday
            yesterday = timezone.now().date() - timedelta(days=1)
            has_logged = SleepSession.objects.filter(
                user=reminder.user,
                sleep_time__date=yesterday
            ).exists()

            if not has_logged:
                result = EmailNotificationService.send_log_reminder(reminder.user)
                if result:
                    reminder.last_sent = timezone.now()
                    reminder.save()
                    sent_count += 1

    return f"Sent {sent_count} log reminders"


@shared_task
def sync_sleep_to_calendar(sleep_session_id):
    """
    Sync a sleep session to Google Calendar
    Args:
     sleep_session_id: ID of the SleepSession to sync
    """
    try:
        sleep_session = SleepSession.objects.get(id=sleep_session_id)
        user_profile = sleep_session.user.profile

        if not user_profile.google_calendar_enabled:
            return "Google Calendar not enabled for this user"
        
        calendar_service = GoogleCalendarService(user_profile)

        if sleep_session.synced_to_calendar and sleep_session.calendar_event_id:
            # Update existing event
            event_id = calendar_service.update_sleep_event (
                sleep_session.calendar_event_id,
                sleep_session
            )
            return f"Updated calendar event: {event_id}"
        else:
        # Create new event
            event_id = calendar_service.create_sleep_event(sleep_session)
            if event_id:
                sleep_session.calendar_event_id = event_id
                sleep_session.synced_to_calendar = True
                sleep_session.save()
                return f"Created calendar event: {event_id}"
        
            return "Failed to sync to calendar"

    except SleepSession.DoesNotExist:
        return f"Sleep session {sleep_session_id} not found"
    except Exception as e:
        return f"Error syncing to calendar: {str(e)}"


@shared_task
def calculate_daily_statistics():
    """
    Calculate daily sleep statistics for all users
    """
    yesterday = timezone.now().date() - timedelta(days=1)
    users = User.objects.filter(sleep_sessions__sleep_time__date=yesterday).distinct()

    stats_created = 0
    for user in users:
        sessions = SleepSession.objects.filter(
            user=user,
            sleep_time__date=yesterday
        )

        if sessions.exists():
            total_hours = sum(s.duration_hours or 0 for s in sessions)
            avg_hours = total_hours / sessions.count()
            quality_sessions = sessions.filter(quality_rating__isnull=False)
            avg_quality = None
            if quality_sessions.exists():
                avg_quality = sum(s.quality_rating for s in quality_sessions) / quality_sessions.count()

            SleepStatistics.objects.update_or_create(
                user=user,
                date=yesterday,
                period_type='daily',
                defaults={
                    'total_sleep_hours': total_hours,
                    'average_sleep_hours': avg_hours,
                    'average_quality': avg_quality,
                    'sessions_count': sessions.count()
                }
            )
            stats_created += 1

    return f"Created/updated {stats_created} daily statistics"

@shared_task
def calculate_weekly_statistics():
    """
    Calculate weekly sleep statistics for all users
    """
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday()) # Monday
    week_end = week_start + timedelta(days=6) # Sunday

    users = User.objects. filter(
        sleep_sessions__sleep_time__date__gte=week_start,
        sleep_sessions__sleep_time__date__lte=week_end
    ).distinct()

    stats_created = 0
    for user in users:
        sessions = SleepSession.objects.filter(
            user=user,
            sleep_time__date__gte=week_start,
            sleep_time__date__lte=week_end
        )

        if sessions.exists():
            total_hours = sum(s.duration_hours or 0 for s in sessions)
            avg_hours = total_hours / sessions.count()
            quality_sessions = sessions.filter(quality_rating__isnull=False)
            avg_quality = None
            if quality_sessions.exists():
                avg_quality = sum(s.quality_rating for s in quality_sessions) / quality_sessions.count()
            
            SleepStatistics.objects.update_or_create(
                user=user,
                date=week_start,
                period_type='weekly',
                defaults={
                    'total_sleep_hours'; total_hours,
                    'average_sleep_hours': avg_hours,
                    'average_quality': avg_quality,
                    'sessions_count': sessions.count()
                }
            )
            stats_created += 1

    return f"Created/updated {stats_created} weekly statistics"

@shared_task
def send_weekly_reports():
    """
    Send weekly sleep reports to all active users
    """
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday() + 7) # Last Monday

    stats = SleepStatistics.objects.filter(
        date=week_start,
        period_type='weekly'
    )

    sent_count = 0
    for stat in stats:
        if stat.user.profile.notification_enabled:
            statistics = {
                'avg_hours': float (stat.average_sleep_hours),
                'sessions': stat.sessions_count,
                'avg_quality': float(stat.average_quality) if stat.average_quality else 0,
                'goal_achievement': float(stat.goal_achievement_rate) if stat.goal_achievement_rate else 0
            }

        result = EmailNotificationService.send_weekly_report(
            stat.user,
            statistics
        )
        if result:
            sent_count += 1

    return f"Sent {sent_count} weekly reports"