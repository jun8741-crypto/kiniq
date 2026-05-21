const BASE = "/api/v1";

function getToken(): string | null {
  return localStorage.getItem("access_token") ?? sessionStorage.getItem("access_token");
}

function setToken(token: string): void {
  if (localStorage.getItem("access_token") !== null) {
    localStorage.setItem("access_token", token);
  } else {
    sessionStorage.setItem("access_token", token);
  }
}

function clearToken(): void {
  localStorage.removeItem("access_token");
  sessionStorage.removeItem("access_token");
}

let refreshing: Promise<string | null> | null = null;

async function tryRefresh(): Promise<string | null> {
  if (refreshing) return refreshing;
  refreshing = fetch(`${BASE}/auth/token/refresh`, {
    method: "GET",
    credentials: "include",
  })
    .then(async (res) => {
      if (!res.ok) return null;
      const data = await res.json();
      const newToken: string = data.access_token;
      setToken(newToken);
      return newToken;
    })
    .catch(() => null)
    .finally(() => { refreshing = null; });
  return refreshing;
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE}${path}`, { ...options, headers, credentials: "include" });

  if (res.status === 401) {
    const newToken = await tryRefresh();
    if (!newToken) {
      clearToken();
      window.location.href = "/";
      throw new Error("Unauthorized");
    }
    // 새 토큰으로 원래 요청 재시도
    const retryHeaders = { ...headers, Authorization: `Bearer ${newToken}` };
    const retry = await fetch(`${BASE}${path}`, { ...options, headers: retryHeaders, credentials: "include" });
    if (retry.status === 401) {
      clearToken();
      window.location.href = "/";
      throw new Error("Unauthorized");
    }
    const retryData = await retry.json().catch(() => ({}));
    if (!retry.ok) {
      const message = retryData?.detail ?? `HTTP ${retry.status}`;
      throw new Error(Array.isArray(message) ? message[0]?.msg ?? String(message) : String(message));
    }
    return retryData as T;
  }

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const message = data?.detail ?? `HTTP ${res.status}`;
    throw new Error(Array.isArray(message) ? message[0]?.msg ?? String(message) : String(message));
  }

  return data as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path, { method: "GET" }),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "POST", body: JSON.stringify(body) }),
  patch: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "PATCH", body: JSON.stringify(body) }),
  delete: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};
