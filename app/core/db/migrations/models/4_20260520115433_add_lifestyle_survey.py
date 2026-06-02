from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "lifestyle_surveys" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "surveyed_date" DATE NOT NULL,
    "smoking_status" VARCHAR(7) NOT NULL,
    "drinking_frequency" VARCHAR(12) NOT NULL,
    "exercise_days_per_week" INT NOT NULL,
    "sleep_hours_per_day" DOUBLE PRECISION,
    "daily_water_intake" DOUBLE PRECISION,
    "stress_level" VARCHAR(9),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "lifestyle_surveys"."surveyed_date" IS '설문 응답일';
COMMENT ON COLUMN "lifestyle_surveys"."smoking_status" IS '흡연 상태';
COMMENT ON COLUMN "lifestyle_surveys"."drinking_frequency" IS '음주 빈도';
COMMENT ON COLUMN "lifestyle_surveys"."exercise_days_per_week" IS '주당 운동 일수 (0~7)';
COMMENT ON COLUMN "lifestyle_surveys"."sleep_hours_per_day" IS '하루 평균 수면 시간 (시간)';
COMMENT ON COLUMN "lifestyle_surveys"."daily_water_intake" IS '하루 평균 수분 섭취량 (L)';
COMMENT ON COLUMN "lifestyle_surveys"."stress_level" IS '스트레스 수준';
        ALTER TABLE "health_checks" DROP COLUMN "drinking_frequency";
        ALTER TABLE "health_checks" DROP COLUMN "exercise_days_per_week";
        ALTER TABLE "health_checks" DROP COLUMN "smoking_status";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "health_checks" ADD "drinking_frequency" VARCHAR(12) NOT NULL;
        ALTER TABLE "health_checks" ADD "exercise_days_per_week" INT NOT NULL;
        ALTER TABLE "health_checks" ADD "smoking_status" VARCHAR(7) NOT NULL;
        COMMENT ON COLUMN "health_checks"."drinking_frequency" IS 'NEVER: NEVER\nOCCASIONALLY: OCCASIONALLY\nWEEKLY: WEEKLY\nDAILY: DAILY';
COMMENT ON COLUMN "health_checks"."exercise_days_per_week" IS '주당 운동 일수';
COMMENT ON COLUMN "health_checks"."smoking_status" IS 'NEVER: NEVER\nPAST: PAST\nCURRENT: CURRENT';
        DROP TABLE IF EXISTS "lifestyle_surveys";"""


MODELS_STATE = (
    "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"
)
