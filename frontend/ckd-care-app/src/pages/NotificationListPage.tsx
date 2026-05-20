import { useEffect, useState } from "react";
import { TopNav } from "../components/TopNav";
import { ScreenLabel } from "../components/ScreenLabel";
import { notificationApi, type Notification, type NotificationType } from "../api/notification";

const TYPE_LABEL: Record<NotificationType, string> = {
  CHALLENGE_JOINED: "참여",
  CHECKIN_DONE: "체크인",
  CHALLENGE_COMPLETED: "완료",
  CHALLENGE_REMINDER: "리마인더",
};

const TYPE_COLOR: Record<NotificationType, string> = {
  CHALLENGE_JOINED: "bg-info",
  CHECKIN_DONE: "bg-success",
  CHALLENGE_COMPLETED: "bg-accent",
  CHALLENGE_REMINDER: "bg-warning",
};

const TYPE_BORDER: Record<NotificationType, string> = {
  CHALLENGE_JOINED: "border-info",
  CHECKIN_DONE: "border-success",
  CHALLENGE_COMPLETED: "border-accent",
  CHALLENGE_REMINDER: "border-warning",
};

const FILTERS = ["전체", "체크인", "참여", "완료", "리마인더"] as const;
type Filter = (typeof FILTERS)[number];

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const min = Math.floor(diff / 60000);
  if (min < 1) return "방금";
  if (min < 60) return `${min}분 전`;
  const hr = Math.floor(min / 60);
  if (hr < 24) return `${hr}시간 전`;
  return `${Math.floor(hr / 24)}일 전`;
}

export function NotificationListPage() {
  const [items, setItems] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [filter, setFilter] = useState<Filter>("전체");
  const [loading, setLoading] = useState(true);

  async function load(unreadOnly = false) {
    try {
      const res = await notificationApi.list(unreadOnly);
      setItems(res.items);
      setUnreadCount(res.unread_count);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleMarkRead(id: number) {
    await notificationApi.markRead(id);
    setItems((prev) =>
      prev.map((n) => (n.id === id ? { ...n, is_read: true } : n))
    );
    setUnreadCount((c) => Math.max(0, c - 1));
  }

  async function handleMarkAllRead() {
    await notificationApi.markAllRead();
    setItems((prev) => prev.map((n) => ({ ...n, is_read: true })));
    setUnreadCount(0);
  }

  const FILTER_TYPE: Record<Filter, NotificationType | null> = {
    전체: null,
    체크인: "CHECKIN_DONE",
    참여: "CHALLENGE_JOINED",
    완료: "CHALLENGE_COMPLETED",
    리마인더: "CHALLENGE_REMINDER",
  };

  const filtered = filter === "전체"
    ? items
    : items.filter((n) => n.type === FILTER_TYPE[filter]);

  return (
    <div className="flex min-h-screen flex-col bg-bg-alt">
      <ScreenLabel label="17 · 알림 목록 (REQ-NOTI)" />
      <TopNav />

      <main className="flex flex-1 flex-col items-center gap-[16px] p-[32px]">
        <div className="flex w-[760px] items-center justify-between">
          <div className="flex items-center gap-[8px]">
            <h1 className="text-xl font-bold text-text-primary">알림</h1>
            {unreadCount > 0 && (
              <span className="flex h-[20px] min-w-[20px] items-center justify-center rounded-full bg-danger px-[6px] text-xs font-bold text-bg">
                {unreadCount}
              </span>
            )}
          </div>
          {unreadCount > 0 && (
            <button onClick={handleMarkAllRead} className="text-sm text-info">
              모두 읽음 처리
            </button>
          )}
        </div>

        {/* 필터 탭 */}
        <div className="flex w-[760px] gap-[8px]">
          {FILTERS.map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`rounded-sm px-[12px] py-[4px] text-xs ${
                filter === f
                  ? "bg-accent font-bold text-bg"
                  : "border border-border bg-bg font-normal text-text-primary"
              }`}
            >
              {f}
            </button>
          ))}
        </div>

        {/* 알림 목록 */}
        <div className="flex w-[760px] flex-col gap-[8px]">
          {loading ? (
            <p className="text-center text-sm text-text-muted">로딩 중...</p>
          ) : filtered.length === 0 ? (
            <div className="rounded-md border border-dashed border-border bg-bg p-[32px] text-center">
              <p className="text-sm text-text-muted">알림이 없습니다.</p>
            </div>
          ) : (
            filtered.map((n) => (
              <div
                key={n.id}
                onClick={() => !n.is_read && handleMarkRead(n.id)}
                className={`flex cursor-pointer items-center gap-[12px] rounded-sm border ${
                  n.is_read ? "border-border bg-bg" : `${TYPE_BORDER[n.type]} bg-bg-alt`
                } p-[12px] transition-colors hover:bg-bg-alt`}
              >
                <div className={`h-[8px] w-[8px] shrink-0 rounded-full ${n.is_read ? "bg-placeholder" : TYPE_COLOR[n.type]}`} />
                <div className="flex min-w-0 flex-1 flex-col gap-[2px]">
                  <div className="flex items-center gap-[8px]">
                    <p className={`text-sm ${n.is_read ? "font-normal text-text-secondary" : "font-bold text-text-primary"}`}>
                      {n.title}
                    </p>
                    <span className={`rounded-sm px-[6px] py-[1px] text-xs text-bg ${TYPE_COLOR[n.type]}`}>
                      {TYPE_LABEL[n.type]}
                    </span>
                  </div>
                  <p className="text-xs text-text-secondary">{n.message}</p>
                </div>
                <span className="shrink-0 text-xs text-text-muted">{timeAgo(n.created_at)}</span>
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  );
}
