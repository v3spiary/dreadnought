"""Middleware для аутентификации веб-сокетов по JWT токену."""

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware


class JWTAuthMiddleware(BaseMiddleware):
    """Middleware для JWT аутентификации в WebSocket."""

    async def __call__(self, scope, receive, send):
        # Получаем заголовки из scope
        headers = {k.decode(): v.decode() for k, v in scope["headers"]}

        # Ищем Authorization header
        token = None
        if b"authorization" in headers:
            auth_header = headers[b"authorization"].decode("utf-8")
            token = auth_header

        # Также проверяем подпротоколы (на случай если фронт использует их)
        subprotocols = scope.get("subprotocols", [])
        for proto in subprotocols:
            token = proto
            break

        if token:
            scope["user"] = await self.get_user_from_token(token)
        else:
            scope["user"] = await self.get_anonymous_user()

        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user_from_token(self, token_str):
        """Аутентификация пользователя по JWT токену."""
        try:
            # Убираем 'Bearer ' если есть
            # if token_str.startswith('Bearer '):
            #     token_str = token_str[7:]

            # Импорты ВНУТРИ функции чтобы избежать AppRegistryNotReady
            from django.contrib.auth import get_user_model
            from rest_framework_simplejwt.tokens import AccessToken

            access_token = AccessToken(token_str)
            User = get_user_model()
            user = User.objects.get(id=access_token["user_id"])
            return user
        except Exception as e:
            return self.get_anonymous_user()

    @database_sync_to_async
    def get_anonymous_user(self):
        """Получение анонимного пользователя."""
        from django.contrib.auth.models import AnonymousUser

        return AnonymousUser()
