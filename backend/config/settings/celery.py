"""Конфигурация Celery."""

import os

from celery.schedules import crontab

# Настройки Celery
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = "django-db"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Europe/Moscow"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_WORKER_HIJACK_ROOT_LOGGER = False

# Пример периодических задач
CELERY_BEAT_SCHEDULE = {
    "daily-maintenance": {
        "task": "chatbot.tasks.daily_maintenance",
        "schedule": crontab(hour=0, minute=0),
    },
    "cleanup-old-traces": {
        "task": "config.tasks.cleanup_old_traces",
        "schedule": crontab(hour=3, minute=0),
        "kwargs": {"days": 30},
    },
}
