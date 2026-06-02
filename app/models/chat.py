from enum import StrEnum

from tortoise import fields, models


class ChatRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(models.Model):
    id = fields.BigIntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="chat_messages")
    role = fields.CharEnumField(enum_type=ChatRole, description="발화 주체 (user/assistant)")
    content = fields.TextField(description="질문 또는 답변 본문")
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "chat_messages"
        ordering = ["created_at"]
