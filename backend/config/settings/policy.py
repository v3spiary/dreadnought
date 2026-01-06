"""Конфигурация политики управления адресами и контентом."""

from os import environ

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

CORS_ALLOW_ALL_ORIGINS = False  # DEBUG
