# AmbiDream
## A Sleep Tracker App
A comprehensive Django-based sleep tracking application with Google Calendar
integration and email notifications.

## Features
- **Sleep Session Tracking**: Log sleep times, wake times, and quality ratings
- **Google Calendar Integration**: Automatically sync sleep sessions to Google Calendar
- **Email Notifications**: Bedtime reminders, wake-up alerts, and weekly reports
- **Sleep Goals**: Set and track sleep goals with different schedules
- **Statistics & Analytics**: View daily, weekly, and monthly sleep statistics
- **REST API**: Full-featured API for mobile/web client integration
## Tech Stack
- **Backend**: Django 5.0 + Django REST Framework
- **Database**: SQLite (default) / PostgreSQL / MySQL
- **Task Queue**: Celery + Redis
- **Integrations**: Google Calendar API, Email (SMTP)
## Project Structure

```
sleep_tracker/
├─ manage.py
├─ requirements.txt
├─ .env.example
├─ sleep_tracker_project/
│   ├─ _init _. py
│   ├─ settings.py
│   ├─ urls.py
│   ├─ wsgi.py
│   ├─ asgi.py
│   ├─ celery.py
┗━  tracker/
    ├─ __init__.py
    ├─ models.py            # Database models
    ├─ views.py             # API views and viewsets
    ├─ serializers.py       # DRF serializers
    ├─ urls.py              # URL routing
    ├─ admin.py             # Django admin configuration
    ├─ apps.py              # App configuration
    ├─ signals.py           # Django signals
    ├─ tasks.py             # Celery tasks
    ├─ notifications.py     # Email notification service
    ┗━ google_calendar.py   # Google Calendar integration
```

## Setup Instructions

### 1. Create Virtual Environment (For Windows)

Navigate to project

``` bash
cd `url to file`
python3 -m venv venv
venvScripts\activate.bat         # CMD
# OR
venv\Scripts\Activate.ps1       # PowerShell
# OR
source venv/Scripts/activate    # Git Bash
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

```bash
cp .env.example .env
```

Edit `.env` and configure:
-`SECRET_KEY`: Generate with `python -c "from django.core.management.utils import
get_random_secret_key; print(get_random_secret_key())"`
- Email settings (Gmail or other SMTP provider)
- Redis URL for Celery

### 4. Google Calendar API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download credentials and save as `credentials.json` in project root

### 5. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

### 7. Run Development Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000/admin` to access the admin panel.

### 8. Start Celery Worker (Optional, for background tasks)

In a separate terminal:

```bash
# Start Redis (if not already running)
redis-server

# Start Celery worker
celery -A sleep_tracker_project worker -l info

# Start Celery beat (for scneduled tasks)
celery -A sleep_tracker_project beat -l info
```

## API Endpoints

### Authentication
- All endpoints require authentication (Session or Token)

### User Profile
- `GET /api/profiles/me/` - Get current user's profile
- `PATCH /api/profiles/{id}/` - Update profile
- `POST /api/profiles/{id}/connect_google_calendar/` - Connect Google Calendar

### Sleep Sessions
- `GET /api/sleep-sessions/` - List all sleep sessions
- `POST /api/sleep-sessions/` - Create new sleep session
- `GET /api/sleep-sessions/{id}/` - Get specific session
- `PATCH /api/sleep-sessions/{id}/` - Update session
- `DELETE /api/sleep-sessions/{id}/` - Delete session
- `GET /api/sleep-sessions/recent/` - Get last 7 days
- `GET /api/sleep-sessions/today/` - Get today's sessions
- `POST /api/sleep-sessions/{id}/sync_to_calendar/` - Manually sync to calendar

### Sleep Goals
- `GET /api/goals/` - List all goals
- `POST /api/goals/` - Create new goal
- `GET /api/goals/active/` - Get active goals
- `PATCH /api/goals/{id}/` - Update goal
- `DELETE /api/goals/{id}/` - Delete goal

### Sleep Reminders
- `GET /api/reminders/` - List all reminders
- `POST /api/reminders/` - Create new reminder
- `GET /api/reminders/active/` - Get active reminders
- `PATCH /api/reminders/{id}/` - Update reminder
- `DELETE /api/reminders/{id}/` - Delete reminder

### Statistics
- `GET /api/statistics/` - List statistics
- `GET /api/statistics/summary/` - Get 30-day summary

## Email Configuration (Gmail)
For Gmail, you need to:
1. Enable 2-factor authentication on your Google account
2. Generate an App Password: Google Account - Security - 2-Step Verification - App
Passwords
3. Use the app password in 'EMAIL_HOST_PASSWORD' in '.env'

## Celery Tasks

The following background tasks are available:
- `send_bedtime_reminders` - Send bedtime reminders
- `send_wake_reminders` - Send wake-up reminders
- `send_log_reminders` - Remind users to log sleep
- `sync_sleep_to_calendar` - Sync sleep session to Google Calendar
- `calculate_daily_statistics` - Calculate daily stats
- `calculate_weekly_statistics` - Calculate weekly stats
- `send_weekly_reports` - Send weekly email reports

## Models Overview

### UserProfile
Extended user profile with sleep preferences, notification settings, and Google
Calendar credentials.

### SleepSession
Individual sleep session tracking with start/end times, quality rating, and notes.

### SleepGoal
User-defined sleep goals with target bedtimes and wake times.

### SleepReminder
Scheduled reminders for bedtime, wake time, or logging.

### SleepStatistics
Aggregated sleep statistics (daily, weekly, monthly).

## Next Steps
1. Create frontend templates for dashboard and sleep log
2. Implement user registration and authentication
3. Add data visualization (charts, graphs)
4. Create mobile app using the REST API
5. Add more advanced analytics
6. Implement sleep quality insights using AI/ML
## License

MIT License

## Support

Create Jira Issue

For issues and questions, please create an issue in the repository.
