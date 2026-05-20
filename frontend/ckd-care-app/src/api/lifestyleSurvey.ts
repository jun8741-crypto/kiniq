import { api } from "./client";

export type SmokingStatus = "NEVER" | "PAST" | "CURRENT";
export type DrinkingFrequency = "NEVER" | "OCCASIONALLY" | "WEEKLY" | "DAILY";
export type StressLevel = "VERY_LOW" | "LOW" | "MODERATE" | "HIGH" | "VERY_HIGH";

export interface LifestyleSurveyCreateRequest {
  surveyed_date: string;
  smoking_status: SmokingStatus;
  drinking_frequency: DrinkingFrequency;
  exercise_days_per_week: number;
  sleep_hours_per_day?: number | null;
  daily_water_intake?: number | null;
  stress_level?: StressLevel | null;
}

export interface LifestyleSurveyResponse {
  id: number;
  user_id: number;
  surveyed_date: string;
  smoking_status: SmokingStatus;
  drinking_frequency: DrinkingFrequency;
  exercise_days_per_week: number;
  sleep_hours_per_day: number | null;
  daily_water_intake: number | null;
  stress_level: StressLevel | null;
  created_at: string;
}

export interface LifestyleSurveyListResponse {
  total: number;
  items: LifestyleSurveyResponse[];
}

export const lifestyleSurveyApi = {
  create: (body: LifestyleSurveyCreateRequest) =>
    api.post<LifestyleSurveyResponse>("/lifestyle-surveys", body),
  list: (limit = 20, offset = 0) =>
    api.get<LifestyleSurveyListResponse>(`/lifestyle-surveys?limit=${limit}&offset=${offset}`),
};
