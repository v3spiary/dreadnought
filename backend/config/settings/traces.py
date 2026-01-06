"""Конфигурация сборки трейсов."""

import logging
from os import environ

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Настройки OpenTelemetry
OTEL_ENABLED = environ.get("OTEL_ENABLED", "false").lower() == "true"
OTEL_EXPORTER_OTLP_ENDPOINT = environ.get(
    "OTEL_EXPORTER_OTLP_ENDPOINT", "http://tempo:4317"
)
OTEL_SERVICE_NAME = environ.get("OTEL_SERVICE_NAME", "deadwood-api")
OTEL_PYTHON_LOG_CORRELATION = (
    environ.get("OTEL_PYTHON_LOG_CORRELATION", "true").lower() == "true"
)

# Настройка провайдера трассировки
trace.set_tracer_provider(TracerProvider())

# Настройка экспортера для Tempo
otlp_exporter = OTLPSpanExporter(
    endpoint=OTEL_EXPORTER_OTLP_ENDPOINT,
    insecure=True,
)

# Добавление процессора для пакетной обработки
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Инструментация Django
DjangoInstrumentor().instrument()
RedisInstrumentor().instrument()
Psycopg2Instrumentor().instrument()
CeleryInstrumentor().instrument()
LoggingInstrumentor().instrument(
    set_logging_format=True,
    log_level=logging.INFO,
)
