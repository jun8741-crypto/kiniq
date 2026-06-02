import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export function OAuthCallbackPage() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const { login } = useAuth();
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    const token = params.get("token");
    const error = params.get("error");

    if (error) {
      setErrorMsg(decodeURIComponent(error));
      return;
    }
    if (!token) {
      setErrorMsg("로그인 처리 중 오류가 발생했습니다.");
      return;
    }

    login(token, true)
      .then(() => navigate("/dashboard", { replace: true }))
      .catch(() => setErrorMsg("로그인 처리 중 오류가 발생했습니다."));
  }, []);  // eslint-disable-line react-hooks/exhaustive-deps

  if (errorMsg) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-[16px] bg-bg-alt p-[32px]">
        <p className="rounded-md bg-danger/10 px-[16px] py-[12px] text-sm text-danger">{errorMsg}</p>
        <button
          onClick={() => navigate("/", { replace: true })}
          className="text-sm text-info hover:underline"
        >
          로그인 페이지로 돌아가기
        </button>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-bg-alt">
      <p className="text-sm text-text-secondary">로그인 처리 중...</p>
    </div>
  );
}
