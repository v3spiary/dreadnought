"""
Настройки для тестирования.
"""

from .dev import *

# Используем SQLite в памяти для тестов
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Ускоряем тесты
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Отключаем кеширование для тестов
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Отключаем отправку email
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
