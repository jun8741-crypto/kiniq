import { ScreenLabel } from "../components/ScreenLabel";
import { TextInput } from "../components/TextInput";
import { Checkbox } from "../components/Checkbox";
import { BtnPrimary } from "../components/BtnPrimary";

export function SignupPage() {
  return (
    <div className="flex min-h-screen flex-col bg-bg-alt">
      <ScreenLabel label="02 · 회원가입 (REQ-AUTH-02)" />
      <main className="flex flex-1 items-center justify-center p-[32px]">
        <div className="flex w-[520px] flex-col gap-[24px] rounded-lg border border-border bg-bg p-[40px]">
          {/* 제목 */}
          <h1 className="text-2xl font-bold text-text-primary">회원가입</h1>

          {/* 입력 필드 */}
          <div className="flex flex-col gap-[16px]">
            <TextInput label="이름" placeholder="홍길동" />
            <TextInput label="이메일" placeholder="email@example.com" />
            <div className="flex flex-col gap-[4px]">
              <TextInput label="비밀번호" placeholder="비밀번호를 입력하세요" />
              <p className="text-xs text-text-muted">
                8자 이상, 영문·숫자·특수문자 각 1개 이상
              </p>
            </div>
            <TextInput label="생년월일" placeholder="YYYY-MM-DD" />
          </div>

          {/* 성별 선택 */}
          <div className="flex flex-col gap-[8px]">
            <label className="text-sm font-normal text-text-secondary">
              성별
            </label>
            <div className="flex gap-[12px]">
              <button className="flex-1 rounded-md border border-border-strong bg-bg px-[16px] py-[10px] text-sm font-normal text-text-primary">
                남성
              </button>
              <button className="flex-1 rounded-md border border-border-strong bg-bg px-[16px] py-[10px] text-sm font-normal text-text-primary">
                여성
              </button>
            </div>
          </div>

          {/* 동의 섹션 */}
          <div className="flex flex-col gap-[12px] rounded-sm border border-border bg-bg-alt p-[12px]">
            <p className="text-sm font-bold text-text-primary">
              필수 동의 (개인정보보호법 &sect;23)
            </p>
            <div className="flex flex-col gap-[10px]">
              <Checkbox label="[필수] 민감의료정보 수집·이용 동의" />
              <Checkbox label="[필수] 개인정보 처리방침 동의" />
              <Checkbox label="[필수] 서비스 이용약관 동의" />
              <Checkbox label="[선택] 마케팅 수신 동의" />
            </div>
          </div>

          {/* 가입 버튼 */}
          <BtnPrimary label="가입하기" height={48} className="w-full" />
        </div>
      </main>
    </div>
  );
}
