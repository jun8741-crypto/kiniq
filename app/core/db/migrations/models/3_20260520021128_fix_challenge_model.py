from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "health_checks" ADD "app_group" VARCHAR(2);
        ALTER TABLE "challenges" ADD "stage" INT NOT NULL DEFAULT 1;
        COMMENT ON COLUMN "challenges"."category" IS 'HYDRATION: HYDRATION
EXERCISE: EXERCISE
DIET: DIET
SLEEP: SLEEP
STRESS: STRESS';
        COMMENT ON COLUMN "health_checks"."app_group" IS 'ML 모델 배정 그룹 (REQ-ML-003)';
COMMENT ON COLUMN "challenges"."stage" IS '난이도 단계 1=입문 2=초보 3=중급 4=숙련';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "health_checks" DROP COLUMN "app_group";
        ALTER TABLE "challenges" DROP COLUMN "stage";
        COMMENT ON COLUMN "challenges"."category" IS 'HYDRATION: HYDRATION
EXERCISE: EXERCISE
DIET: DIET
SLEEP: SLEEP
SMOKING: SMOKING';"""


MODELS_STATE = (
    "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"
)
