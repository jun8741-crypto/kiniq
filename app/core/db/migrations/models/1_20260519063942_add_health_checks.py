from tortoise import BaseDBAsyncClient

RUN_IN_TRANSACTION = True


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "health_checks" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "checked_date" DATE NOT NULL,
    "systolic_bp" INT NOT NULL,
    "diastolic_bp" INT NOT NULL,
    "fasting_glucose" DOUBLE PRECISION NOT NULL,
    "creatinine" DOUBLE PRECISION,
    "total_cholesterol" DOUBLE PRECISION,
    "hdl_cholesterol" DOUBLE PRECISION,
    "triglycerides" DOUBLE PRECISION,
    "weight" DOUBLE PRECISION NOT NULL,
    "height" DOUBLE PRECISION NOT NULL,
    "bmi" DOUBLE PRECISION NOT NULL,
    "waist_circumference" DOUBLE PRECISION,
    "smoking_status" VARCHAR(7) NOT NULL,
    "drinking_frequency" VARCHAR(12) NOT NULL,
    "exercise_days_per_week" INT NOT NULL,
    "egfr_estimated" DOUBLE PRECISION,
    "ckd_risk_score" DOUBLE PRECISION,
    "ckd_stage" VARCHAR(3),
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "user_id" BIGINT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE
);
COMMENT ON COLUMN "health_checks"."checked_date" IS '검진일';
COMMENT ON COLUMN "health_checks"."systolic_bp" IS '수축기혈압';
COMMENT ON COLUMN "health_checks"."diastolic_bp" IS '이완기혈압';
COMMENT ON COLUMN "health_checks"."fasting_glucose" IS '공복혈당 mg/dL';
COMMENT ON COLUMN "health_checks"."creatinine" IS '혈청 크레아티닌 mg/dL';
COMMENT ON COLUMN "health_checks"."total_cholesterol" IS '총 콜레스테롤 mg/dL';
COMMENT ON COLUMN "health_checks"."hdl_cholesterol" IS 'HDL 콜레스테롤 mg/dL';
COMMENT ON COLUMN "health_checks"."triglycerides" IS '중성지방 mg/dL';
COMMENT ON COLUMN "health_checks"."weight" IS '체중 kg';
COMMENT ON COLUMN "health_checks"."height" IS '신장 cm';
COMMENT ON COLUMN "health_checks"."bmi" IS '체질량지수 (서비스에서 자동 계산)';
COMMENT ON COLUMN "health_checks"."waist_circumference" IS '허리둘레 cm';
COMMENT ON COLUMN "health_checks"."smoking_status" IS 'NEVER: NEVER\nPAST: PAST\nCURRENT: CURRENT';
COMMENT ON COLUMN "health_checks"."drinking_frequency" IS 'NEVER: NEVER\nOCCASIONALLY: OCCASIONALLY\nWEEKLY: WEEKLY\nDAILY: DAILY';
COMMENT ON COLUMN "health_checks"."exercise_days_per_week" IS '주당 운동 일수';
COMMENT ON COLUMN "health_checks"."egfr_estimated" IS '추정 eGFR mL/min/1.73m²';
COMMENT ON COLUMN "health_checks"."ckd_risk_score" IS 'ML 모델 CKD 위험도 0.0~1.0';
COMMENT ON COLUMN "health_checks"."ckd_stage" IS 'G1: G1\nG2: G2\nG3A: G3A\nG3B: G3B\nG4: G4\nG5: G5';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "health_checks";"""


MODELS_STATE = (
    "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"
)
