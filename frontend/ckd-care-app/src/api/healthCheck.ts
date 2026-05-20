import { api } from "./client";

export interface HealthCheckCreateRequest {
  checked_date: string;
  systolic_bp: number;
  diastolic_bp: number;
  fasting_glucose: number;
  creatinine?: number | null;
  total_cholesterol?: number | null;
  hdl_cholesterol?: number | null;
  triglycerides?: number | null;
  weight: number;
  height: number;
  waist_circumference?: number | null;
}

export interface HealthCheckResponse {
  id: number;
  user_id: number;
  checked_date: string;
  systolic_bp: number;
  diastolic_bp: number;
  fasting_glucose: number;
  creatinine: number | null;
  total_cholesterol: number | null;
  hdl_cholesterol: number | null;
  triglycerides: number | null;
  weight: number;
  height: number;
  bmi: number;
  waist_circumference: number | null;
  egfr_estimated: number | null;
  ckd_risk_score: number | null;
  ckd_stage: string | null;
  safety_warning: string | null;
  created_at: string;
}

export interface HealthCheckListResponse {
  total: number;
  items: HealthCheckResponse[];
}

export const healthCheckApi = {
  create: (body: HealthCheckCreateRequest) =>
    api.post<HealthCheckResponse>("/health-checks", body),
  list: (limit = 20, offset = 0) =>
    api.get<HealthCheckListResponse>(`/health-checks?limit=${limit}&offset=${offset}`),
};
