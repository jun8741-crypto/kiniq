import { TopNav } from "../components/TopNav";
import { ScreenLabel } from "../components/ScreenLabel";
import { BtnPrimary } from "../components/BtnPrimary";

const headers = ["검진일", "입력 방법", "eGFR", "단계", "공복혈당", "SBP/DBP", "중성지방", "동작"];
const headerWidths = ["w-[120px]", "w-[80px]", "w-[100px]", "w-[80px]", "w-[100px]", "w-[120px]", "w-[100px]", "flex-1"];

const rows = [
  {
    date: "2026-05-10",
    method: "OCR",
    egfr: "88.4",
    egfrColor: "text-success",
    stage: "G1",
    stageColor: "text-success",
    glucose: "105",
    glucoseColor: "text-warning",
    bp: "128/82",
    bpColor: "text-text-primary",
    tg: "135",
    tgColor: "text-warning",
    bold: true,
  },
  {
    date: "2026-01-15",
    method: "수동",
    egfr: "90.2",
    egfrColor: "text-success",
    stage: "G1",
    stageColor: "text-success",
    glucose: "98",
    glucoseColor: "text-text-primary",
    bp: "125/80",
    bpColor: "text-text-primary",
    tg: "128",
    tgColor: "text-text-primary",
    bold: false,
  },
  {
    date: "2025-08-20",
    method: "OCR",
    egfr: "92.0",
    egfrColor: "text-success",
    stage: "G1",
    stageColor: "text-success",
    glucose: "95",
    glucoseColor: "text-text-primary",
    bp: "122/78",
    bpColor: "text-text-primary",
    tg: "110",
    tgColor: "text-text-primary",
    bold: false,
  },
];

export function CheckupHistoryPage() {
  return (
    <div className="flex min-h-screen flex-col bg-bg-alt">
      <ScreenLabel label="24 · 검진 이력 (REQ-DATA 누적 데이터)" />
      <TopNav />

      <main className="flex flex-1 flex-col gap-[16px] p-[32px]">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-text-primary">건강검진 이력</h1>
          <BtnPrimary label="+ 새 검진 추가" />
        </div>

        {/* 테이블 */}
        <div className="overflow-hidden rounded-md border border-border bg-bg">
          {/* 헤더 */}
          <div className="flex gap-[12px] bg-bg-alt px-[16px] py-[8px]">
            {headers.map((h, i) => (
              <span key={h} className={`text-xs font-bold text-text-secondary ${headerWidths[i]}`}>
                {h}
              </span>
            ))}
          </div>

          {/* 행 */}
          {rows.map((r) => (
            <div
              key={r.date}
              className="flex items-center gap-[12px] border-t border-border px-[16px] py-[12px]"
            >
              <span className={`w-[120px] text-sm ${r.bold ? "font-bold" : ""} text-text-primary`}>
                {r.date}
              </span>
              <span className="w-[80px] text-sm text-text-secondary">{r.method}</span>
              <span className={`w-[100px] text-sm font-bold ${r.egfrColor}`}>{r.egfr}</span>
              <span className={`w-[80px] text-sm ${r.stageColor}`}>{r.stage}</span>
              <span className={`w-[100px] text-sm ${r.glucoseColor}`}>{r.glucose}</span>
              <span className={`w-[120px] text-sm ${r.bpColor}`}>{r.bp}</span>
              <span className={`w-[100px] text-sm ${r.tgColor}`}>{r.tg}</span>
              <button className="flex-1 text-sm text-info">보기 →</button>
            </div>
          ))}
        </div>

        {/* eGFR 추세 */}
        <div className="flex flex-col gap-[12px] rounded-md border border-border bg-bg p-[16px]">
          <h3 className="text-sm font-bold text-text-primary">
            eGFR 추세 (최근 3회)
          </h3>
          <div className="flex h-[120px] items-center justify-center rounded-sm border border-border-strong bg-placeholder">
            <p className="text-xs text-text-secondary">
              📈 92.0 (8월) → 90.2 (1월) → 88.4 (5월) · 점진적 감소 추이
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
