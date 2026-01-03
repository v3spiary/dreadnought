"""Конфиг админки для приложения чат-бота."""

# flake8: noqa
from chatbot.models import *
from django.contrib import admin

admin.site.register(Chat)
admin.site.register(Message)
