"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import debugpy

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import chatbot.routing
from chatbot.middleware import JWTAuthMiddleware


DEBUG_PORT = 5678
DEBUG_HOST = "0.0.0.0"

debugpy.listen((DEBUG_HOST, DEBUG_PORT))
print(f"debugpy listening on {DEBUG_HOST}:{DEBUG_PORT}")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.dev")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": JWTAuthMiddleware(
            URLRouter(chatbot.routing.websocket_urlpatterns)
        ),
    }
)
