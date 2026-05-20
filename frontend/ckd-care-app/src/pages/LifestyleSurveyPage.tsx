import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ScreenLabel } from "../components/ScreenLabel";
import { TopNav } from "../components/TopNav";
import { BtnPrimary } from "../components/BtnPrimary";
import { lifestyleSurveyApi, type SmokingStatus, type DrinkingFrequency, type StressLevel } from "../api/lifestyleSurvey";

function SelectGroup<T extends string>({
  label, options, value, onChange,
}: {
  label: string;
  options: { value: T; label: string }[];
  value: T | "";
  onChange: (v: T) => void;
}) {
  return (
    <div className="flex flex-col gap-[4px]">
      <label className="text-sm font-normal text-text-secondary">{label}</label>
      <div className="flex gap-[8px]">
        {options.map((o) => (
          <button
            key={o.value}
            onClick={() => onChange(o.value)}
            className={`flex-1 rounded-sm border px-[12px] py-[8px] text-sm ${
              value === o.value
                ? "border-accent bg-accent font-bold text-bg"
                : "border-border-strong bg-bg font-normal text-text-primary"
            }`}
          >
            {o.label}
          </button>
        ))}
      </div>
    </div>
  );
}

function StepperInput({ label, value, onChange, min = 0, max = 7 }: {
  label: string; value: number; onChange: (v: number) => void; min?: number; max?: number;
}) {
  return (
    <div className="flex flex-col gap-[4px]">
      <label className="text-sm font-normal text-text-secondary">{label}</label>
      <div className="flex items-center gap-[12px]">
        <button
          onClick={() => onChange(Math.max(min, value - 1))}
          className="flex h-[36px] w-[36px] items-center justify-center rounded-sm border border-border-strong bg-bg text-lg"
        >−</button>
        <span className="w-[40px] text-center text-lg font-bold text-text-primary">{value}</span>
        <button
          onClick={() => onChange(Math.min(max, value + 1))}
          className="flex h-[36px] w-[36px] items-center justify-center rounded-sm border border-border-strong bg-bg text-lg"
        >+</button>
      </div>
    </div>
  );
}

export function LifestyleSurveyPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [smoking, setSmoking] = useState<SmokingStatus | "">("");
  const [drinking, setDrinking] = useState<DrinkingFrequency | "">("");
  const [stress, setStress] = useState<StressLevel | "">("");
  const [exerciseDays, setExerciseDays] = useState(0);
  const [sleepHours, setSleepHours] = useState(7);
  const [waterIntake, setWaterIntake] = useState(1.5);

  async function handleSubmit() {
    if (!smoking || !drinking) {
      setError("흡연 상태와 음주 빈도는 필수 항목입니다."); return;
    }
    setError("");
    setLoading(true);
    try {
      await lifestyleSurveyApi.create({
        surveyed_date: new Date().toISOString().slice(0, 10),
        smoking_status: smoking,
        drinking_frequency: drinking,
        exercise_days_per_week: exerciseDays,
        sleep_hours_per_day: sleepHours,
        daily_water_intake: waterIntake,
        stress_level: stress || null,
      });
      navigate("/dashboard");
    } catch (e) {
      setError(e instanceof Error ? e.message : "저장에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-bg-alt">
      <ScreenLabel label="08 · 생활습관 설문 (REQ-DATA-04)" />
      <TopNav />
      <main className="flex flex-1 flex-col p-[32px]">
        <h1 className="text-2xl font-bold text-text-primary">생활습관 설문</h1>
        <p className="mt-[4px] text-sm text-text-secondary">오늘 기준 생활습관을 솔직하게 입력해주세요.</p>

        {error && (
          <div className="mt-4 rounded-sm bg-danger/10 px-3 py-2 text-sm text-danger">{error}</div>
        )}

        <div className="mt-[24px] grid grid-cols-2 gap-[32px]">
          {/* 좌측 */}
          <div className="flex flex-col gap-[24px]">
            <div className="rounded-md border border-border bg-bg p-[16px]">
              <p className="mb-[12px] text-md font-bold text-text-primary">
                흡연·음주 <span className="text-danger text-xs">* 필수</span>
              </p>
              <div className="flex flex-col gap-[16px]">
                <SelectGroup<SmokingStatus>
                  label="흡연 상태"
                  value={smoking}
                  onChange={setSmoking}
                  options={[
                    { value: "NEVER", label: "비흡연" },
                    { value: "PAST", label: "과거 흡연" },
                    { value: "CURRENT", label: "현재 흡연" },
                  ]}
                />
                <SelectGroup<DrinkingFrequency>
                  label="음주 빈도"
                  value={drinking}
                  onChange={setDrinking}
                  options={[
                    { value: "NEVER", label: "안 마심" },
                    { value: "OCCASIONALLY", label: "가끔" },
                    { value: "WEEKLY", label: "주 1~2회" },
                    { value: "DAILY", label: "매일" },
                  ]}
                />
              </div>
            </div>

            <div className="rounded-md border border-border bg-bg p-[16px]">
              <p className="mb-[12px] text-md font-bold text-text-primary">스트레스</p>
              <SelectGroup<StressLevel>
                label="스트레스 수준"
                value={stress}
                onChange={setStress}
                options={[
                  { value: "VERY_LOW", label: "매우 낮음" },
                  { value: "LOW", label: "낮음" },
                  { value: "MODERATE", label: "보통" },
                  { value: "HIGH", label: "높음" },
                  { value: "VERY_HIGH", label: "매우 높음" },
                ]}
              />
            </div>
          </div>

          {/* 우측 */}
          <div className="flex flex-col gap-[24px]">
            <div className="rounded-md border border-border bg-bg p-[16px]">
              <p className="mb-[12px] text-md font-bold text-text-primary">신체활동</p>
              <StepperInput
                label="주간 운동 일수 (일)"
                value={exerciseDays}
                onChange={setExerciseDays}
                min={0} max={7}
              />
            </div>

            <div className="rounded-md border border-border bg-bg p-[16px]">
              <p className="mb-[12px] text-md font-bold text-text-primary">수면·수분</p>
              <div className="flex flex-col gap-[16px]">
                <StepperInput
                  label={`하루 평균 수면 (${sleepHours}시간)`}
                  value={sleepHours}
                  onChange={setSleepHours}
                  min={0} max={24}
                />
                <div className="flex flex-col gap-[4px]">
                  <label className="text-sm font-normal text-text-secondary">
                    하루 수분 섭취량 ({waterIntake.toFixed(1)}L)
                  </label>
                  <input
                    type="range"
                    min={0} max={5} step={0.5}
                    value={waterIntake}
                    onChange={(e) => setWaterIntake(parseFloat(e.target.value))}
                    className="w-full accent-accent"
                  />
                  <div className="flex justify-between text-xs text-text-muted">
                    <span>0L</span><span>2.5L</span><span>5L</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-[32px] flex justify-end">
          <BtnPrimary label="설문 완료" loading={loading} onClick={handleSubmit} />
        </div>
      </main>
    </div>
  );
}
