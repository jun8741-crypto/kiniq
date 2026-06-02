from app.models.chat import ChatMessage, ChatRole


class ChatRepository:
    async def add(self, *, user_id: int, role: ChatRole, content: str) -> ChatMessage:
        return await ChatMessage.create(user_id=user_id, role=role, content=content)

    async def get_by_user(self, user_id: int, limit: int = 20, offset: int = 0) -> tuple[int, list[ChatMessage]]:
        qs = ChatMessage.filter(user_id=user_id)
        total = await qs.count()
        items = await qs.order_by("created_at").offset(offset).limit(limit)
        return total, items
