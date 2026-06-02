import { TopNav } from "../components/TopNav";
import { ScreenLabel } from "../components/ScreenLabel";
import { BtnSecondary } from "../components/BtnSecondary";

function ShapBar({
  rank,
  label,
  value,
  shap: _shap,
  note,
  barWidth,
  color,
}: {
  rank: number;
  label: string;
  value: string;
  shap: string;
  note: string;
  barWidth: number;
  color: string;
}) {
  return (
    <div className="flex w-full flex-col gap-[8px] rounded-md border border-border bg-bg p-[16px]">
      <div className="flex items-center justify-between">
        <p className="text-md font-bold text-text-primary">
          {rank}. {label}
        </p>
        <p className="text-sm" style={{ color }}>
          {value}
        </p>
      </div>
      <div className="h-[8px] w-full rounded-sm bg-placeholder">
        <div
          className="h-full rounded-sm"
          style={{ width: barWidth, backgroundColor: color }}
        />
      </div>
      <p className="text-xs text-text-muted">{note}</p>
    </div>
  );
}

export function LLMActionGuidePage() {
  return (
    <div className="flex min-h-screen flex-col bg-bg-alt">
      <ScreenLabel label="15 · LLM 행동 가이드 (SHAP 기반 + PII 토큰화, REQ-LLM-001/002)" />
      <TopNav />

      <main className="flex flex-1 gap-[16px] p-[32px]">
        {/* 좌측: SHAP Top 3 */}
        <div className="flex flex-1 flex-col gap-[12px]">
          <h2 className="text-lg font-bold text-text-primary">
            SHAP Top 3 위험 변수
          </h2>
          <ShapBar rank={1} label="중성지방" value="135 mg/dL" shap="+0.082" note="SHAP +0.082 · 정상 범위 <150 (경계)" barWidth={280} color="#DC2626" />
          <ShapBar rank={2} label="BMI" value="23.6" shap="+0.041" note="SHAP +0.041 · 정상 <23 (경계)" barWidth={160} color="#D97706" />
          <ShapBar rank={3} label="좌식 시간" value="9시간/일" shap="+0.033" note="SHAP +0.033 · 권장 <8시간" barWidth={130} color="#D97706" />
        </div>

        {/* 우측: AI 행동 가이드 */}
        <div className="flex flex-1 flex-col gap-[12px]">
          <h2 className="text-lg font-bold text-text-primary">
            AI 행동 가이드 (스트리밍)
          </h2>

          <div className="flex flex-1 flex-col gap-[12px] rounded-md border border-border bg-bg p-[16px]">
            {[
              {
                title: "🍳 식단 관리",
                body: "중성지방 135mg/dL은 경계 수치입니다. 튀긴 음식과 단 음료를 줄이고, 오메가-3가 풍부한 등푸른 생선을 주 2회 이상 섭취하세요.",
              },
              {
                title: "🏃 신체활동",
                body: "좌식 시간 9시간은 권장(8시간)을 초과합니다. 1시간마다 5분 스트레칭, 점심 후 15분 산책을 권장합니다.",
              },
              {
                title: "⚖️ 체중 관리",
                body: "BMI 23.6은 경계입니다. 하루 300kcal 감량 + 주 150분 중등도 유산소 운동으로 체중 관리를 시작해보세요.",
              },
            ].map((msg) => (
              <div key={msg.title} className="flex gap-[8px]">
                <div className="h-[32px] w-[32px] shrink-0 rounded-full bg-accent" />
                <div className="flex flex-col gap-[4px] rounded-md bg-bg-alt p-[12px]">
                  <p className="text-sm font-bold text-text-primary">{msg.title}</p>
                  <p className="text-xs leading-[1.6] text-text-secondary">{msg.body}</p>
                </div>
              </div>
            ))}

            <div className="rounded-sm border border-warning bg-[#fef3c7] p-[12px]">
              <p className="text-xs leading-[1.5] text-warning">
                ⚠ 본 서비스는 의료 진단·처방을 대체하지 않습니다. 정확한 진단·치료는 의사 상담을 받으세요.
              </p>
            </div>
          </div>

          <div className="flex gap-[12px]">
            <BtnSecondary label="🔄 다시 생성" className="flex-1" />
            <BtnSecondary label="📋 복사" className="flex-1" />
          </div>

          <p className="text-xs leading-[1.5] text-text-muted">
            🔒 사용자 PII는 토큰화되어 LLM에 전송됩니다. 응답 마지막 줄에 면책 문구가 자동 추가됩니다.
          </p>
        </div>
      </main>
    </div>
  );
}
