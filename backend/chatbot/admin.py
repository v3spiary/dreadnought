"""Конфиг админки для приложения чат-бота."""

# flake8: noqa
from django.contrib import admin

from chatbot.models import *

admin.site.register(Chat)
admin.site.register(Message)
