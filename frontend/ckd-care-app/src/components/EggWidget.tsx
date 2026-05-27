import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { gamificationApi, SPECIES_EMOJI, type MascotResponse } from "../api/gamification";

// 진화 단계 시각화 (이미지 첨부 전까지 이모지)
// 0=알, 1=부화 1단계, 2=2단계, 3=3단계, 4=4단계 완전체
const STAGE_FALLBACK_EMOJI = ["🥚", "🐣", "🐥", "🐤", "🌟"];
const STAGE_LABEL = ["알", "1단계", "2단계", "3단계", "완전체"];

// 진화 임계값
const HATCH_AT = 10;
const GOAL_CHECKINS = 200;
const GOAL_GRADIENT_FINAL = 180;

function progressColor(progress: number, isCharge: boolean): string {
  if (isCharge) return "#94A3B8";
  if (progress >= GOAL_GRADIENT_FINAL) return "#DC2626";  // 4단계 임박 빨강
  if (progress >= 100) return "#F59E0B";  // 3단계 도달 주황
  if (progress >= 40) return "#16A34A";   // 2단계 도달 초록
  return "#3B82F6";                        // 부화 전·후 초기 파랑
}

function nextThreshold(progress: number): { name: string; remaining: number } | null {
  if (progress < HATCH_AT) return { name: "부화", remaining: HATCH_AT - progress };
  if (progress < 40) return { name: "2단계", remaining: 40 - progress };
  if (progress < 100) return { name: "3단계", remaining: 100 - progress };
  if (progress < GOAL_CHECKINS) return { name: "4단계", remaining: GOAL_CHECKINS - progress };
  return null;  // 4단계 완료
}

export function EggWidget() {
  const [data, setData] = useState<MascotResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    gamificationApi
      .getMascot()
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex w-[280px] flex-col items-center justify-center rounded-md border border-border bg-bg p-[16px]">
        <p className="text-xs text-text-muted">로딩 중...</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex w-[280px] flex-col items-center justify-center gap-[8px] rounded-md border border-border bg-bg p-[16px]">
        <div className="flex h-[80px] w-[80px] items-center justify-center rounded-full bg-success/20">
          <span className="text-3xl">🥚</span>
        </div>
        <p className="text-sm font-bold text-text-primary">나의 헬스 알</p>
        <p className="text-xs text-text-muted">데이터 없음</p>
      </div>
    );
  }

  const egg = data.current_egg;
  const charge = data.charge_mode;
  const isCharge = charge.is_active;
  const stageIdx = Math.max(0, Math.min(egg.current_stage, 4));
  // 부화 이후엔 종 이모지, 그 전엔 알 이모지
  const emoji = egg.species && stageIdx >= 1 ? SPECIES_EMOJI[egg.species] : STAGE_FALLBACK_EMOJI[stageIdx];
  const label = STAGE_LABEL[stageIdx];
  const progress = egg.progress_checkins;
  const percentToGoal = Math.round((progress / GOAL_CHECKINS) * 100);
  const color = progressColor(progress, isCharge);
  const next = nextThreshold(progress);
  const isComplete = stageIdx === 4;

  return (
    <div className="flex w-[280px] flex-col items-center gap-[10px] rounded-md border border-border bg-bg p-[16px]">
      {/* 캐릭터 아이콘 */}
      <div
        className="relative flex h-[110px] w-[110px] items-center justify-center rounded-full"
        style={{ backgroundColor: `${color}20` }}
      >
        <span className="text-5xl">{emoji}</span>
        {isComplete && (
          <span className="absolute -top-1 -right-1 rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-bold text-yellow-700">
            ✨ 완전체
          </span>
        )}
      </div>

      {/* 헤더 — 캐릭터 이름 또는 알 상태 */}
      <div className="flex flex-col items-center gap-1">
        {egg.character_name ? (
          <>
            <p className="text-sm font-bold text-text-primary">{egg.character_name}</p>
            <span className="text-xs text-text-muted">{label}</span>
          </>
        ) : (
          <p className="text-sm font-bold text-text-primary">알 ({progress}/{HATCH_AT})</p>
        )}
      </div>

      {/* 진행률 바 */}
      <div className="w-full">
        <div className="h-2 w-full overflow-hidden rounded-full bg-bg-alt">
          <div
            className="h-full transition-all"
            style={{ width: `${percentToGoal}%`, backgroundColor: color }}
          />
        </div>
        <div className="mt-1 flex justify-between text-xs text-text-muted">
          <span>{progress} / {GOAL_CHECKINS} 체크인</span>
          <span style={{ color }} className="font-bold">{percentToGoal}%</span>
        </div>
      </div>

      {/* 다음 단계까지 강조 */}
      {!isCharge && !isComplete && next && (
        <p className="text-xs font-bold" style={{ color }}>
          {progress >= GOAL_GRADIENT_FINAL && "🔥 "}
          {next.name}까지 {next.remaining}번
        </p>
      )}
      {!isCharge && isComplete && (
        <p className="text-xs font-bold text-yellow-600">🌟 최종 진화 완료!</p>
      )}

      {/* 충전 모드 표시 */}
      {isCharge && (
        <Link
          to="/rest-mode"
          className="w-full rounded-md bg-slate-100 px-2 py-1.5 text-center hover:bg-slate-200"
        >
          <p className="text-xs font-bold text-slate-700">😴 쉬어가기 모드</p>
          <p className="text-xs text-slate-500">자세히 보기 →</p>
        </Link>
      )}
    </div>
  );
}
