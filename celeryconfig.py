from kombu import Exchange, Queue

# Используем Redis в качестве брокера сообщений
BROKER_URL = 'redis://host.docker.internal:6379/0'

# Используем Redis в качестве backend'а для результатов выполнения задач
CELERY_RESULT_BACKEND = 'redis://host.docker.internal:6379/0'

CELERY_SEND_TASK_ERROR_EMAILS = False

CELERYBEAT_SCHEDULE = {
    'your_task_name': {
        'task': 'weather_app.tasks.send_notifications',
        'schedule': 3600,
    },
}

CELERY_DEFAULT_QUEUE = 'default'
CELERY_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
)

