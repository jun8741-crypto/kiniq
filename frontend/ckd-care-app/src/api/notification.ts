import { api } from "./client";

export type NotificationType =
  | "CHALLENGE_JOINED"
  | "CHECKIN_DONE"
  | "CHALLENGE_COMPLETED"
  | "CHALLENGE_REMINDER";

export interface Notification {
  id: number;
  user_id: number;
  type: NotificationType;
  title: string;
  message: string;
  is_read: boolean;
  related_id: number | null;
  created_at: string;
}

export interface NotificationListResponse {
  total: number;
  unread_count: number;
  items: Notification[];
}

export interface NotificationSetting {
  challenge_joined_enabled: boolean;
  checkin_done_enabled: boolean;
  challenge_completed_enabled: boolean;
  challenge_reminder_enabled: boolean;
}

export const notificationApi = {
  list: (unread_only = false, limit = 20, offset = 0) =>
    api.get<NotificationListResponse>(
      `/notifications?unread_only=${unread_only}&limit=${limit}&offset=${offset}`
    ),
  markRead: (id: number) =>
    api.patch<Notification>(`/notifications/${id}/read`, {}),
  markAllRead: () =>
    api.patch<{ updated: number }>("/notifications/read-all", {}),
  getSettings: () =>
    api.get<NotificationSetting>("/notifications/settings"),
  updateSettings: (body: Partial<NotificationSetting>) =>
    api.patch<NotificationSetting>("/notifications/settings", body),
};
