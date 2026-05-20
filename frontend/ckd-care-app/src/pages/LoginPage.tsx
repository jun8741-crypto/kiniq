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
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleLogin() {
    if (!email || !password) { setError("이메일과 비밀번호를 입력하세요."); return; }
    setError("");
    setLoading(true);
    try {
      const res = await authApi.login({ email, password });
      await login(res.access_token);
      navigate("/dashboard");
    } catch (e) {
      setError(e instanceof Error ? e.message : "로그인에 실패했습니다.");
    } finally {
      setLoading(false);
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
              신장 건강 챌린지에 다시 오신 것을 환영합니다
            </p>
          </div>

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
            <Checkbox label="로그인 유지" />
            <button className="text-sm text-info">비밀번호 찾기</button>
          </div>

          <BtnPrimary
            label="로그인"
            height={48}
            className="w-full"
            onClick={handleLogin}
            loading={loading}
          />

          <div className="flex items-center gap-[12px]">
            <div className="h-px flex-1 bg-border" />
            <span className="text-sm text-text-muted">또는</span>
            <div className="h-px flex-1 bg-border" />
          </div>

          <BtnSecondary
            label="카카오로 시작하기 (P1)"
            height={48}
            className="w-full"
          />

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
