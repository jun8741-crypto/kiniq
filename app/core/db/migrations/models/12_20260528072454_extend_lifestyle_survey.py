from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "lifestyle_surveys" ADD "moderate_exercise_days" INT NOT NULL DEFAULT 0;
        ALTER TABLE "lifestyle_surveys" ADD "family_history_heart_disease" BOOL NOT NULL DEFAULT False;
        ALTER TABLE "lifestyle_surveys" ADD "moderate_exercise_minutes" INT NOT NULL DEFAULT 0;
        ALTER TABLE "lifestyle_surveys" ADD "vigorous_exercise_days" INT NOT NULL DEFAULT 0;
        ALTER TABLE "lifestyle_surveys" ADD "sitting_hours_per_day" DOUBLE PRECISION;
        ALTER TABLE "lifestyle_surveys" ADD "vigorous_exercise_minutes" INT NOT NULL DEFAULT 0;
        ALTER TABLE "lifestyle_surveys" ADD "marital_status" VARCHAR(8);
        ALTER TABLE "lifestyle_surveys" ADD "family_history_hypertension" BOOL NOT NULL DEFAULT False;
        ALTER TABLE "lifestyle_surveys" ADD "family_history_diabetes" BOOL NOT NULL DEFAULT False;
        COMMENT ON COLUMN "lifestyle_surveys"."moderate_exercise_days" IS '주당 중강도 신체활동 일수 (0~7)';
COMMENT ON COLUMN "lifestyle_surveys"."family_history_heart_disease" IS '가족력: 심장질환';
COMMENT ON COLUMN "lifestyle_surveys"."moderate_exercise_minutes" IS '중강도 활동 하루 평균 분';
COMMENT ON COLUMN "lifestyle_surveys"."vigorous_exercise_days" IS '주당 고강도 신체활동 일수 (0~7)';
COMMENT ON COLUMN "lifestyle_surveys"."sitting_hours_per_day" IS '하루 좌식 시간 (시간)';
COMMENT ON COLUMN "lifestyle_surveys"."vigorous_exercise_minutes" IS '고강도 활동 하루 평균 분';
COMMENT ON COLUMN "lifestyle_surveys"."marital_status" IS '결혼 여부';
COMMENT ON COLUMN "lifestyle_surveys"."family_history_hypertension" IS '가족력: 고혈압';
COMMENT ON COLUMN "lifestyle_surveys"."family_history_diabetes" IS '가족력: 당뇨';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "lifestyle_surveys" DROP COLUMN "moderate_exercise_days";
        ALTER TABLE "lifestyle_surveys" DROP COLUMN "family_history_heart_disease";
        ALTER TABLE "lifestyle_surveys" DROP COLUMN "moderate_exercise_minutes";
        ALTER TABLE "lifestyle_surveys" DROP COLUMN "vigorous_exercise_days";
        ALTER TABLE "lifestyle_surveys" DROP COLUMN "sitting_hours_per_day";
        ALTER TABLE "lifestyle_surveys" DROP COLUMN "vigorous_exercise_minutes";
        ALTER TABLE "lifestyle_surveys" DROP COLUMN "marital_status";
        ALTER TABLE "lifestyle_surveys" DROP COLUMN "family_history_hypertension";
        ALTER TABLE "lifestyle_surveys" DROP COLUMN "family_history_diabetes";"""


MODELS_STATE = (
    "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"
    "ttr8UWkjlTYS10Z+/D+l+kSH"
)
