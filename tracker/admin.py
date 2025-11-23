"""
Admin configuration for Sleep Tracker
"""
from django.contrib import admin
from .models import UserProfile, SleepSession, SleepGoal, SleepReminder, SleepStatistics

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'target_sleep_hours', 'notification_enabled', 'google_calendar_enabled']
    list_filter = ['notification_enabled', 'google_calendar_enabled']
    search_fields = ['user_username', 'user_email']
    readonly_fields = ['created at', 'updated_at']

@admin.register(SleepSession)
class SleepSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'sleep_time', 'wake time', 'duration_hours', 'quality_rating', 'synced_to_calendar']
    list_filter = ['quality_rating', 'synced_to_calendar', 'sleep_time']
    search_fields = ['user_username', 'notes']
    readonly_fields = ['duration_hours', 'created_at', 'updated_at']
    date_hierarchy = 'sleep time'

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Sleep Timing', {
            'fields': ('sleep_time', 'wake_time', 'duration_hours')
        }), 
        ('Quality & Notes', {
            'fields': ('quality_rating', 'notes')
        }),
        ('Calendar Integration', {
            'fields': ('synced_to_calendar', 'calendar_event_id')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }), 
    )

@admin.register(SleepGoal)
class SleepGoalAdmin(admin.ModelAdmin):
    list_display= ['user', 'target_bedtime', 'target_wake_time', 'target_duration_hours', 'is_active']
    list_filter = ['is_active']
    search_fields = ['user_username']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(SleepReminder)
class SleepReminderAdmin(admin.ModelAdmin): 
    list_display = ['user', 'reminder type', 'reminder_time', 'is_active', 'last sent']
    list_filter = ['reminder_type', 'is_active']
    search_fields = ['user_username']
    readonly_fields = ['last sent, created at', 'updated at']

@admin.register(SleepStatistics)
class SleepStatisticsAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'period_type', 'average_sleep_hours', 'average_quality', 'sessions_count']
    list_filter = ['period_type', 'date']
    search_fields = ['user_username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'