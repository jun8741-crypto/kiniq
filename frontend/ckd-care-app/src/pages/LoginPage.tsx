import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { ScreenLabel } from "../components/ScreenLabel";
import { TextInput } from "../components/TextInput";
import { Checkbox } from "../components/Checkbox";
import { BtnPrimary } from "../components/BtnPrimary";
import { BtnSecondary } from "../components/BtnSecondary";
import { authApi } from "../api/auth";
import { useAuth } from "../contexts/AuthContext";

export function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(true);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // 비밀번호 찾기 상태
  const [showForgot, setShowForgot] = useState(false);
  const [forgotEmail, setForgotEmail] = useState("");
  const [forgotSent, setForgotSent] = useState(false);
  const [forgotLoading, setForgotLoading] = useState(false);
  const [tempPassword, setTempPassword] = useState("");
  const [forgotError, setForgotError] = useState("");

  async function handleLogin() {
    if (!email || !password) { setError("이메일과 비밀번호를 입력하세요."); return; }
    setError("");
    setLoading(true);
    try {
      const res = await authApi.login({ email, password });
      await login(res.access_token, rememberMe);
      navigate("/dashboard");
    } catch (e) {
      setError(e instanceof Error ? e.message : "로그인에 실패했습니다.");
    } finally {
      setLoading(false);
    }
  }

  async function handleForgotSubmit() {
    if (!forgotEmail) {
      setForgotError("이메일을 입력해주세요.");
      return;
    }
    // 클라이언트 측 이메일 형식 검증 (백엔드 영어 에러 차단)
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(forgotEmail)) {
      setForgotError("올바른 이메일 형식이 아닙니다.");
      return;
    }
    setForgotError("");
    setForgotLoading(true);
    try {
      const res = await authApi.forgotPassword(forgotEmail);
      setTempPassword(res.temp_password);
      setForgotSent(true);
    } catch (e) {
      const raw = e instanceof Error ? e.message : "";
      // 백엔드 영어 에러를 한국어로 매핑
      let msg = "임시 비밀번호 발급에 실패했습니다.";
      if (raw.includes("등록된 이메일")) msg = "등록된 이메일이 없습니다.";
      else if (raw.includes("소셜 로그인")) msg = "소셜 로그인 계정은 임시 비밀번호를 사용할 수 없습니다.";
      else if (raw.toLowerCase().includes("email")) msg = "올바른 이메일 형식이 아닙니다.";
      else if (raw) msg = raw;
      setForgotError(msg);
    } finally {
      setForgotLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-bg-alt">
      <ScreenLabel label="01 · 로그인 (REQ-AUTH-01)" />
      <main className="flex flex-1 items-center justify-center p-[32px]">
        <div className="flex w-[440px] flex-col gap-[24px] rounded-lg border border-border bg-bg p-[40px]">
          <div className="flex flex-col items-center gap-[8px]">
            <h1 className="text-2xl font-bold text-text-primary">CKD CARE</h1>
            <p className="text-sm text-text-secondary text-center">
              신장 건강 관리 챌린지에 오신 것을 환영합니다
            </p>
          </div>

          {/* 비밀번호 찾기 패널 */}
          {showForgot ? (
            <div className="flex flex-col gap-[16px] rounded-md border border-border bg-bg-alt p-[16px]">
              <div className="flex items-center justify-between">
                <p className="text-sm font-bold text-text-primary">비밀번호 찾기</p>
                <button
                  className="text-xs text-text-muted hover:text-text-secondary"
                  onClick={() => { setShowForgot(false); setForgotSent(false); setForgotEmail(""); setForgotError(""); }}
                >
                  닫기
                </button>
              </div>

              {forgotError && (
                <div className="rounded-sm bg-danger/10 px-[12px] py-[8px] text-sm text-danger">
                  {forgotError}
                </div>
              )}

              {forgotSent ? (
                <div className="flex flex-col gap-[8px] rounded-sm bg-success/10 px-[12px] py-[10px]">
                  <p className="text-sm text-success font-bold">임시 비밀번호가 발급됐습니다.</p>
                  <p className="text-sm text-success">임시 비밀번호: <span className="font-mono font-bold">{tempPassword}</span></p>
                  <p className="text-xs text-text-secondary">로그인 후 마이페이지에서 비밀번호를 변경해주세요.</p>
                </div>
              ) : (
                <>
                  <TextInput
                    label="가입 시 등록한 이메일"
                    placeholder="email@example.com"
                    type="email"
                    value={forgotEmail}
                    onChange={(e) => setForgotEmail(e.target.value)}
                  />
                  <BtnPrimary
                    label="임시 비밀번호 받기"
                    loading={forgotLoading}
                    onClick={handleForgotSubmit}
                  />
                </>
              )}
            </div>
          ) : (
            <>
              <div className="flex flex-col gap-[16px]">
                <TextInput
                  label="이메일"
                  placeholder="email@example.com"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
                <TextInput
                  label="비밀번호"
                  placeholder="비밀번호를 입력하세요"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>

              {error && (
                <p className="rounded-sm bg-danger/10 px-[12px] py-[8px] text-sm text-danger">
                  {error}
                </p>
              )}

              <div className="flex items-center justify-between">
                <Checkbox
                  label="로그인 유지"
                  checked={rememberMe}
                  onChange={setRememberMe}
                />
                <button
                  className="text-sm text-info hover:underline"
                  onClick={() => setShowForgot(true)}
                >
                  비밀번호 찾기
                </button>
              </div>

              <BtnPrimary
                label="로그인"
                height={48}
                className="w-full"
                onClick={handleLogin}
                loading={loading}
              />
            </>
          )}

          <div className="flex items-center gap-[12px]">
            <div className="h-px flex-1 bg-border" />
            <span className="text-sm text-text-muted">또는</span>
            <div className="h-px flex-1 bg-border" />
          </div>

          <div className="flex flex-col gap-[8px]">
            <BtnSecondary
              label="카카오로 시작하기"
              height={48}
              className="w-full opacity-50"
              onClick={() => alert("카카오 로그인은 서비스 오픈 후 이용 가능합니다.")}
            />
            <BtnSecondary
              label="Google로 시작하기"
              height={48}
              className="w-full opacity-50"
              onClick={() => alert("Google 로그인은 서비스 오픈 후 이용 가능합니다.")}
            />
          </div>

          <p className="text-center text-sm text-text-secondary">
            계정이 없으신가요?{" "}
            <Link to="/signup" className="font-bold text-info">회원가입</Link>
          </p>

          <p className="text-center text-xs text-text-muted">
            본 서비스는 의료 진단·처방을 대체하지 않습니다.
          </p>
        </div>
      </main>
    </div>
  );
}
