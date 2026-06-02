import { ArrowRight } from "lucide-react";
import { TopNav } from "../components/TopNav";
import { ScreenLabel } from "../components/ScreenLabel";
import { Tag } from "../components/Tag";

export function SimulationPage() {
  return (
    <div className="flex min-h-screen flex-col bg-bg-alt">
      <ScreenLabel label="23 · 예상 eGFR 시뮬레이션 (REQ-CHAL-007/REQ-DASH-003)" />
      <TopNav />

      <main className="flex flex-1 flex-col items-center gap-[24px] p-[32px]">
        <h1 className="text-2xl font-bold text-text-primary">
          챌린지를 100% 달성하면?
        </h1>
        <p className="text-sm text-text-muted">
          가상 시뮬레이션 — 실측이 아닙니다. ※ G4·G5(eGFR&lt;30)는 boost 미적용
        </p>

        {/* 비교 카드 */}
        <div className="flex w-[840px] items-center justify-center gap-[24px]">
          <div className="flex flex-1 flex-col items-center gap-[8px] rounded-md border border-border bg-bg p-[24px]">
            <p className="text-sm text-text-secondary">현재 (실측)</p>
            <p className="text-3xl font-bold text-success">88.4</p>
            <p className="text-xs text-text-muted">eGFR mL/min/1.73m²</p>
            <Tag label="G1 정상" />
          </div>

          <ArrowRight size={48} className="shrink-0 text-accent" />

          <div className="flex flex-1 flex-col items-center gap-[8px] rounded-md border-2 border-success bg-bg p-[24px]">
            <p className="text-sm text-text-secondary">3개월 후 예상</p>
            <p className="text-3xl font-bold text-success">91.2</p>
            <p className="text-xs text-text-muted">예상 eGFR (+2.8)</p>
            <Tag label="G1 유지" />
          </div>
        </div>

        {/* 가중치 */}
        <div className="flex w-[840px] flex-col gap-[12px] rounded-md border border-border bg-bg p-[16px]">
          <h3 className="text-md font-bold text-text-primary">
            의학적 가중치 적용 (REQ-CHAL-007)
          </h3>
          <div className="flex justify-between">
            {["식단 0.35", "운동 0.25", "수면 0.15", "수분 0.12", "스트레스 0.10"].map(
              (w) => (
                <span key={w} className="text-xs text-success">
                  {w}
                </span>
              )
            )}
          </div>
        </div>

        <p className="w-[760px] text-center text-xs leading-[1.6] text-text-muted">
          ※ 표현 규칙 — '위험을 낮출 수 있다' / '예방에 도움이 됩니다' / '관리·개선'
          <br />
          금지: '막을 수 있다' / '예방됩니다' / '치료' / '확진' / '진단합니다'
        </p>
      </main>
    </div>
  );
}
