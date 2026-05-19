from enum import StrEnum

from tortoise import fields, models


class SmokingStatus(StrEnum):
    NEVER = "NEVER"  # 비흡연
    PAST = "PAST"  # 과거 흡연 (현재 금연 중)
    CURRENT = "CURRENT"  # 현재 흡연


class DrinkingFrequency(StrEnum):
    NEVER = "NEVER"  # 음주 안 함
    OCCASIONALLY = "OCCASIONALLY"  # 월 1~3회
    WEEKLY = "WEEKLY"  # 주 1~4회
    DAILY = "DAILY"  # 거의 매일


class CkdStage(StrEnum):
    G1 = "G1"  # eGFR >= 90  (정상 or 고위험 경계)
    G2 = "G2"  # eGFR 60~89  (경증 감소)
    G3A = "G3A"  # eGFR 45~59  (경~중등도)
    G3B = "G3B"  # eGFR 30~44  (중~중증도)
    G4 = "G4"  # eGFR 15~29  (중증)
    G5 = "G5"  # eGFR < 15   (신부전)


class HealthCheck(models.Model):
    id = fields.BigIntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="health_checks")
    checked_date = fields.DateField(description="검진일")

    # 혈압 (mmHg)
    systolic_bp = fields.IntField(description="수축기혈압")
    diastolic_bp = fields.IntField(description="이완기혈압")

    # 혈액 검사
    fasting_glucose = fields.FloatField(description="공복혈당 mg/dL")
    creatinine = fields.FloatField(null=True, description="혈청 크레아티닌 mg/dL")
    total_cholesterol = fields.FloatField(null=True, description="총 콜레스테롤 mg/dL")
    hdl_cholesterol = fields.FloatField(null=True, description="HDL 콜레스테롤 mg/dL")
    triglycerides = fields.FloatField(null=True, description="중성지방 mg/dL")

    # 신체 측정
    weight = fields.FloatField(description="체중 kg")
    height = fields.FloatField(description="신장 cm")
    bmi = fields.FloatField(description="체질량지수 (서비스에서 자동 계산)")
    waist_circumference = fields.FloatField(null=True, description="허리둘레 cm")

    # 생활습관 설문
    smoking_status = fields.CharEnumField(enum_type=SmokingStatus)
    drinking_frequency = fields.CharEnumField(enum_type=DrinkingFrequency)
    exercise_days_per_week = fields.IntField(description="주당 운동 일수")

    # AI / CKD-EPI 예측 결과 — ai_worker 또는 서비스가 비동기로 채움
    egfr_estimated = fields.FloatField(null=True, description="추정 eGFR mL/min/1.73m²")
    ckd_risk_score = fields.FloatField(null=True, description="ML 모델 CKD 위험도 0.0~1.0")
    ckd_stage = fields.CharEnumField(enum_type=CkdStage, null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "health_checks"
        ordering = ["-checked_date"]
