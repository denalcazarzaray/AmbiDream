"""
Celery configuration for sleep_tracker_project.
"""

import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sleep_tracker_project.settings')

app = Celery('sleep_tracker_project')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)

def debug task(self):
    print(f'Request: {self, request!r}')