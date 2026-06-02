import { MailCheck } from "lucide-react";
import { ScreenLabel } from "../components/ScreenLabel";
import { BtnSecondary } from "../components/BtnSecondary";

export function EmailVerifyPage() {
  return (
    <div className="flex min-h-screen flex-col bg-bg-alt">
      <ScreenLabel label="03 · 이메일 인증 (REQ-AUTH-03)" />
      <main className="flex flex-1 items-center justify-center p-[32px]">
        <div className="flex w-[480px] flex-col items-center gap-[24px] rounded-lg border border-border bg-bg p-[40px]">
          {/* 아이콘 */}
          <MailCheck size={64} className="text-success" />

          {/* 제목 */}
          <h1 className="text-xl font-bold text-text-primary">
            이메일을 확인해주세요
          </h1>

          {/* 설명 */}
          <p className="text-center text-sm text-text-secondary">
            user@example.com 로 인증 링크를 발송했습니다.
            <br />
            24시간 내 인증을 완료해주세요.
          </p>

          {/* 안내 박스 */}
          <div className="w-full rounded-sm bg-bg-alt p-[12px]">
            <p className="text-xs text-text-secondary">
              메일이 도착하지 않았다면 스팸함을 확인해주세요.
            </p>
          </div>

          {/* 재발송 버튼 */}
          <BtnSecondary
            label="인증 메일 재발송"
            height={44}
            className="w-full"
          />
        </div>
      </main>
    </div>
  );
}
