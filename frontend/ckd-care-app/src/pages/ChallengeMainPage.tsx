import { Droplets, UtensilsCrossed, Footprints, Moon, Brain } from "lucide-react";
import { ScreenLabel } from "../components/ScreenLabel";
import { TopNav } from "../components/TopNav";
import { BtnSecondary } from "../components/BtnSecondary";
import { Card } from "../components/Card";
import type { LucideIcon } from "lucide-react";

/* 챌린지 데이터 */
interface Challenge {
  icon: LucideIcon;
  title: string;
  weight: string;
  done: boolean;
  hp: number;
  borderColor: string;
}

const challenges: Challenge[] = [
  { icon: Droplets, title: "수분 섭취 1.5L", weight: "x1.2", done: true, hp: 90, borderColor: "border-info" },
  { icon: UtensilsCrossed, title: "저염식 한 끼", weight: "x1.5", done: true, hp: 85, borderColor: "border-success" },
  { icon: Footprints, title: "30분 걷기", weight: "x1.0", done: true, hp: 78, borderColor: "border-warning" },
  { icon: Moon, title: "11시 이전 취침", weight: "x1.0", done: false, hp: 70, borderColor: "border-accent" },
  { icon: Brain, title: "스트레스 관리 5분", weight: "x0.8", done: false, hp: 65, borderColor: "border-border-strong" },
];

export function ChallengeMainPage() {
  return (
    <div className="flex min-h-screen flex-col bg-bg-alt">
      <ScreenLabel label="11 · 챌린지 메인 (REQ-CHG-01)" />
      <TopNav />
      <main className="flex flex-1 flex-col p-[32px]">
        {/* 헤더 */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-text-primary">
              오늘의 챌린지
            </h1>
            <p className="mt-[4px] text-sm text-text-secondary">
              A 트랙 — 생활습관 개선을 통한 CKD 진행 억제
            </p>
          </div>
          <BtnSecondary label="🍺 회식 모드" />
        </div>

        {/* 달성률 바 */}
        <div className="mt-[24px] rounded-md border border-border bg-bg p-[16px]">
          <div className="flex items-center justify-between">
            <p className="text-sm font-bold text-text-primary">3 / 5 항목</p>
            <p className="text-sm font-bold text-accent">60%</p>
          </div>
          <div className="mt-[8px] h-[10px] w-full rounded-full bg-placeholder">
            <div className="h-full w-[60%] rounded-full bg-accent" />
          </div>
        </div>

        {/* 챌린지 카드들 */}
        <div className="mt-[24px] flex flex-col gap-[12px]">
          {challenges.map((c) => (
            <div
              key={c.title}
              className={`flex items-center gap-[16px] rounded-md border-l-4 ${c.borderColor} border border-border bg-bg p-[16px]`}
            >
              {/* 체크 */}
              <div
                className={`flex h-[24px] w-[24px] items-center justify-center rounded-full ${
                  c.done ? "bg-success" : "border-2 border-border-strong"
                }`}
              >
                {c.done && (
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M3 7L6 10L11 4" stroke="white" strokeWidth="2" />
                  </svg>
                )}
              </div>

              {/* 아이콘 + 제목 */}
              <c.icon size={20} className="shrink-0 text-text-secondary" />
              <div className="flex-1">
                <p className="text-sm font-bold text-text-primary">{c.title}</p>
              </div>

              {/* 가중치 */}
              <span className="text-xs text-text-muted">{c.weight}</span>

              {/* 알 체력 바 */}
              <div className="flex w-[100px] items-center gap-[4px]">
                <div className="h-[6px] flex-1 rounded-full bg-placeholder">
                  <div
                    className="h-full rounded-full bg-success"
                    style={{ width: `${c.hp}%` }}
                  />
                </div>
                <span className="text-xs text-text-muted">{c.hp}</span>
              </div>
            </div>
          ))}
        </div>

        {/* 빈 슬롯 */}
        <div className="mt-[12px] rounded-md border border-dashed border-border bg-bg p-[16px] text-center">
          <p className="text-sm text-text-muted">
            스테이지 1 완료 시 새 챌린지 5개 자동 배정
          </p>
        </div>

        {/* 예상 Risk Score 개선 */}
        <Card title="예상 Risk Score 개선" className="mt-[24px]">
          <div className="flex items-center gap-[16px]">
            <div className="flex flex-col items-center">
              <span className="text-xs text-text-muted">현재</span>
              <span className="text-lg font-bold text-warning">32%</span>
            </div>
            <span className="text-text-muted">&rarr;</span>
            <div className="flex flex-col items-center">
              <span className="text-xs text-text-muted">예상</span>
              <span className="text-lg font-bold text-success">28%</span>
            </div>
            <p className="flex-1 text-xs text-text-secondary">
              오늘의 챌린지를 모두 달성하면 위험도가 약 4%p 감소할 것으로
              예상됩니다.
            </p>
          </div>
        </Card>
      </main>
    </div>
  );
}
