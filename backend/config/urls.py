"""Эндпоинты проекта, их объявление начинается здесь."""

import os
import logging

from django.conf import settings
from django.contrib import admin
from django.http import Http404, HttpResponse
from django.urls import include, path, re_path
from django.views import View
from django.views.static import serve
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# Set up logger
logger = logging.getLogger(__name__)


class SPAView(View):
    """
    Отображение фронта.
    """

    def get(self, request, *args, **kwargs):
        """
        GET-запрос для бандла.
        """
        index_file = os.path.join(settings.BUNDLE_DIR, "index.html")
        if os.path.exists(index_file):
            with open(index_file, "rb") as f:
                return HttpResponse(f.read(), content_type="text/html")
        raise Http404("index.html not found in STATIC_ROOT.")


urlpatterns = [
    path("not_your_fucking_business//", admin.site.urls),  # админка
    path("api/v1/auth/", include("auth_app.urls")),
    path("api/v1/chatbot/", include("chatbot.urls")),
    path("api/v1/tracker/", include("tracker.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("", include("django_prometheus.urls")),
]

# 1. Статика Django
urlpatterns += [
    re_path(
        r"^static/(?P<path>.*)$",
        serve,
        {
            "document_root": settings.STATIC_ROOT,
        },
    ),
]

if settings.DEBUG == False:

    # 2. Статика SPA (assets)
    try:
        urlpatterns += [
            re_path(
                r"^assets/(?P<path>.*)$",
                serve,
                {
                    "document_root": os.path.join(settings.BUNDLE_DIR, "assets"),
                },
            ),
        ]
    except Exception as e:
        logger.warning("Url Bundle Error detected", exc_info=True)

    # 3. SPAView
    urlpatterns += [
        re_path(r"^(?!api|admin|static|assets).*$", SPAView.as_view(), name="spa"),
    ]
