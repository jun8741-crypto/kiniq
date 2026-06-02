import { HeartHandshake } from "lucide-react";
import { TopNav } from "../components/TopNav";
import { ScreenLabel } from "../components/ScreenLabel";
import { BtnPrimary } from "../components/BtnPrimary";
import { BtnSecondary } from "../components/BtnSecondary";
import { Tag } from "../components/Tag";

export function SlumpPage() {
  return (
    <div className="flex min-h-screen flex-col bg-bg-alt">
      <ScreenLabel label="14 · 슬럼프 + 마이크로 챌린지 (REQ-CHAL-006)" />
      <TopNav />

      <main className="flex flex-1 flex-col items-center justify-center p-[32px]">
        <div className="flex w-[560px] flex-col gap-[16px] rounded-lg border border-border bg-bg p-[40px]">
          <div className="flex flex-col items-center gap-[16px]">
            <HeartHandshake size={80} className="text-warning" />
            <h1 className="w-full text-center text-xl font-bold text-text-primary">
              잠시 쉬어가도 괜찮아요
            </h1>
            <p className="w-full text-center text-sm leading-[1.6] text-text-secondary">
              5일 동안 체크인을 못하셨네요.
              <br />
              작은 것부터 다시 시작해볼까요?
            </p>

            <div className="flex w-full flex-col items-center gap-[12px] rounded-md bg-bg-alt p-[16px]">
              <p className="w-full text-center text-xs text-text-muted">
                오늘의 마이크로 챌린지
              </p>
              <p className="w-full text-center text-lg font-bold text-text-primary">
                점심 국물 반만 남기기
              </p>
              <Tag label="1분 미션" />
            </div>

            <div className="flex w-full gap-[12px]">
              <BtnSecondary label="오늘 못해요" className="w-full" height={48} />
              <BtnPrimary label="오늘은 해볼게요!" className="w-full" height={48} />
            </div>
          </div>
        </div>

        <p className="mt-[16px] text-xs text-text-muted">
          💌 슬럼프 기록은 다음 챌린지 강도 조정에 반영됩니다.
        </p>
      </main>
    </div>
  );
}
