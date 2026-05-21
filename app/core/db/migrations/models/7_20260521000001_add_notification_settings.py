from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "notification_settings" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "challenge_joined_enabled" BOOL NOT NULL DEFAULT TRUE,
    "checkin_done_enabled" BOOL NOT NULL DEFAULT TRUE,
    "challenge_completed_enabled" BOOL NOT NULL DEFAULT TRUE,
    "challenge_reminder_enabled" BOOL NOT NULL DEFAULT TRUE,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" BIGINT NOT NULL UNIQUE REFERENCES "users" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "notification_settings";"""
