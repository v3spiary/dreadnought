"""Эндпоинты приложения авторизации."""

from django.urls import include, path

from . import views

urlpatterns = [
    path("", include("djoser.urls")),
    path("jwt/create/", views.jwt_create, name="jwt-create"),
    path("jwt/refresh/", views.jwt_refresh, name="jwt-refresh"),
    path("jwt/logout/", views.jwt_logout, name="jwt-logout"),
]
