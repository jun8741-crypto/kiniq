import { api } from "./client";

export type ChallengeCategory = "HYDRATION" | "EXERCISE" | "DIET" | "SLEEP" | "STRESS";
export type ChallengeTrack = "A" | "B";
export type UserChallengeStatus = "ACTIVE" | "COMPLETED" | "ABANDONED";

export interface Challenge {
  id: number;
  name: string;
  category: ChallengeCategory;
  description: string;
  duration_days: number;
  track: ChallengeTrack;
}

export interface ChallengeListResponse {
  total: number;
  items: Challenge[];
}

export interface UserChallenge {
  id: number;
  challenge_id: number;
  started_at: string;
  status: UserChallengeStatus;
  streak_count: number;
  total_checkins: number;
  last_checkin_date: string | null;
  created_at: string;
}

export interface UserChallengeListResponse {
  total: number;
  items: UserChallenge[];
}

export interface CheckInResponse {
  id: number;
  streak_count: number;
  total_checkins: number;
  last_checkin_date: string;
  status: UserChallengeStatus;
  message: string;
}

export const challengeApi = {
  list: () => api.get<ChallengeListResponse>("/challenges"),
  myList: (limit = 20, offset = 0) =>
    api.get<UserChallengeListResponse>(`/user-challenges?limit=${limit}&offset=${offset}`),
  join: (challenge_id: number, started_at: string) =>
    api.post<UserChallenge>("/user-challenges", { challenge_id, started_at }),
  checkin: (userChallengeId: number) =>
    api.post<CheckInResponse>(`/user-challenges/${userChallengeId}/checkin`, {}),
};
