from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "challenges" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(100) NOT NULL,
    "category" VARCHAR(9) NOT NULL,
    "description" TEXT NOT NULL,
    "duration_days" INT NOT NULL,
    "track" VARCHAR(1) NOT NULL,
    "is_active" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON COLUMN "challenges"."category" IS 'HYDRATION: HYDRATION\nEXERCISE: EXERCISE\nDIET: DIET\nSLEEP: SLEEP\nSMOKING: SMOKING';
COMMENT ON COLUMN "challenges"."duration_days" IS '챌린지 총 기간 (일)';
COMMENT ON COLUMN "challenges"."track" IS 'A: A\nB: B';
        CREATE TABLE IF NOT EXISTS "user_challenges" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "started_at" DATE NOT NULL,
    "status" VARCHAR(9) NOT NULL DEFAULT 'ACTIVE',
    "streak_count" INT NOT NULL DEFAULT 0,
    "total_checkins" INT NOT NULL DEFAULT 0,
    "last_checkin_date" DATE,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "challenge_id" BIGINT NOT NULL REFERENCES "challenges" ("id") ON DELETE CASCADE,
    "user_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_user_challe_user_id_05b55e" UNIQUE ("user_id", "challenge_id")
);
COMMENT ON COLUMN "user_challenges"."started_at" IS '챌린지 시작일';
COMMENT ON COLUMN "user_challenges"."status" IS 'ACTIVE: ACTIVE\nCOMPLETED: COMPLETED\nABANDONED: ABANDONED';
COMMENT ON COLUMN "user_challenges"."streak_count" IS '연속 체크인 일수';
COMMENT ON COLUMN "user_challenges"."total_checkins" IS '누적 체크인 횟수';
COMMENT ON COLUMN "user_challenges"."last_checkin_date" IS '마지막 체크인 날짜';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "challenges";
        DROP TABLE IF EXISTS "user_challenges";"""


MODELS_STATE = (
    "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"
    "4xe3cecvTnj9H99SOgU="
)
