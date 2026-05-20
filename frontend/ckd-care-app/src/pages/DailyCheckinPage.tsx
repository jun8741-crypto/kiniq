import { ScreenLabel } from "../components/ScreenLabel";
import { TopNav } from "../components/TopNav";
import { BtnPrimary } from "../components/BtnPrimary";

/* 감정 이모티콘 */
const emotions = [
  { emoji: "😄", label: "아주 좋음" },
  { emoji: "🙂", label: "좋음" },
  { emoji: "😐", label: "보통" },
  { emoji: "😟", label: "불안" },
  { emoji: "😢", label: "우울" },
  { emoji: "😠", label: "짜증" },
  { emoji: "😴", label: "피곤" },
];

export function DailyCheckinPage() {
  return (
    <div className="flex min-h-screen flex-col bg-bg-alt">
      <ScreenLabel label="12 · 데일리 체크인 (REQ-CHK-01)" />
      <TopNav />
      <main className="flex flex-1 flex-col items-center p-[32px]">
        {/* 제목 */}
        <h1 className="text-2xl font-bold text-text-primary">오늘의 체크인</h1>
        <p className="mt-[8px] text-sm text-text-secondary">
          2026-05-19 (월) · 오후 9:00 알림
        </p>

        {/* 정보 박스 */}
        <div className="mt-[16px] w-[760px] rounded-sm border border-border bg-bg p-[12px]">
          <p className="text-xs text-text-secondary">
            감정만 기록해도 체크인 완료로 인정됩니다. 각 항목은 선택 사항입니다.
          </p>
        </div>

        {/* 체크인 카드 */}
        <div className="mt-[24px] w-[760px] rounded-md border border-border bg-bg p-[24px]">
          {/* 수분 섭취 예시 */}
          <p className="text-md font-bold text-text-primary">
            수분 섭취 1.5L
          </p>
          <p className="mt-[4px] text-sm text-text-secondary">
            오늘 수분 섭취 목표를 달성했나요?
          </p>

          {/* 성공/절반/실패 버튼 */}
          <div className="mt-[16px] flex gap-[12px]">
            <button className="flex-1 rounded-md border border-success bg-success/10 px-[16px] py-[12px] text-sm font-bold text-success">
              성공
            </button>
            <button className="flex-1 rounded-md border border-warning bg-warning/10 px-[16px] py-[12px] text-sm font-bold text-warning">
              절반
            </button>
            <button className="flex-1 rounded-md border border-danger bg-danger/10 px-[16px] py-[12px] text-sm font-bold text-danger">
              실패
            </button>
          </div>

          {/* 구분선 */}
          <div className="my-[20px] h-px bg-border" />

          {/* 감정 기록 */}
          <p className="text-md font-bold text-text-primary">
            오늘의 감정
          </p>
          <p className="mt-[4px] text-sm text-text-secondary">
            오늘 하루 어떤 기분이었나요?
          </p>
          <div className="mt-[16px] flex gap-[12px]">
            {emotions.map((e) => (
              <button
                key={e.label}
                className="flex flex-col items-center gap-[4px] rounded-md border border-border bg-bg p-[12px] hover:bg-bg-alt"
              >
                <span className="text-2xl">{e.emoji}</span>
                <span className="text-xs text-text-secondary">{e.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* 추가 항목 안내 */}
        <p className="mt-[16px] text-sm text-text-muted">
          &hellip; 식단·운동·수면·스트레스 항목도 동일 패턴으로 체크인합니다.
        </p>

        {/* 저장 버튼 */}
        <div className="mt-[24px] w-[760px]">
          <BtnPrimary label="체크인 저장하기" height={52} className="w-full" />
        </div>
      </main>
    </div>
  );
}
