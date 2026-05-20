import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ScreenLabel } from "../components/ScreenLabel";
import { TopNav } from "../components/TopNav";
import { Tag } from "../components/Tag";
import { Card } from "../components/Card";
import { dashboardApi, type DashboardSummary, type EgfrTrend } from "../api/dashboard";
import { useAuth } from "../contexts/AuthContext";

function EgfrGauge({ value }: { value: number | null }) {
  if (value === null) return <div className="flex h-[200px] items-center justify-center text-sm text-text-muted">데이터 없음</div>;
  const max = 120;
  const pct = Math.min(value / max, 1);
  const color = value >= 60 ? "#059669" : value >= 30 ? "#D97706" : "#DC2626";
  const angle = -135 + pct * 270;
  const cx = 80, cy = 90, r = 60;
  const toRad = (deg: number) => (deg * Math.PI) / 180;
  const startAngle = -135, endAngle = -135 + pct * 270;
  const x1 = cx + r * Math.cos(toRad(startAngle));
  const y1 = cy + r * Math.sin(toRad(startAngle));
  const x2 = cx + r * Math.cos(toRad(endAngle));
  const y2 = cy + r * Math.sin(toRad(endAngle));
  const largeArc = pct * 270 > 180 ? 1 : 0;
  return (
    <div className="flex flex-col items-center justify-center gap-2 p-4 rounded-md border border-border bg-bg" style={{ height: 200 }}>
      <svg width="160" height="120" viewBox="0 0 160 120">
        <path d={`M ${cx + r * Math.cos(toRad(-135))} ${cy + r * Math.sin(toRad(-135))} A ${r} ${r} 0 1 1 ${cx + r * Math.cos(toRad(135))} ${cy + r * Math.sin(toRad(135))}`}
          fill="none" stroke="#E5E7EB" strokeWidth="10" strokeLinecap="round" />
        {pct > 0 && (
          <path d={`M ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2}`}
            fill="none" stroke={color} strokeWidth="10" strokeLinecap="round" />
        )}
        <text x={cx} y={cy - 4} textAnchor="middle" fontSize="20" fontWeight="bold" fill={color}>{Math.round(value)}</text>
        <text x={cx} y={cy + 14} textAnchor="middle" fontSize="10" fill="#6B7280">mL/min</text>
        <line x1={cx} y1={cy} x2={cx + (r - 10) * Math.cos(toRad(angle))} y2={cy + (r - 10) * Math.sin(toRad(angle))}
          stroke="#1F2937" strokeWidth="2" strokeLinecap="round" />
      </svg>
      <p className="text-xs font-bold text-text-primary">eGFR 계기판</p>
    </div>
  );
}

function RiskGauge({ score }: { score: number | null }) {
  if (score === null) return <div className="flex h-[200px] items-center justify-center text-sm text-text-muted">데이터 없음</div>;
  const color = score < 30 ? "#059669" : score < 60 ? "#D97706" : "#DC2626";
  return (
    <div className="flex flex-col items-center justify-center gap-2 p-4 rounded-md border border-border bg-bg" style={{ height: 200 }}>
      <div className="relative flex h-[80px] w-[80px] items-center justify-center rounded-full border-8" style={{ borderColor: color }}>
        <span className="text-xl font-bold" style={{ color }}>{Math.round(score)}%</span>
      </div>
      <p className="text-xs font-bold text-text-primary">CKD 위험도</p>
      <p className="text-xs text-text-secondary">{score < 30 ? "낮음" : score < 60 ? "중간" : "높음"}</p>
    </div>
  );
}

function EgfrTrendChart({ trend }: { trend: EgfrTrend | null }) {
  if (!trend || trend.data_points.length === 0) {
    return (
      <div className="flex h-[240px] items-center justify-center rounded-md border border-border bg-bg text-sm text-text-muted">
        eGFR 검진 데이터가 없습니다
      </div>
    );
  }
  const pts = trend.data_points;
  const W = 600, H = 180, PAD = 40;
  const vals = pts.map((p) => p.egfr_estimated);
  const minV = Math.min(...vals) - 5;
  const maxV = Math.max(...vals) + 5;
  const toX = (i: number) => PAD + (i / (pts.length - 1 || 1)) * (W - PAD * 2);
  const toY = (v: number) => H - PAD - ((v - minV) / (maxV - minV || 1)) * (H - PAD * 2);
  const polyline = pts.map((p, i) => `${toX(i)},${toY(p.egfr_estimated)}`).join(" ");

  return (
    <div className="rounded-md border border-border bg-bg p-4">
      <p className="mb-2 text-sm font-bold text-text-primary">eGFR 추세 차트</p>
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full" style={{ height: 200 }}>
        {[30, 60, 90].map((line) => (
          <g key={line}>
            <line x1={PAD} y1={toY(line)} x2={W - PAD} y2={toY(line)} stroke="#E5E7EB" strokeDasharray="4 4" />
            <text x={PAD - 4} y={toY(line) + 4} textAnchor="end" fontSize="10" fill="#9CA3AF">{line}</text>
          </g>
        ))}
        <polyline points={polyline} fill="none" stroke="#2563EB" strokeWidth="2" strokeLinejoin="round" />
        {pts.map((p, i) => (
          <g key={i}>
            <circle cx={toX(i)} cy={toY(p.egfr_estimated)} r="4" fill="#2563EB" />
            <text x={toX(i)} y={H - 8} textAnchor="middle" fontSize="9" fill="#9CA3AF">
              {p.checked_date.slice(5)}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
}

const CKD_STAGE_LABEL: Record<string, string> = {
  G1: "G1 · 정상", G2: "G2 · 경계군", G3a: "G3a · 경증", G3b: "G3b · 중등도",
  G4: "G4 · 중증", G5: "G5 · 신부전",
};

const LIFESTYLE_LABEL: Record<string, string> = {
  NEVER: "비흡연", PAST: "과거 흡연", CURRENT: "현재 흡연",
  NONE: "안 마심", MONTHLY: "월 1~4회", WEEKLY: "주 2회+",
  LOW: "낮음", MODERATE: "보통", HIGH: "높음",
};

export function DashboardPage() {
  const { user } = useAuth();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [trend, setTrend] = useState<EgfrTrend | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([dashboardApi.getSummary(), dashboardApi.getEgfrTrend()])
      .then(([s, t]) => { setSummary(s); setTrend(t); })
      .catch((e) => setError(e instanceof Error ? e.message : "데이터를 불러오지 못했습니다."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="flex min-h-screen flex-col bg-bg-alt">
      <ScreenLabel label="10 · 대시보드 (REQ-DASH-01)" />
      <TopNav />
      <main className="flex flex-1 items-center justify-center text-text-secondary">데이터 로딩 중...</main>
    </div>
  );

  const h = summary?.latest_health;
  const cs = summary?.challenge_stats;
  const ls = summary?.latest_lifestyle;

  return (
    <div className="flex min-h-screen flex-col bg-bg-alt">
      <ScreenLabel label="10 · 대시보드 (REQ-DASH-01)" />
      <TopNav />
      <main className="flex flex-1 flex-col p-[32px]">

        {error && (
          <div className="mb-4 rounded-sm bg-danger/10 px-3 py-2 text-sm text-danger">{error}</div>
        )}

        {/* 헤더 */}
        <div className="flex items-center gap-[12px]">
          <h1 className="text-2xl font-bold text-text-primary">
            안녕하세요, {user?.name ?? "—"} 님
          </h1>
          {h?.ckd_stage && <Tag label={CKD_STAGE_LABEL[h.ckd_stage] ?? h.ckd_stage} />}
        </div>

        {/* Row1: 계기판 + 헬스 알 */}
        <div className="mt-[24px] flex gap-[24px]">
          <div className="flex flex-1 gap-[16px]">
            <div className="flex-1">
              <EgfrGauge value={h?.egfr_estimated ?? null} />
            </div>
            <div className="flex-1">
              <RiskGauge score={h?.ckd_risk_score ? h.ckd_risk_score * 100 : null} />
            </div>
          </div>
          <div className="flex w-[280px] flex-col items-center justify-center gap-[8px] rounded-md border border-border bg-bg p-[16px]">
            <div className="flex h-[120px] w-[100px] items-center justify-center rounded-full bg-success/20">
              <span className="text-3xl">🥚</span>
            </div>
            <p className="text-sm font-bold text-text-primary">나의 헬스 알</p>
            <p className="text-xs text-text-secondary">
              달성 챌린지 {cs?.completed_count ?? 0}개 · 최장 {cs?.best_streak ?? 0}일 연속
            </p>
          </div>
        </div>

        {/* Row2: eGFR 추세 */}
        <div className="mt-[24px]">
          <EgfrTrendChart trend={trend} />
        </div>

        {/* Row3: 최신 건강지표 카드 */}
        {h && (
          <div className="mt-[24px] grid grid-cols-4 gap-[16px]">
            {[
              { label: "혈압", value: `${h.systolic_bp}/${h.diastolic_bp}`, unit: "mmHg" },
              { label: "공복혈당", value: String(h.fasting_glucose), unit: "mg/dL" },
              { label: "BMI", value: String(h.bmi), unit: "" },
              { label: "검진일", value: h.checked_date, unit: "" },
            ].map((item) => (
              <Card key={item.label} title={item.label}>
                <p className="text-xl font-bold text-text-primary">{item.value}</p>
                {item.unit && <p className="text-xs text-text-muted">{item.unit}</p>}
              </Card>
            ))}
          </div>
        )}

        {/* Row4: 챌린지 현황 */}
        {cs && (
          <div className="mt-[24px]">
            <Card title="챌린지 현황">
              <div className="flex gap-[32px]">
                {[
                  { label: "진행 중", value: cs.active_count },
                  { label: "완료", value: cs.completed_count },
                  { label: "총 체크인", value: cs.total_checkins },
                  { label: "최장 연속", value: `${cs.best_streak}일` },
                ].map((s) => (
                  <div key={s.label} className="flex flex-col items-center">
                    <span className="text-2xl font-bold text-accent">{s.value}</span>
                    <span className="text-xs text-text-secondary">{s.label}</span>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {/* Row5: 생활습관 요약 */}
        {ls && (
          <div className="mt-[24px]">
            <Card title={`생활습관 요약 (${ls.surveyed_date})`}>
              <div className="flex gap-[24px] text-sm text-text-primary">
                <span>흡연: {LIFESTYLE_LABEL[ls.smoking_status] ?? ls.smoking_status}</span>
                <span>음주: {LIFESTYLE_LABEL[ls.drinking_frequency] ?? ls.drinking_frequency}</span>
                <span>운동: 주 {ls.exercise_days_per_week}회</span>
                {ls.stress_level && <span>스트레스: {LIFESTYLE_LABEL[ls.stress_level] ?? ls.stress_level}</span>}
              </div>
            </Card>
          </div>
        )}

        {!h && !loading && (
          <div className="mt-[24px] rounded-md border border-dashed border-border bg-bg p-[32px] text-center">
            <p className="text-text-muted">검진 데이터가 없습니다.</p>
            <div className="mt-[12px] flex justify-center gap-[12px]">
              <Link to="/manual-input" className="rounded-md bg-accent px-[16px] py-[8px] text-sm font-bold text-bg">
                검진 수치 입력
              </Link>
              <Link to="/lifestyle-survey" className="rounded-md border border-accent px-[16px] py-[8px] text-sm font-bold text-accent">
                생활습관 설문
              </Link>
            </div>
          </div>
        )}

        <p className="mt-[24px] text-center text-xs text-text-muted">
          본 서비스는 의료 진단·처방을 대체하지 않습니다. 수치 해석은 담당 의료진과 상의하세요.
        </p>
      </main>
    </div>
  );
}
