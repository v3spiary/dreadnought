"""Сериализаторы для приложения чатбота."""

from rest_framework import serializers

from chatbot.models import Chat, Message


class StartChatSerializer(serializers.Serializer):
    """Сериализатор для создания нового чата"""

    message = serializers.CharField(
        max_length=10000,
        min_length=1,
        required=True,
        help_text="Первое сообщение в чате",
    )

    def validate_message(self, value):
        """Валидация сообщения"""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Сообщение не может быть пустым")
        return value


class MessageSerializer(serializers.ModelSerializer):
    """Сериализатор для сообщения в чате."""

    class Meta:
        """Метаданные сериализатора."""

        model = Message
        fields = ["id", "content", "sender", "message_type", "is_edited", "created_at"]


class ChatSerializer(serializers.ModelSerializer):
    """Сериализатор для чата."""

    # Вложенная информация о последних сообщениях
    latest_messages = MessageSerializer(
        source="get_latest_messages", many=True, read_only=True
    )

    class Meta:
        """Метаданные сериализатора."""

        model = Chat
        fields = ["id", "name", "is_pinned", "created_at", "latest_messages"]
        read_only_fields = ["id", "name", "owner", "created_at", "latest_messages"]

    def get_latest_messages(self, obj):
        """Возвращает сообщения."""
        messages = obj.messages.all().order_by("-created_at")[:5]
        return messages
