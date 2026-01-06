"""Конфигурация сборки логов."""

import json
from os import environ

LOG_LEVEL = environ.get("LOG_LEVEL", "INFO").upper()

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "[%(levelname)s] %(message)s",
            "style": "%",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "verbose": {
            "format": """
                %(asctime)s
                [%(levelname)s]
                trace_id=%(otelTraceID)s
                span_id=%(otelSpanID)s
                resource.service.name=%(otelServiceName)s
                -
                [%(threadName)s]
                -
                %(name)s
                -
                (%(filename).%(funcName)s(%(lineno)d)
                -
                %(message)s
                """,
            "style": "%",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": json.dumps(
                {
                    "asctime": "%(asctime)s",
                    "name": "%(name)s",
                    "levelname": "%(levelname)s",
                    "message": "%(message)s",
                    "module": "%(module)s",
                    "funcName": "%(funcName)s",
                    "lineno": "%(lineno)d",
                    "process": "%(process)d",
                    "thread": "%(thread)d",
                    "otelTraceID": "%(otelTraceID)s",
                    "otelSpanID": "%(otelSpanID)s",
                    "otelTraceSampled": "%(otelTraceSampled)s",
                    "otelServiceName": "%(otelServiceName)s",
                }
            ),
            "json_ensure_ascii": False,
            "rename_fields": {
                "asctime": "timestamp",
                "levelname": "level",
                "name": "logger",
            },
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
        "asgi": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "uvicorn": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
