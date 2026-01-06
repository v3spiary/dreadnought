"""Конфигурация сборки метрик."""

import json
import logging
import os
from datetime import timedelta
from os import environ
from pathlib import Path

from celery.schedules import crontab
from django.core.management.utils import get_random_secret_key
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

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

# Настройки для Django-Prometheus
PROMETHEUS_METRIC_EXPORT_PORT_RANGE = range(8001, 8050)

# Настройки для экспорта метрик Prometheus
PROMETHEUS_PUSH_GATEWAY = environ.get(
    "PROMETHEUS_PUSH_GATEWAY", "http://prometheus:9091"
)
PROMETHEUS_PUSH_INTERVAL = int(environ.get("PROMETHEUS_PUSH_INTERVAL", "30"))

# Prometheus для Celery
CELERY_WORKER_PROMETHEUS_PORTS = environ.get(
    "CELERY_WORKER_PROMETHEUS_PORTS", "8880,8881"
).split(",")
