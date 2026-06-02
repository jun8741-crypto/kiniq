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
COMMENT ON COLUMN "diet_surveys"."soup_stew_per_day" IS '하루 국·찌개·탕류 섭취 횟수';
COMMENT ON COLUMN "diet_surveys"."sweet_drink_per_day" IS '하루 단 음료 잔 수';
COMMENT ON COLUMN "diet_surveys"."fried_food_per_week" IS '주 튀긴 음식 섭취 횟수';
COMMENT ON COLUMN "diet_surveys"."vegetables_every_meal" IS '매 끼 채소 반찬 섭취 여부';
        CREATE TABLE IF NOT EXISTS "notification_settings" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "challenge_joined_enabled" BOOL NOT NULL DEFAULT True,
    "checkin_done_enabled" BOOL NOT NULL DEFAULT True,
    "challenge_completed_enabled" BOOL NOT NULL DEFAULT True,
    "challenge_reminder_enabled" BOOL NOT NULL DEFAULT True,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" BIGINT NOT NULL UNIQUE REFERENCES "users" ("id") ON DELETE CASCADE
);
        CREATE TABLE IF NOT EXISTS "point_transactions" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "amount" INT NOT NULL,
    "reason" VARCHAR(18) NOT NULL,
    "extra" JSONB NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "point_transactions"."amount" IS '+적립 / -소비';
COMMENT ON COLUMN "point_transactions"."reason" IS 'LOGIN: LOGIN\nCHECKIN: CHECKIN\nLUCKY: LUCKY\nSTREAK_BONUS: STREAK_BONUS\nSTAGE_BONUS: STAGE_BONUS\nFULL_PARTICIPATION: FULL_PARTICIPATION\nPURCHASE: PURCHASE\nPROTECT_CONSUME: PROTECT_CONSUME\nREFUND: REFUND';
COMMENT ON COLUMN "point_transactions"."extra" IS '컨텍스트: challenge_id, stage_no, streak_day, item_code 등';
        CREATE TABLE IF NOT EXISTS "user_charge_mode" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "is_active" BOOL NOT NULL DEFAULT False,
    "entered_at" TIMESTAMPTZ,
    "exited_at" TIMESTAMPTZ,
    "warning_4d_alerted" BOOL NOT NULL DEFAULT False,
    "warning_5d_alerted" BOOL NOT NULL DEFAULT False,
    "warning_6d_alerted" BOOL NOT NULL DEFAULT False,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
        CREATE TABLE IF NOT EXISTS "user_daily_logins" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "login_date" DATE NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_user_daily__user_id_659c4f" UNIQUE ("user_id", "login_date")
);
COMMENT ON TABLE "user_daily_logins" IS '일일 로그인 보상 중복 지급 방지용 — 사용자 × 날짜 1개 row.';
        CREATE TABLE IF NOT EXISTS "user_eggs" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "egg_no" INT NOT NULL,
    "progress_checkins" INT NOT NULL DEFAULT 0,
    "current_stage" INT NOT NULL DEFAULT 1,
    "is_legendary" BOOL,
    "goal_70_alerted" BOOL NOT NULL DEFAULT False,
    "goal_90_alerted" BOOL NOT NULL DEFAULT False,
    "stage_25_bonus_paid" BOOL NOT NULL DEFAULT False,
    "stage_50_bonus_paid" BOOL NOT NULL DEFAULT False,
    "stage_75_bonus_paid" BOOL NOT NULL DEFAULT False,
    "stage_100_bonus_paid" BOOL NOT NULL DEFAULT False,
    "started_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "hatched_at" TIMESTAMPTZ,
    "user_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_user_eggs_user_id_d7250d" UNIQUE ("user_id", "egg_no")
);
COMMENT ON COLUMN "user_eggs"."egg_no" IS '사용자 기준 몇 번째 알 (1부터 시작)';
COMMENT ON COLUMN "user_eggs"."progress_checkins" IS '누적 체크인 수 (0~100)';
COMMENT ON COLUMN "user_eggs"."current_stage" IS '1=0~25%, 2=25~50%, 3=50~75%, 4=75~100%, 5=부화';
COMMENT ON COLUMN "user_eggs"."is_legendary" IS '부화 시 5% 추첨 결과. 진행 중엔 NULL';
COMMENT ON COLUMN "user_eggs"."hatched_at" IS '부화 시각. NULL이면 진행 중';
        CREATE TABLE IF NOT EXISTS "user_inventory" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "item_code" VARCHAR(13) NOT NULL,
    "quantity" INT NOT NULL DEFAULT 0,
    "acquired_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_user_invent_user_id_3c9c50" UNIQUE ("user_id", "item_code")
);
COMMENT ON COLUMN "user_inventory"."item_code" IS 'PROTECT: PROTECT\nMINI_BOOSTER: MINI_BOOSTER\nSKIN_S_BLUE: SKIN_S_BLUE\nSKIN_S_GREEN: SKIN_S_GREEN\nSKIN_M_RED: SKIN_M_RED\nSKIN_M_PURPLE: SKIN_M_PURPLE\nSKIN_L_GOLD: SKIN_L_GOLD';
COMMENT ON COLUMN "user_inventory"."quantity" IS '보호권은 0~2, 부스터/스킨은 0~∞';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "user_charge_mode";
        DROP TABLE IF EXISTS "user_eggs";
        DROP TABLE IF EXISTS "diet_surveys";
        DROP TABLE IF EXISTS "point_transactions";
        DROP TABLE IF EXISTS "user_inventory";
        DROP TABLE IF EXISTS "user_daily_logins";
        DROP TABLE IF EXISTS "notification_settings";"""


MODELS_STATE = (
    "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"
    "V9JIJY3EpZHv/w+l7cO5"
)
