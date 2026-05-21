from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "diet_surveys" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "surveyed_date" DATE NOT NULL,
    "soup_stew_per_day" INT NOT NULL,
    "sweet_drink_per_day" INT NOT NULL,
    "fried_food_per_week" INT NOT NULL,
    "vegetables_every_meal" BOOL NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "diet_surveys"."surveyed_date" IS '설문 응답일';
COMMENT ON COLUMN "diet_surveys"."soup_stew_per_day" IS '하루 국/찌개 섭취 횟수';
COMMENT ON COLUMN "diet_surveys"."sweet_drink_per_day" IS '하루 단 음료 섭취 횟수';
COMMENT ON COLUMN "diet_surveys"."fried_food_per_week" IS '주당 튀김/볶음 섭취 횟수';
COMMENT ON COLUMN "diet_surveys"."vegetables_every_meal" IS '매 식사 채소 섭취 여부';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "diet_surveys";"""
