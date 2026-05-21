import { api } from "./client";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
}

export interface SignUpRequest {
  email: string;
  password: string;
  name: string;
  gender: "MALE" | "FEMALE";
  birth_date: string;
  phone_number: string;
}

export interface UserInfo {
  id: number;
  name: string;
  email: string;
  phone_number: string;
  birthday: string;
  gender: "MALE" | "FEMALE";
  created_at: string;
}

export const authApi = {
  login: (body: LoginRequest) => api.post<LoginResponse>("/auth/login", body),
  signup: (body: SignUpRequest) => api.post<{ detail: string }>("/auth/signup", body),
  logout: () => api.post<void>("/auth/logout", {}),
  me: () => api.get<UserInfo>("/users/me"),
  changePassword: (body: { current_password: string; new_password: string }) =>
    api.patch<void>("/users/me/password", body),
  deleteAccount: () => api.delete<void>("/users/me"),
  forgotPassword: (email: string) => api.post<{ temp_password: string }>("/auth/forgot-password", { email }),
};
