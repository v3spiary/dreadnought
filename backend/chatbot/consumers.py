# consumer.py
import json
import logging
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Optional

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.db import transaction

logger = logging.getLogger(__name__)

# Глобальный пул потоков для всех генераций
_AI_EXECUTOR = ThreadPoolExecutor(
    max_workers=getattr(settings, "AI_MAX_WORKERS", 3), thread_name_prefix="ai_worker"
)


class OllamaClient:
    """Клиент для работы с Ollama API"""

    @staticmethod
    def generate_response(
        chat_id: str,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        channel_layer=None,
        group_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Генерирует ответ от AI модели через Ollama API.

        Args:
            chat_id: ID чата
            prompt: Пользовательский промпт
            model: Название модели (по умолчанию из настроек)
            system_prompt: Системный промпт
            channel_layer: Канальный слой для отправки сообщений
            group_name: Имя группы для отправки сообщений

        Returns:
            Dict с результатом генерации
        """
        from asgiref.sync import async_to_sync

        from chatbot.models import Message

        # Настройки по умолчанию
        if model is None:
            model = getattr(settings, "DEFAULT_AI_MODEL", "deepseek-r1:1.5b")

        if system_prompt is None:
            system_prompt = getattr(settings, "DEFAULT_SYSTEM_PROMPT", "")

        if channel_layer is None:
            from channels.layers import get_channel_layer

            channel_layer = get_channel_layer()

        if group_name is None:
            group_name = f"chat_{chat_id}"

        full_response = ""
        message_id = "error"
        error = None

        try:
            # Подготавливаем данные для запроса
            request_data = {"model": model, "prompt": prompt, "stream": True}

            if system_prompt:
                request_data["system"] = system_prompt

            # Создаем запрос
            req = urllib.request.Request(
                getattr(settings, "OLLAMA_API_URL", "http://ollama:11434/api/generate"),
                data=json.dumps(request_data).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Django-ChatBot/1.0",
                },
                method="POST",
            )

            # Выполняем запрос с таймаутами
            timeout = getattr(settings, "OLLAMA_TIMEOUT", 300)  # 5 минут по умолчанию
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                for line in resp:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        data = json.loads(line.decode("utf-8"))
                    except json.JSONDecodeError as e:
                        logger.warning(
                            f"Failed to decode JSON line: {line[:100]}... Error: {e}"
                        )
                        continue

                    token = data.get("response", "")
                    if token:
                        full_response += token
                        # Отправляем чанк в WebSocket группу
                        try:
                            async_to_sync(channel_layer.group_send)(
                                group_name,
                                {
                                    "type": "ai_chunk",
                                    "chunk": token,
                                    "chat_id": chat_id,
                                },
                            )
                        except Exception as e:
                            logger.error(f"Failed to send chunk: {e}")
                            # Продолжаем генерацию даже если не удалось отправить чанк

                    # Проверяем завершение
                    if data.get("done", False):
                        # Логируем метрики генерации
                        if data.get("total_duration"):
                            logger.info(
                                f"AI generation completed for chat {chat_id[:8]}... "
                                f"Tokens: {len(full_response.split())}, "
                                f"Duration: {data.get('total_duration')}ms"
                            )
                        break

            # Сохраняем сообщение в БД
            if full_response:
                try:
                    with transaction.atomic():
                        ai_msg = Message.objects.create(
                            chat_id=chat_id,
                            content=full_response,
                            message_type="text",
                            sender=None,
                        )
                        message_id = str(ai_msg.id)

                        # Обновляем время последней активности чата
                        # ai_msg.chat.touch()  # Предполагается, что у модели Chat есть метод touch()

                except Exception as e:
                    logger.error(f"Failed to save AI message to DB: {e}", exc_info=True)
                    error = "Ошибка сохранения сообщения"
                    message_id = "db_error"
            else:
                error = "Пустой ответ от модели"
                message_id = "empty_response"

        except urllib.error.URLError as e:
            logger.error(f"Ollama connection error for chat {chat_id}: {e}")
            error = "Модель временно недоступна"
            message_id = "connection_error"

        except TimeoutError as e:
            logger.error(f"Ollama timeout for chat {chat_id}: {e}")
            error = "Превышено время ожидания ответа от модели"
            message_id = "timeout_error"

        except Exception as e:
            logger.error(
                f"Unexpected error during AI generation for chat {chat_id}: {e}",
                exc_info=True,
            )
            error = "Внутренняя ошибка сервера"
            message_id = "internal_error"

        finally:
            # Всегда отправляем сообщение о завершении
            try:
                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        "type": "ai_complete",
                        "message_id": message_id,
                        "chat_id": chat_id,
                        "error": error,
                    },
                )
            except Exception as e:
                logger.error(f"Failed to send completion message: {e}")

        return {
            "success": error is None,
            "message_id": message_id,
            "error": error,
            "response_length": len(full_response),
        }


class AIResponseTracker:
    """Трекер для отслеживания статуса AI генераций"""

    _active_generations = {}  # chat_id -> task_future

    @classmethod
    def start_generation(cls, chat_id: str, future):
        """Начать отслеживание генерации для чата"""
        cls._active_generations[chat_id] = future

    @classmethod
    def stop_generation(cls, chat_id: str):
        """Остановить отслеживание генерации для чата"""
        if chat_id in cls._active_generations:
            future = cls._active_generations.pop(chat_id)
            if not future.done():
                future.cancel()
                logger.info(f"Cancelled generation for chat {chat_id}")

    @classmethod
    def is_generating(cls, chat_id: str) -> bool:
        """Проверяет, идет ли генерация для чата"""
        if chat_id in cls._active_generations:
            future = cls._active_generations[chat_id]
            return not future.done()
        return False


class ServiceChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer для чата с AI"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.chat_id = None
        self.room_group_name = None

    async def connect(self):
        """Обработка подключения WebSocket"""

        self.user = self.scope["user"]
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]

        # Проверка аутентификации
        if self.user.is_anonymous:
            logger.warning(f"Anonymous user tried to connect to chat {self.chat_id}")
            await self.close(code=4001)  # Custom close code for auth failure
            return

        # Проверка прав доступа к чату
        try:
            chat_exists = await self._check_chat_access()
            if not chat_exists:
                logger.warning(
                    f"User {self.user.id} has no access to chat {self.chat_id}"
                )
                await self.close(code=4003)  # Custom close code for access denied
                return
        except Exception as e:
            logger.error(f"Error checking chat access: {e}")
            await self.close(code=4002)  # Custom close code for server error
            return

        # Подключаемся к группе чата
        self.room_group_name = f"chat_{self.chat_id}"

        try:
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.accept()

            logger.info(f"User {self.user.id} connected to chat {self.chat_id}")

            # Отправляем приветственное сообщение
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "connection_established",
                        "message": "Connected to chat",
                        "chat_id": self.chat_id,
                        "user_id": str(self.user.id),
                    }
                )
            )

        except Exception as e:
            logger.error(f"Error during WebSocket connect: {e}", exc_info=True)
            await self.close(code=4002)

    async def disconnect(self, close_code):
        """Обработка отключения WebSocket"""
        if hasattr(self, "room_group_name") and self.room_group_name:
            try:
                # Удаляем из группы
                await self.channel_layer.group_discard(
                    self.room_group_name, self.channel_name
                )

                # Отменяем активную генерацию для этого чата
                AIResponseTracker.stop_generation(self.chat_id)

                logger.info(
                    f"User {self.user.id if self.user else 'unknown'} "
                    f"disconnected from chat {self.chat_id}, code: {close_code}"
                )

            except Exception as e:
                logger.error(f"Error during WebSocket disconnect: {e}")

    async def receive(self, text_data):
        """Обработка входящих сообщений"""
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON received from user {self.user.id}")
            await self.send(
                text_data=json.dumps(
                    {"type": "error", "message": "Invalid JSON format"}
                )
            )
            return

        # Получаем сообщение
        content = data.get("message", "").strip()
        if not content:
            await self.send(
                text_data=json.dumps(
                    {"type": "error", "message": "Message cannot be empty"}
                )
            )
            return

        # Проверяем длину сообщения
        max_length = getattr(settings, "MAX_MESSAGE_LENGTH", 10000)
        if len(content) > max_length:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "error",
                        "message": f"Message too long (max {max_length} characters)",
                    }
                )
            )
            return

        # Проверяем, не идет ли уже генерация для этого чата
        if AIResponseTracker.is_generating(self.chat_id):
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "error",
                        "message": "Please wait for the current response to complete",
                    }
                )
            )
            return

        try:
            # 1. Сохраняем сообщение пользователя
            user_msg = await self._save_user_message(content)

            # 2. Отправляем эхо-сообщение в группу
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "user_message",
                    "message_id": str(user_msg.id),
                    "content": content,
                    "user_id": str(self.user.id),
                    "chat_id": self.chat_id,
                    "timestamp": (
                        user_msg.created_at.isoformat()
                        if hasattr(user_msg, "created_at")
                        else None
                    ),
                },
            )

            # 3. Запускаем AI генерацию в пуле потоков
            future = _AI_EXECUTOR.submit(
                OllamaClient.generate_response,
                chat_id=self.chat_id,
                prompt=content,
                channel_layer=self.channel_layer,
                group_name=self.room_group_name,
            )

            # Начинаем отслеживание генерации
            AIResponseTracker.start_generation(self.chat_id, future)

            logger.info(
                f"Started AI generation for chat {self.chat_id}, "
                f"message length: {len(content)}"
            )

        except Exception as e:
            logger.error(
                f"Error processing message from user {self.user.id}: {e}", exc_info=True
            )
            await self.send(
                text_data=json.dumps(
                    {"type": "error", "message": "Failed to process your message"}
                )
            )

    # --- Обработчики групповых сообщений ---

    async def user_message(self, event):
        """Обработчик для эхо-сообщений пользователя"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "user_message",
                    "message_id": event["message_id"],
                    "content": event["content"],
                    "user_id": event.get("user_id"),
                    "chat_id": event.get("chat_id"),
                    "timestamp": event.get("timestamp"),
                }
            )
        )

    async def ai_chunk(self, event):
        """Обработчик для чанков AI ответа"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "ai_chunk",
                    "chunk": event["chunk"],
                    "chat_id": event.get("chat_id"),
                }
            )
        )

    async def ai_complete(self, event):
        """Обработчик для сообщения о завершении генерации"""
        # Останавливаем отслеживание генерации
        AIResponseTracker.stop_generation(event.get("chat_id"))

        await self.send(
            text_data=json.dumps(
                {
                    "type": "ai_complete",
                    "message_id": event["message_id"],
                    "chat_id": event.get("chat_id"),
                    "error": event.get("error"),
                }
            )
        )

    async def connection_established(self, event):
        """Обработчик для сообщения об установке соединения (используется для broadcast)"""

    # --- Вспомогательные методы ---

    @database_sync_to_async
    def _check_chat_access(self):
        """Проверяет, имеет ли пользователь доступ к чату"""
        from chatbot.models import Chat

        try:
            return Chat.objects.filter(id=self.chat_id, owner=self.user).exists()
        except Exception as e:
            logger.error(f"Error checking chat access: {e}")
            return False

    @database_sync_to_async
    def _save_user_message(self, content):
        """Сохраняет сообщение пользователя в БД"""
        from chatbot.models import Chat, Message

        with transaction.atomic():
            # Блокируем запись чата для обновления
            chat = Chat.objects.select_for_update().get(id=self.chat_id)

            # Создаем сообщение
            message = Message.objects.create(
                chat=chat,
                sender=self.user,
                content=content,
                message_type="text",
            )

            # Обновляем время последней активности
            # chat.touch()

            return message

    # --- Методы для health check и управления ---

    @classmethod
    async def get_active_connections_count(cls, chat_id: str) -> int:
        """Возвращает количество активных соединений для чата"""
        from channels.layers import get_channel_layer

        channel_layer = get_channel_layer()

        # В реальности это сложнее, но для примера:
        # Нужно хранить информацию о соединениях
        return 0

    @classmethod
    async def broadcast_to_chat(cls, chat_id: str, message: dict):
        """Отправляет сообщение всем участникам чата"""
        from channels.layers import get_channel_layer

        channel_layer = get_channel_layer()

        await channel_layer.group_send(
            f"chat_{chat_id}", {"type": "broadcast_message", "message": message}
        )

    async def broadcast_message(self, event):
        """Обработчик для broadcast сообщений"""
        await self.send(
            text_data=json.dumps({"type": "broadcast", "message": event["message"]})
        )


# Декоратор для обработки ошибок в AI генерации
def handle_ai_errors(func):
    """Декоратор для обработки ошибок в AI функциях"""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"Unhandled error in AI function {func.__name__}: {e}", exc_info=True
            )
            raise

    return wrapper


# Утилита для graceful shutdown
def shutdown_ai_executor():
    """Корректное завершение работы AI executor"""
    logger.info("Shutting down AI executor...")
    _AI_EXECUTOR.shutdown(wait=True)
    logger.info("AI executor shutdown complete")
