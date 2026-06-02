import zoneinfo
from dataclasses import field

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

    TIMEZONE: zoneinfo.ZoneInfo = field(default_factory=lambda: zoneinfo.ZoneInfo("Asia/Seoul"))

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    RAG_JOBS_STREAM: str = "rag_jobs"
    RAG_JOBS_GROUP: str = "rag_workers"
    RAG_RESP_PREFIX: str = "rag_resp"
