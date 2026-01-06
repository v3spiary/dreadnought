# chatbot/tasks.py
import logging

logger = logging.getLogger(__name__)

# @shared_task(bind=True)
# def generate_ai_response(self, chat_id: str, prompt: str):
#     try:
#         from chatbot.models import Message, Chat

#         logger.info(f"[Celery] Start AI for chat {chat_id}, prompt: {prompt[:50]}...")

#         try:
#             chat_uuid = UUID(chat_id)
#         except ValueError:
#             logger.error(f"Invalid chat_id format: {chat_id}")
#             return

#         channel_layer = get_channel_layer()
#         group_name = f"chat_{chat_id}"
#         full_response = ""

#         req = urllib.request.Request(
#             "http://ollama:11434/api/generate",
#             data=json.dumps({
#                 "model": "qwen2.5:7b-instruct",
#                 "prompt": f"Ты AI-психолог HisMind. Общайся ТОЛЬКО на русском. ... {prompt}",
#                 "stream": True
#             }).encode(),
#             headers={"Content-Type": "application/json"},
#             method="POST",
#         )

#         with urllib.request.urlopen(req) as resp:
#             for line in resp:
#                 line = line.strip()
#                 if not line:
#                     continue
#                 data = json.loads(line.decode())
#                 token = data.get("response", "")
#                 if not token:
#                     continue

#                 full_response += token
#                 async_to_sync(channel_layer.group_send)(
#                     group_name,
#                     {"type": "ai_chunk", "chunk": token},
#                 )
#                 if data.get("done"):
#                     break

#         ai_msg = Message.objects.create(
#             chat_id=chat_id,  # ← ЯВНО
#             content=full_response,
#             message_type="text",
#             sender=None,
#         )

#         async_to_sync(channel_layer.group_send)(
#             group_name,
#             {"type": "ai_complete", "message_id": str(ai_msg.id)},
#         )

#         # # СОХРАНЯЕМ В БД
#         # ai_msg = Message.objects.create(
#         #     chat_id=chat_id,
#         #     content=full_response,
#         #     message_type="text",
#         #     sender=None,
#         # )
#         # logger.info(f"[Celery] AI message saved: {ai_msg.id}")

#         # # ОТПРАВЛЯЕМ ai_complete
#         # async_to_sync(channel_layer.group_send)(
#         #     group_name,
#         #     {"type": "ai_complete", "message_id": str(ai_msg.id)},
#         # )
#         # logger.info(f"[Celery] ai_complete sent for {ai_msg.id}")

#     except Exception as e:
#         logger.error(f"[Celery] ERROR in generate_ai_response: {e}", exc_info=True)
