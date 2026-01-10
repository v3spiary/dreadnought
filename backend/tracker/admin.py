"""Конфигурация Django-админки."""

from django.apps import apps
from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered

# Get all models in the current project
models = apps.get_models()

for model in models:
    try:
        admin.site.register(model)
    except AlreadyRegistered:
        pass
    except Exception as e:
        print(f"Could not register model {model.__name__}: {e}")
