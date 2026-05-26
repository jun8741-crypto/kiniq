import { api } from "./client";

export type ItemCode =
  | "PROTECT"
  | "MINI_BOOSTER"
  | "SKIN_S_BLUE"
  | "SKIN_S_GREEN"
  | "SKIN_M_RED"
  | "SKIN_M_PURPLE"
  | "SKIN_L_GOLD";

export type CharacterSpecies = "TURTLE" | "PENGUIN" | "SQUIRREL";

export const SPECIES_EMOJI: Record<CharacterSpecies, string> = {
  TURTLE: "🐢",
  PENGUIN: "🐧",
  SQUIRREL: "🐿️",
};

export const SPECIES_LABEL: Record<CharacterSpecies, string> = {
  TURTLE: "거북이",
  PENGUIN: "펭귄",
  SQUIRREL: "다람쥐",
};

export type PointReason =
  | "LOGIN"
  | "CHECKIN"
  | "LUCKY"
  | "STREAK_BONUS"
  | "STAGE_BONUS"
  | "FULL_PARTICIPATION"
  | "PURCHASE"
  | "PROTECT_CONSUME"
  | "REFUND";

export interface EggResponse {
  egg_no: number;
  progress_checkins: number;
  current_stage: number;
  progress_percent: number;
  goal_70_alerted: boolean;
  goal_90_alerted: boolean;
  is_legendary: boolean | null;
  species: CharacterSpecies | null;
  character_name: string | null;
  started_at: string;
}

export interface EggHistoryItem {
  egg_no: number;
  is_legendary: boolean | null;
  species: CharacterSpecies | null;
  character_name: string | null;
  started_at: string;
  hatched_at: string;
}

export interface EggHistoryResponse {
  total: number;
  legendary_count: number;
  items: EggHistoryItem[];
}

export interface ChargeModeResponse {
  is_active: boolean;
  entered_at: string | null;
  exited_at: string | null;
  days_since_last_checkin: number | null;
  warning_4d_alerted: boolean;
  warning_5d_alerted: boolean;
  warning_6d_alerted: boolean;
}

export interface MascotResponse {
  current_egg: EggResponse;
  charge_mode: ChargeModeResponse;
  legendary_unlocked: boolean;
  skin_active: ItemCode | null;
}

export interface InventoryItem {
  item_code: ItemCode;
  quantity: number;
  acquired_at: string;
}

export interface InventoryResponse {
  total: number;
  items: InventoryItem[];
}

export interface PointBalanceResponse {
  balance: number;
  lifetime_earned: number;
  lifetime_spent: number;
}

export interface PointTransactionItem {
  id: number;
  amount: number;
  reason: PointReason;
  extra: Record<string, unknown>;
  created_at: string;
}

export interface PointTransactionListResponse {
  total: number;
  items: PointTransactionItem[];
}

export interface PurchaseResponse {
  item_code: ItemCode;
  new_quantity: number;
  spent: number;
  new_balance: number;
}

export const gamificationApi = {
  getCurrentEgg: () => api.get<EggResponse>("/gamification/eggs"),
  getEggHistory: () => api.get<EggHistoryResponse>("/gamification/eggs/history"),
  getMascot: () => api.get<MascotResponse>("/gamification/mascot"),
  getChargeMode: () => api.get<ChargeModeResponse>("/gamification/charge-mode"),
  exitChargeMode: () => api.post<ChargeModeResponse>("/gamification/charge-mode/exit", {}),
  getInventory: () => api.get<InventoryResponse>("/inventory"),
  renameCharacter: (eggId: number, name: string) =>
    api.patch<EggHistoryItem>(`/gamification/eggs/${eggId}/name`, { name }),
};

export const pointsApi = {
  getBalance: () => api.get<PointBalanceResponse>("/points/balance"),
  getTransactions: (limit = 20, offset = 0) =>
    api.get<PointTransactionListResponse>(`/points/transactions?limit=${limit}&offset=${offset}`),
  purchase: (item_code: ItemCode) =>
    api.post<PurchaseResponse>("/points/purchase", { item_code }),
};
