from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Weather.settings')

app = Celery('Weather')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


app.conf.beat_schedule = {
    'send-notifications': {
        'task': 'Weather.tasks.send_notifications',
        'schedule': crontab(),
    },
}

