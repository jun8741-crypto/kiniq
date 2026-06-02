import pytest
from app.core.redis_client import get_redis, build_redis_url


def test_build_redis_url():
    assert build_redis_url("localhost", 6379) == "redis://localhost:6379"


@pytest.mark.asyncio
async def test_get_redis_returns_singleton():
    a = get_redis()
    b = get_redis()
    assert a is b
