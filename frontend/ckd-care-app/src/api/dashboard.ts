import { api } from "./client";

export interface LatestHealthMetrics {
  checked_date: string;
  systolic_bp: number;
  diastolic_bp: number;
  fasting_glucose: number;
  bmi: number;
  egfr_estimated: number | null;
  ckd_stage: string | null;
  ckd_risk_score: number | null;
}

export interface ChallengeStats {
  active_count: number;
  completed_count: number;
  total_checkins: number;
  best_streak: number;
}

export interface LatestLifestyleSummary {
  surveyed_date: string;
  smoking_status: string;
  drinking_frequency: string;
  exercise_days_per_week: number;
  stress_level: string | null;
}

export interface DashboardSummary {
  latest_health: LatestHealthMetrics | null;
  challenge_stats: ChallengeStats;
  latest_lifestyle: LatestLifestyleSummary | null;
  generated_at: string;
}

export interface EgfrDataPoint {
  checked_date: string;
  egfr_estimated: number;
}

export interface EgfrTrend {
  data_points: EgfrDataPoint[];
}

export const dashboardApi = {
  getSummary: () => api.get<DashboardSummary>("/dashboard/summary"),
  getEgfrTrend: (limit = 12) => api.get<EgfrTrend>(`/dashboard/egfr-trend?limit=${limit}`),
};
