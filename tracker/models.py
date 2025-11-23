"""
Sleep Tracker Models
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class UserProfile(models.Model):
    """
    Extended user profile with sleep-related preferences
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    target_sleep_hours = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=8.0,
        validators=[MinValueValidator(1.0), MaxValueValidator(24.0)]
    )
    timezone = models. CharField(max_length=58, default='UTC')
    notification_enabled = models.BooleanField(default=True)
    notification_time = models.TimeField(null=True, blank=True, help_text="Time to receive daily sleep reminders")
    google_calendar_enabled = models.BooleanField(default=False)
    google_refresh_token = models.TextField(blank True, null True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

class SleepSession(models. Model):
    """
    Individual sleep session tracking
    """
    QUALITY_CHOICES = [
        (1, 'Very Poor'),
        (2, 'Poor'),
        (3, 'Fair'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sleep_sessions')

    #Sleep timing 
    sleep_time = models.DateTimeField(help_text="When the user went to sleep")
    wake_time = models.DateTimeField(help_text="When the user woke up")

    #Sleep quality metrics 
    quality_rating = models.IntegerField(
        choices=QUALITY_CHOICES,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    notes = models.TextField(blank=True, help_text="Additional notes about sleep session")

    #Calculated fields 
    duration_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True, 
        help_text="Calculated sleep duration in hours"
    )

    #Integration tracking 
    synced_to_calendar = models.BooleanField(default=False)
    calendar_event_id = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """
        Calculate duration before saving
        """
        if self.sleep_time and self.wake_time:
            duration = self.wake_time - self.sleep_time
            self.duration_hours = round(duration.total_seconds() / 3600, 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.sleep_time.date()} ({self.duration_hours}h)"

    class Meta:
        verbose_name = "Sleep Session"
        verbose_name_plural = "Sleep Sessions"
        ordering = ['-sleep_time']
        indexes = [
            models.Index(fields=['-sleep_time']),
            models.Index(fields=['user', '-sleep_time']),
        ]

class SleepGoal (models.Model):
    """
    User's sleep goals and targets
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sleep_goals')

    target_bedtime = models.TimeField(help_text="Target time to go to bed")
    target_wake_time = models.TimeField(help_text="Target time to wake up")
    target_duration_hours = models. DecimalField(
        max_digits=3,
        decimal_places=1,
        default=8.0,
        validators=[MinValueValidator(1.0), MaxValueValidator(24.0)]
    )

    #Days of week (for different schedules on weekdays vs weekends) 
    days_of_week = models.JSONField(
        default=list,
        help_text="List of days this goal applies to (8-Monday, 6-Sunday)"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Goal: {self.target_bedtime} - {self.target_wake_time}"

    class Meta:
        verbose_name = "Sleep Goal"
        verbose_name_plural = "Sleep Goals"

class SleepReminder(models.Model):
    """
    Scheduled reminders for sleep tracking
    """
    REMINDER TYPE_CHOICES = [
    ('bedtime', 'Bedtime Reminder'),
    ('wake', 'Wake Time Reminder'),
    ('log', 'Log Sleep Reminder'),
    ]

    user = models.ForeignKey (User, on_delete=models.CASCADE, related_name='sleep_reminders')
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPE_CHOICES)
    reminder_time = models.TimeField()

    is_active = models.BooleanField(default=True)
    message = models.TextField(blank=True, help_text="Custom reminder message")

    #Tracking 
    last_sent = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models. DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_reminder_type_display()} at {self.reminder_time}"

    class Meta:
        verbose_name = "Sleep Reminder"
        verbose_name_plural = "Sleep Reminders"

class SleepStatistics (models.Model):
    """
    Aggregated sleep statistics for reporting
    """
    user = models.ForeignKey (User, on_delete=models.CASCADE, related_name='sleep_statistics')

    #Period 
    date = models.DateField()
    period_type= models.CharField(
        max_length=20,
        choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')]
    )

    #Metrics 
    total_sleep_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    average_sleep_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    average_quality = models. DecimalField(
        max_digits=3
        decimal_places=2,
        null=True,
        blank=True
    )
    sessions_count = models.IntegerField(default=0)

    goal_achievement_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Percentage of days meeting sleep goals"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.period type} stats for {self.date}"

    class Meta:
        verbose_name = "Sleep Statistics"
        verbose_name_plural = "Sleep Statistics"
        unique_together = ['user', 'date', 'period_type']
        ordering = ['-date']