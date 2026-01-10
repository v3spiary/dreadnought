"""Эндпоинты приложения чатбота."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"chats", views.ChatViewSet, basename="chat")

urlpatterns = [
    path("", include(router.urls)),
]
