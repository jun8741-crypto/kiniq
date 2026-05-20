import { TopNav } from "../components/TopNav";
import { ScreenLabel } from "../components/ScreenLabel";

const filters = ["전체", "체크인", "검진", "가족 응원"];

const notifications = [
  {
    dotColor: "bg-info",
    borderColor: "border-info",
    bgColor: "bg-bg-alt",
    title: "오늘 챌린지 체크인 시간이에요",
    subtitle: "3일 연속 달성 중! 오늘도 화이팅 💪",
    time: "방금",
    bold: true,
  },
  {
    dotColor: "bg-placeholder",
    borderColor: "border-border",
    bgColor: "bg-bg",
    title: "가족이 응원 메시지를 보냈어요 💌",
    subtitle: '"오늘도 화이팅, 우리 아빠!" — 딸',
    time: "2시간 전",
    bold: false,
  },
  {
    dotColor: "bg-placeholder",
    borderColor: "border-border",
    bgColor: "bg-bg",
    title: "오늘의 건강 퀴즈가 도착했어요",
    subtitle: "맞히면 다음 챌린지 포인트 2배!",
    time: "오늘 8:00",
    bold: false,
  },
  {
    dotColor: "bg-placeholder",
    borderColor: "border-border",
    bgColor: "bg-bg",
    title: "새 검진 결과지를 입력할 시간이에요",
    subtitle: "국가건강검진 주기 기준 · 카메라로 바로 촬영",
    time: "어제",
    bold: false,
  },
  {
    dotColor: "bg-warning",
    borderColor: "border-warning",
    bgColor: "bg-bg",
    title: "미세먼지 매우 나쁨 · 실내 챌린지 추천",
    subtitle: "OO 지하상가 20분 걷기 챌린지 어떨까요?",
    time: "3일 전",
    bold: true,
    titleColor: "text-warning",
  },
];

export function NotificationListPage() {
  return (
    <div className="flex min-h-screen flex-col bg-bg-alt">
      <ScreenLabel label="17 · 알림 목록 (REQ-NOTI)" />
      <TopNav />

      <main className="flex flex-1 flex-col items-center gap-[16px] p-[32px]">
        <div className="flex w-[760px] items-center justify-between">
          <h1 className="text-xl font-bold text-text-primary">알림</h1>
          <button className="text-sm text-info">모두 읽음 처리</button>
        </div>

        <div className="flex w-[760px] gap-[8px]">
          {filters.map((f, i) => (
            <button
              key={f}
              className={`rounded-sm px-[12px] py-[4px] text-xs ${
                i === 0
                  ? "bg-accent font-bold text-bg"
                  : "border border-border bg-bg font-normal text-text-primary"
              }`}
            >
              {f}
            </button>
          ))}
        </div>

        <div className="flex w-[760px] flex-col gap-[8px]">
          {notifications.map((n) => (
            <div
              key={n.title}
              className={`flex items-center gap-[12px] rounded-sm border ${n.borderColor} ${n.bgColor} p-[12px]`}
            >
              <div className={`h-[8px] w-[8px] shrink-0 rounded-full ${n.dotColor}`} />
              <div className="flex min-w-0 flex-1 flex-col gap-[2px]">
                <p
                  className={`text-sm ${n.bold ? "font-bold" : "font-normal"} ${
                    n.titleColor ?? "text-text-primary"
                  }`}
                >
                  {n.title}
                </p>
                <p className="text-xs text-text-secondary">{n.subtitle}</p>
              </div>
              <span className="shrink-0 text-xs text-text-muted">{n.time}</span>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
