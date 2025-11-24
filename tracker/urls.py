"""
URL routing for Sleep Tracker
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for API endpoints
router = DefaultRouter()
router.register(r'profiles', views.UserProfileViewSet, basename='profile')
router.register(r'sleep-sessions', views.SleepSessionViewSet, basename='sleep-session')
router.register(r'goals', views.SleepGoalViewSet, basename='goal')
router.register(r'reminders', views.SleepReminderViewSet, basename='reminder')
router.register(r'statistics', views.SleepStatisticsViewSet, basename='statistics')

app_name = 'tracker'

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),

    # Template views
    path('', views.dashboard, name='dashboard'),
    path('log/', views.sleep_log, name='sleep-log'),
]
