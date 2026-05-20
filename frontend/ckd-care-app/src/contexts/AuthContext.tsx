import { createContext, useContext, useState, useEffect, type ReactNode } from "react";
import { authApi, type UserInfo } from "../api/auth";

interface AuthContextValue {
  user: UserInfo | null;
  token: string | null;
  login: (token: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem("access_token"));
  const [user, setUser] = useState<UserInfo | null>(null);
  const [isLoading, setIsLoading] = useState(!!localStorage.getItem("access_token"));

  useEffect(() => {
    if (!token) { setIsLoading(false); return; }
    authApi.me()
      .then(setUser)
      .catch(() => { localStorage.removeItem("access_token"); setToken(null); })
      .finally(() => setIsLoading(false));
  }, [token]);

  async function login(newToken: string) {
    localStorage.setItem("access_token", newToken);
    setToken(newToken);
    const me = await authApi.me();
    setUser(me);
  }

  function logout() {
    localStorage.removeItem("access_token");
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
