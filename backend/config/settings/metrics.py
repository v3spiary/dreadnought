"""Конфигурация сборки метрик."""

from os import environ

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
