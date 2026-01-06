"""Конфигурация Django Channels."""

import os

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")],
        },
    },
}
