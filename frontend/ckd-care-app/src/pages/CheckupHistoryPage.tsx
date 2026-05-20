import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { TopNav } from "../components/TopNav";
import { ScreenLabel } from "../components/ScreenLabel";
import { BtnPrimary } from "../components/BtnPrimary";
import { healthCheckApi, type HealthCheckResponse } from "../api/healthCheck";

const CKD_STAGE_COLOR: Record<string, string> = {
  G1: "text-success", G2: "text-success",
  G3a: "text-warning", G3b: "text-warning",
  G4: "text-danger", G5: "text-danger",
};

function egfrColor(v: number | null) {
  if (v === null) return "text-text-muted";
  return v >= 60 ? "text-success" : v >= 30 ? "text-warning" : "text-danger";
}

export function CheckupHistoryPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState<HealthCheckResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    healthCheckApi.list(50, 0)
      .then((r) => setItems(r.items))
      .catch((e) => setError(e instanceof Error ? e.message : "불러오기 실패"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="flex min-h-screen flex-col bg-bg-alt">
      <ScreenLabel label="24 · 검진 이력 (REQ-DATA 누적 데이터)" />
      <TopNav />

      <main className="flex flex-1 flex-col gap-[16px] p-[32px]">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-text-primary">건강검진 이력</h1>
          <BtnPrimary label="+ 새 검진 추가" onClick={() => navigate("/manual-input")} />
        </div>

        {error && (
          <div className="rounded-sm bg-danger/10 px-3 py-2 text-sm text-danger">{error}</div>
        )}

        {loading && (
          <div className="flex h-[200px] items-center justify-center text-sm text-text-muted">
            로딩 중...
          </div>
        )}

        {!loading && items.length === 0 && !error && (
          <div className="flex h-[200px] flex-col items-center justify-center gap-[12px] rounded-md border border-dashed border-border bg-bg text-sm text-text-muted">
            <p>아직 검진 데이터가 없습니다.</p>
            <BtnPrimary label="첫 검진 입력하기" onClick={() => navigate("/manual-input")} />
          </div>
        )}

        {!loading && items.length > 0 && (
          <div className="overflow-hidden rounded-md border border-border bg-bg">
            {/* 헤더 */}
            <div className="grid grid-cols-[140px_80px_80px_100px_120px_100px_1fr] gap-[12px] bg-bg-alt px-[16px] py-[8px]">
              {["검진일", "eGFR", "단계", "공복혈당", "혈압(SBP/DBP)", "BMI", ""].map((h) => (
                <span key={h} className="text-xs font-bold text-text-secondary">{h}</span>
              ))}
            </div>

            {items.map((r, idx) => (
              <div
                key={r.id}
                className="grid grid-cols-[140px_80px_80px_100px_120px_100px_1fr] items-center gap-[12px] border-t border-border px-[16px] py-[12px]"
              >
                <span className={`text-sm ${idx === 0 ? "font-bold text-text-primary" : "text-text-primary"}`}>
                  {r.checked_date}
                  {idx === 0 && <span className="ml-[6px] text-xs text-accent">최신</span>}
                </span>
                <span className={`text-sm font-bold ${egfrColor(r.egfr_estimated)}`}>
                  {r.egfr_estimated != null ? r.egfr_estimated.toFixed(1) : "—"}
                </span>
                <span className={`text-sm ${CKD_STAGE_COLOR[r.ckd_stage ?? ""] ?? "text-text-muted"}`}>
                  {r.ckd_stage ?? "—"}
                </span>
                <span className="text-sm text-text-primary">{r.fasting_glucose}</span>
                <span className="text-sm text-text-primary">{r.systolic_bp}/{r.diastolic_bp}</span>
                <span className="text-sm text-text-primary">{r.bmi}</span>
                <button
                  className="text-sm text-info hover:underline"
                  onClick={() => navigate("/manual-input", { state: { prefill: r } })}
                >
                  재입력 →
                </button>
              </div>
            ))}
          </div>
        )}

        {!loading && items.length > 1 && (
          <div className="flex flex-col gap-[12px] rounded-md border border-border bg-bg p-[16px]">
            <h3 className="text-sm font-bold text-text-primary">eGFR 추이</h3>
            <div className="flex items-end gap-[8px] overflow-x-auto pb-[4px]">
              {[...items].reverse().slice(-6).map((r) => {
                const v = r.egfr_estimated ?? 0;
                const pct = Math.min(v / 120, 1);
                return (
                  <div key={r.id} className="flex flex-col items-center gap-[4px]">
                    <span className={`text-xs font-bold ${egfrColor(r.egfr_estimated)}`}>{v.toFixed(0)}</span>
                    <div
                      className="w-[32px] rounded-t-sm"
                      style={{ height: `${Math.max(pct * 80, 4)}px`, backgroundColor: v >= 60 ? "#059669" : v >= 30 ? "#D97706" : "#DC2626" }}
                    />
                    <span className="text-[10px] text-text-muted">{r.checked_date.slice(5)}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
