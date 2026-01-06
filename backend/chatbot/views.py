"""Views приложения чат-бота (описываем логику)."""

import logging
import threading

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from chatbot.models import Chat, Message
from chatbot.serializers import ChatSerializer, MessageSerializer

# from .tasks import generate_ai_response

# Set up logger
logger = logging.getLogger(__name__)


class ChatViewSet(viewsets.ModelViewSet):
    """Класс, описывающий логику API для чатов."""

    serializer_class = ChatSerializer

    def get_queryset(self):
        """Пользователь видит только свои, не удаленные чаты."""
        return Chat.objects.filter(owner=self.request.user, deleted=False).order_by(
            "-created_at"
        )

    def perform_create(self, serializer):
        """При создании чата автоматически устанавливается владелец."""
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=["post"])
    def start_chat(self, request):
        try:
            from .consumers import _generate_ai_sync

            message = request.data.get("message", "").strip()
            if not message:
                return Response(
                    {"error": "Сообщение обязательно"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # СОЗДАЁМ ЧАТ И СООБЩЕНИЕ
            chat = Chat.objects.create(owner=request.user, name=message[:50])
            Message.objects.create(
                chat=chat,
                sender=request.user,
                content=message,
                message_type="text",
            )

            # ЗАПУСКАЕМ AI В ПОТОКЕ
            threading.Thread(
                target=_generate_ai_sync, args=(str(chat.id), message), daemon=True
            ).start()

            return Response({"chat_id": str(chat.id)}, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"START CHAT ERROR: {e}", exc_info=True)
            return Response(
                {"chat_id": str(chat.id)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        """GET /api/chats/{id}/messages/ - Получить все сообщения чата."""
        chat = self.get_object()
        messages = chat.messages.all().order_by("created_at")
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["patch"])
    def rename(self, request, pk=None):
        """Эндпоинт для переименования чата: PATCH /api/chats/{id}/rename/."""
        chat = self.get_object()
        new_name = request.data.get("name")
        if not new_name:
            return Response(
                {"error": "Новое имя не предоставлено"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        chat.name = new_name
        chat.save()
        return Response(ChatSerializer(chat).data)

    @action(detail=True, methods=["patch"])
    def toggle_pin(self, request, pk=None):
        """Эндпоинт для закрепления/открепления чата: PATCH /api/chats/{id}/toggle_pin/."""
        chat = self.get_object()
        chat.is_pinned = not chat.is_pinned
        chat.save()
        return Response(ChatSerializer(chat).data)

    def perform_destroy(self, instance):
        """Эндпоинт для логического удаления: DELETE /api/chats/{id}/."""
        instance.deleted = True
        instance.save()
