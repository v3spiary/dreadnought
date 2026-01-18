"""Конфигурация всего проекта."""

import os
from datetime import timedelta
from os import environ
from pathlib import Path

from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = environ.get("SECRET_KEY")

DEBUG = True

HOST = environ.get("API_HOST")

PORT = environ.get("API_PORT")

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "backend",
    HOST,
]

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    f"http://{HOST}",
    f"http://{HOST}:{PORT}",
]

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://127.0.0.1",
    "http://localhost",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    f"http://{HOST}",
    f"http://{HOST}:{PORT}",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_ALL_ORIGINS = True

DATETIME_FORMAT = "%d.%m.%Y %H:%M"

DATE_FORMAT = "%d.%m.%Y"

TIME_FORMAT = "%H:%M"

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Мониторинг и метрики
    "django_prometheus",
    # Celery
    "django_celery_beat",
    "django_celery_results",
    # Channels для WebSocket
    "channels",
    # REST framework
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "djoser",
    "drf_spectacular",
    "django_filters",
    "corsheaders",
    "storages",
    # Кастомные приложения
    "auth_app",
    "chatbot",
    "tracker",
    "collector",
]

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

# AI Settings
AI_MAX_WORKERS = 3  # Максимальное количество параллельных AI генераций
DEFAULT_AI_MODEL = "deepseek-r1:1.5b"  # Модель по умолчанию
DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."

# Ollama Settings
OLLAMA_API_URL = "http://ollama:11434/api/generate"
OLLAMA_TIMEOUT = 300  # Таймаут в секундах (5 минут)

# Chat Settings
MAX_MESSAGE_LENGTH = 10000  # Максимальная длина сообщения
MAX_ACTIVE_CHATS_PER_USER = 5  # Максимальное количество активных чатов

# WebSocket Settings
WEBSOCKET_PING_INTERVAL = 30  # Интервал ping в секундах
WEBSOCKET_PING_TIMEOUT = 60  # Таймаут ping в секундах

# Настройки OpenTelemetry
# OTEL_ENABLED = environ.get("OTEL_ENABLED", "false").lower() == "true"
# OTEL_EXPORTER_OTLP_ENDPOINT = environ.get(
#     "OTEL_EXPORTER_OTLP_ENDPOINT", "http://tempo:4317"
# )
# OTEL_SERVICE_NAME = environ.get("OTEL_SERVICE_NAME", "deadwood-api")
# OTEL_PYTHON_LOG_CORRELATION = (
#     environ.get("OTEL_PYTHON_LOG_CORRELATION", "true").lower() == "true"
# )

# # Настройка провайдера трассировки
# trace.set_tracer_provider(TracerProvider())

# # Настройка экспортера для Tempo
# otlp_exporter = OTLPSpanExporter(
#     endpoint=OTEL_EXPORTER_OTLP_ENDPOINT,
#     insecure=True,
# )

# # Добавление процессора для пакетной обработки
# span_processor = BatchSpanProcessor(otlp_exporter)
# trace.get_tracer_provider().add_span_processor(span_processor)

# # Инструментация Django
# DjangoInstrumentor().instrument()
# RedisInstrumentor().instrument()
# Psycopg2Instrumentor().instrument()
# CeleryInstrumentor().instrument()
# LoggingInstrumentor().instrument(
#     set_logging_format=True,
#     log_level=logging.INFO,
# )

# Настройки Prometheus
PROMETHEUS_EXPORT_MIGRATIONS = False  # Отключаем экспорт миграций
PROMETHEUS_LATENCY_BUCKETS = (
    0.01,
    0.025,
    0.05,
    0.075,
    0.1,
    0.25,
    0.5,
    0.75,
    1.0,
    2.5,
    5.0,
    7.5,
    10.0,
    25.0,
    50.0,
    75.0,
    float("inf"),
)

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")],
        },
    },
}

# Настройки Celery
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = "django-db"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "Europe/Moscow"
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
CELERY_WORKER_HIJACK_ROOT_LOGGER = False

# Prometheus для Celery
CELERY_WORKER_PROMETHEUS_PORTS = environ.get(
    "CELERY_WORKER_PROMETHEUS_PORTS", "8880,8881"
).split(",")

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

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DATETIME_FORMAT": "%d.%m.%Y %H:%M",
    "DATE_FORMAT": "%d.%m.%Y",
    "TIME_FORMAT": "%H:%M",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Builder Platform API",
    "DESCRIPTION": "",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": "/api/",
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": True,
    },
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer {token}"',
        }
    },
    "SECURITY": [{"Bearer": []}],
    "AUTHENTICATION_WHITELIST": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "JWK_URL": None,
    "LEEWAY": 0,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_COOKIE_NAME": "refresh_token",
    "REFRESH_TOKEN_COOKIE_HTTPONLY": True,
    "REFRESH_TOKEN_COOKIE_SECURE": True,
    "REFRESH_TOKEN_COOKIE_SAMESITE": "Lax",
    "REFRESH_TOKEN_COOKIE_PATH": "/",
}

DJOSER = {
    "PASSWORD_RESET_CONFIRM_URL": "https://deadwood.ru/auth/reset-password-confirm/confirm/{uid}/{token}",
    "ACTIVATION_URL": "#/activate/{uid}/{token}",
    "SEND_ACTIVATION_EMAIL": False,
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

EMAIL_HOST = environ.get("EMAIL_HOST")

EMAIL_PORT = environ.get("EMAIL_PORT")

EMAIL_USE_TLS = environ.get("EMAIL_USE_TLS")

EMAIL_HOST_USER = environ.get("EMAIL_HOST_USER")

EMAIL_HOST_PASSWORD = environ.get("EMAIL_HOST_PASSWORD")

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Prometheus для базы данных
DATABASES = {
    "default": {
        "ENGINE": "django_prometheus.db.backends.postgresql",
        "NAME": environ.get("POSTGRES_DB"),
        "USER": environ.get("POSTGRES_USER"),
        "PASSWORD": environ.get("POSTGRES_PASSWORD"),
        "HOST": environ.get("DB_HOST"),
        "PORT": environ.get("DB_PORT", "5432"),
    }
}

# Настройки логирования с ротацией
# LOG_LEVEL = environ.get("LOG_LEVEL", "INFO").upper()

# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {
#         "simple": {
#             "format": "[%(levelname)s] %(message)s",
#             "style": "%",
#             "datefmt": "%Y-%m-%d %H:%M:%S",
#         },
#         "verbose": {
#             "format": """
#                 %(asctime)s
#                 [%(levelname)s]
#                 trace_id=%(otelTraceID)s
#                 span_id=%(otelSpanID)s
#                 resource.service.name=%(otelServiceName)s
#                 -
#                 [%(threadName)s]
#                 -
#                 %(name)s
#                 -
#                 (%(filename).%(funcName)s(%(lineno)d)
#                 -
#                 %(message)s
#                 """,
#             "style": "%",
#             "datefmt": "%Y-%m-%d %H:%M:%S",
#         },
#         "json": {
#             "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
#             "format": json.dumps(
#                 {
#                     "asctime": "%(asctime)s",
#                     "name": "%(name)s",
#                     "levelname": "%(levelname)s",
#                     "message": "%(message)s",
#                     "module": "%(module)s",
#                     "funcName": "%(funcName)s",
#                     "lineno": "%(lineno)d",
#                     "process": "%(process)d",
#                     "thread": "%(thread)d",
#                     "otelTraceID": "%(otelTraceID)s",
#                     "otelSpanID": "%(otelSpanID)s",
#                     "otelTraceSampled": "%(otelTraceSampled)s",
#                     "otelServiceName": "%(otelServiceName)s",
#                 }
#             ),
#             "json_ensure_ascii": False,
#             "rename_fields": {
#                 "asctime": "timestamp",
#                 "levelname": "level",
#                 "name": "logger",
#             },
#         },
#     },
#     "handlers": {
#         "console": {
#             "class": "logging.StreamHandler",
#             "formatter": "json",
#         },
#     },
#     "loggers": {
#         "": {
#             "handlers": ["console"],
#             "level": LOG_LEVEL,
#             "propagate": True,
#         },
#         "asgi": {
#             "handlers": ["console"],
#             "level": LOG_LEVEL,
#             "propagate": False,
#         },
#         "uvicorn": {
#             "handlers": ["console"],
#             "level": "INFO",
#             "propagate": False,
#         },
#         "uvicorn.access": {
#             "handlers": ["console"],
#             "level": "INFO",
#             "propagate": False,
#         },
#         "uvicorn.error": {
#             "handlers": ["console"],
#             "level": "INFO",
#             "propagate": False,
#         },
#     },
# }

# Настройки для Django-Prometheus
PROMETHEUS_METRIC_EXPORT_PORT_RANGE = range(8001, 8050)

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "ru-ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True

# AWS S3/MinIO settings
AWS_ACCESS_KEY_ID = environ.get("MINIO_ACCESS_KEY", "minioadmin")
AWS_SECRET_ACCESS_KEY = environ.get("MINIO_SECRET_KEY", "minioadmin")
AWS_STORAGE_BUCKET_NAME = environ.get("MINIO_BUCKET_NAME", "mybucket")
AWS_S3_ENDPOINT_URL = environ.get("MINIO_ENDPOINT_URL", "http://minio:9000")
AWS_S3_CUSTOM_DOMAIN = None
AWS_DEFAULT_ACL = None
AWS_S3_VERIFY = False
AWS_S3_FILE_OVERWRITE = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_DIR = os.path.join(BASE_DIR, "static")
STATIC_ROOT = STATIC_DIR

DEFAULT_FILE_STORAGE = "config.storage.MediaMinIOStorage"

# Media files settings
MEDIA_URL = f"{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/"
MEDIA_ROOT = ""
MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = (
    True  # Optional: create bucket if it doesn't exist
)
MINIO_STORAGE_AUTO_CREATE_MEDIA_POLICY = (
    True  # Optional: set public policy for media bucket
)

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
