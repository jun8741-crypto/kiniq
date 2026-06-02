"""ChatRepository PostgreSQL 통합 테스트.

tortoise.contrib.test.TestCase 패턴을 사용한다 (기존 테스트 코드 일관성 유지).
"""

from datetime import date

from tortoise.contrib.test import TestCase

from app.models.chat import ChatRole
from app.models.users import User
from app.repositories.chat_repository import ChatRepository


async def _make_user(email: str = "chat_repo_test@example.com") -> User:
    return await User.create(
        email=email,
        hashed_password="$2b$12$dummy",
        name="채팅테스터",
        gender="MALE",
        birthday=date(1990, 1, 1),
        phone_number="01099990001",
    )


class TestChatRepository(TestCase):
    async def test_add_and_get_by_user(self):
        """add 2건 저장 후 get_by_user → total==2, created_at 오름차순 검증."""
        user = await _make_user()
        repo = ChatRepository()

        await repo.add(user_id=user.id, role=ChatRole.USER, content="질문")
        await repo.add(user_id=user.id, role=ChatRole.ASSISTANT, content="답변")

        total, items = await repo.get_by_user(user.id)

        assert total == 2
        assert items[0].content == "질문"
        assert items[0].role == ChatRole.USER
        assert items[1].content == "답변"
        assert items[1].role == ChatRole.ASSISTANT
        # created_at 오름차순 확인
        assert items[0].created_at <= items[1].created_at

    async def test_get_by_user_empty(self):
        """메시지가 없는 사용자 → total==0, items==[]."""
        user = await _make_user(email="chat_empty@example.com")
        repo = ChatRepository()

        total, items = await repo.get_by_user(user.id)

        assert total == 0
        assert items == []

    async def test_get_by_user_pagination(self):
        """limit/offset 페이지네이션 동작 검증."""
        user = await _make_user(email="chat_page@example.com")
        repo = ChatRepository()

        # 3건 삽입
        for i in range(3):
            await repo.add(user_id=user.id, role=ChatRole.USER, content=f"질문{i}")

        total, items = await repo.get_by_user(user.id, limit=2, offset=0)
        assert total == 3
        assert len(items) == 2

        total2, items2 = await repo.get_by_user(user.id, limit=2, offset=2)
        assert total2 == 3
        assert len(items2) == 1
