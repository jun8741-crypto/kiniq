import { ScreenLabel } from "../components/ScreenLabel";
import { TextInput } from "../components/TextInput";
import { Checkbox } from "../components/Checkbox";
import { BtnPrimary } from "../components/BtnPrimary";
import { BtnSecondary } from "../components/BtnSecondary";

export function LoginPage() {
  return (
    <div className="flex min-h-screen flex-col bg-bg-alt">
      <ScreenLabel label="01 · 로그인 (REQ-AUTH-01)" />
      <main className="flex flex-1 items-center justify-center p-[32px]">
        <div className="flex w-[440px] flex-col gap-[24px] rounded-lg border border-border bg-bg p-[40px]">
          {/* 브랜드 */}
          <div className="flex flex-col items-center gap-[8px]">
            <h1 className="text-2xl font-bold text-text-primary">CKD CARE</h1>
            <p className="text-sm text-text-secondary text-center">
              신장 건강 챌린지에 다시 오신 것을 환영합니다
            </p>
          </div>

          {/* 입력 필드 */}
          <div className="flex flex-col gap-[16px]">
            <TextInput label="이메일" placeholder="email@example.com" />
            <TextInput label="비밀번호" placeholder="비밀번호를 입력하세요" />
          </div>

          {/* 로그인 유지 + 비밀번호 찾기 */}
          <div className="flex items-center justify-between">
            <Checkbox label="로그인 유지" />
            <button className="text-sm text-info">비밀번호 찾기</button>
          </div>

          {/* 로그인 버튼 */}
          <BtnPrimary label="로그인" height={48} className="w-full" />

          {/* 구분선 */}
          <div className="flex items-center gap-[12px]">
            <div className="h-px flex-1 bg-border" />
            <span className="text-sm text-text-muted">또는</span>
            <div className="h-px flex-1 bg-border" />
          </div>

          {/* 카카오 로그인 */}
          <BtnSecondary
            label="카카오로 시작하기 (P1)"
            height={48}
            className="w-full"
          />

          {/* 회원가입 안내 */}
          <p className="text-center text-sm text-text-secondary">
            계정이 없으신가요?{" "}
            <button className="font-bold text-info">회원가입</button>
          </p>

          {/* 면책 문구 */}
          <p className="text-center text-xs text-text-muted">
            본 서비스는 의료 진단·처방을 대체하지 않습니다.
          </p>
        </div>
      </main>
    </div>
  );
}
