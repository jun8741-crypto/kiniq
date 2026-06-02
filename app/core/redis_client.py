"""RAG 챗봇용 Redis 비동기 클라이언트 (단일 커넥션 풀)."""
from __future__ import annotations

import redis.asyncio as aioredis

from app.core import config

_client: aioredis.Redis | None = None


def build_redis_url(host: str, port: int) -> str:
    return f"redis://{host}:{port}"


def get_redis() -> aioredis.Redis:
    global _client
    if _client is None:
        _client = aioredis.from_url(
            build_redis_url(config.REDIS_HOST, config.REDIS_PORT),
            decode_responses=True,
        )
    return _client
