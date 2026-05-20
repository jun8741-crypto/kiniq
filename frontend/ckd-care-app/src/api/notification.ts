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

export const notificationApi = {
  list: (unread_only = false, limit = 20, offset = 0) =>
    api.get<NotificationListResponse>(
      `/notifications?unread_only=${unread_only}&limit=${limit}&offset=${offset}`
    ),
  markRead: (id: number) =>
    api.patch<Notification>(`/notifications/${id}/read`, {}),
  markAllRead: () =>
    api.patch<{ updated: number }>("/notifications/read-all", {}),
};
