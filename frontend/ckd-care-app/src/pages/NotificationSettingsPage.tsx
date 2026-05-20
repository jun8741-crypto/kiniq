import { useState } from "react";
import { TopNav } from "../components/TopNav";
import { ScreenLabel } from "../components/ScreenLabel";
import { BtnPrimary } from "../components/BtnPrimary";
import { TextInput } from "../components/TextInput";

function Toggle({
  enabled,
  onChange,
}: {
  enabled: boolean;
  onChange: () => void;
}) {
  return (
    <button
      onClick={onChange}
      className={`flex h-[24px] w-[48px] items-center rounded-full p-[2px] transition-colors ${
        enabled ? "justify-end bg-success" : "justify-start bg-placeholder"
      }`}
    >
      <div className="h-[20px] w-[20px] rounded-full bg-bg" />
    </button>
  );
}

function ToggleItem({
  title,
  subtitle,
  enabled,
  onToggle,
}: {
  title: string;
  subtitle: string;
  enabled: boolean;
  onToggle: () => void;
}) {
  return (
    <div className="flex items-center justify-between rounded-sm bg-bg-alt p-[12px]">
      <div className="flex flex-col gap-[2px]">
        <p className="text-sm font-bold text-text-primary">{title}</p>
        <p className="text-xs text-text-secondary">{subtitle}</p>
      </div>
      <Toggle enabled={enabled} onChange={onToggle} />
    </div>
  );
}

export function NotificationSettingsPage() {
  const [allNoti, setAllNoti] = useState(true);
  const [checkupReminder, setCheckupReminder] = useState(true);
  const [quiz, setQuiz] = useState(false);

  return (
    <div className="flex min-h-screen flex-col bg-bg-alt">
      <ScreenLabel label="16 · 알림 설정 (REQ-NOTI-003)" />
      <TopNav />

      <main className="flex flex-1 flex-col items-center p-[32px]">
        <div className="flex w-[600px] flex-col gap-[16px] rounded-md border border-border bg-bg p-[32px]">
          <h1 className="text-xl font-bold text-text-primary">알림 설정</h1>

          <ToggleItem
            title="알림 수신"
            subtitle="모든 알림 ON/OFF"
            enabled={allNoti}
            onToggle={() => setAllNoti(!allNoti)}
          />

          <div className="flex flex-col gap-[8px] rounded-sm bg-bg-alt p-[12px]">
            <p className="text-sm font-bold text-text-primary">
              일일 체크인 알림 시간
            </p>
            <p className="text-xs text-text-secondary">
              '왜 안 했어요?' 표현은 사용하지 않습니다.
            </p>
            <TextInput label="시간" placeholder="21:00" />
          </div>

          <ToggleItem
            title="검진 리마인더"
            subtitle="국가건강검진 주기 기준 연간 1~2회"
            enabled={checkupReminder}
            onToggle={() => setCheckupReminder(!checkupReminder)}
          />

          <ToggleItem
            title="일일 퀴즈 (P2)"
            subtitle="매일 아침 O/X 퀴즈 1문항"
            enabled={quiz}
            onToggle={() => setQuiz(!quiz)}
          />

          <BtnPrimary label="저장" className="w-full" height={48} />
        </div>
      </main>
    </div>
  );
}
