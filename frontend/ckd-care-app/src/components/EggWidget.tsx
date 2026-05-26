import { useEffect, useState } from "react";
import { gamificationApi, type MascotResponse } from "../api/gamification";

const STAGE_EMOJI = ["🥚", "🥚", "🐣", "🐥", "🐤", "🎉"];
const STAGE_LABEL = ["", "1단계", "2단계", "3단계", "4단계", "부화!"];

function progressColor(percent: number, isCharge: boolean): string {
  if (isCharge) return "#94A3B8";
  if (percent >= 90) return "#DC2626";
  if (percent >= 70) return "#F59E0B";
  if (percent >= 50) return "#16A34A";
  return "#3B82F6";
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
        <p className="text-xs text-text-muted">알 로딩 중...</p>
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
  const stageIdx = Math.min(egg.current_stage, 5);
  const emoji = STAGE_EMOJI[stageIdx];
  const label = STAGE_LABEL[stageIdx];
  const percent = egg.progress_percent;
  const color = progressColor(percent, isCharge);

  return (
    <div className="flex w-[280px] flex-col items-center gap-[10px] rounded-md border border-border bg-bg p-[16px]">
      {/* 알 아이콘 */}
      <div
        className="relative flex h-[110px] w-[110px] items-center justify-center rounded-full"
        style={{ backgroundColor: `${color}20` }}
      >
        <span className="text-5xl">{emoji}</span>
        {data.legendary_unlocked && (
          <span className="absolute -top-1 -right-1 rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-bold text-yellow-700">
            ✨ 전설
          </span>
        )}
      </div>

      {/* 헤더 */}
      <div className="flex items-baseline gap-2">
        <p className="text-sm font-bold text-text-primary">{egg.egg_no}번째 알</p>
        <span className="text-xs text-text-muted">· {label}</span>
      </div>

      {/* 진행률 바 */}
      <div className="w-full">
        <div className="h-2 w-full overflow-hidden rounded-full bg-bg-alt">
          <div
            className="h-full transition-all"
            style={{ width: `${percent}%`, backgroundColor: color }}
          />
        </div>
        <div className="mt-1 flex justify-between text-xs text-text-muted">
          <span>{egg.progress_checkins} / 100 체크인</span>
          <span style={{ color }} className="font-bold">{percent}%</span>
        </div>
      </div>

      {/* Goal Gradient 강조 메시지 */}
      {!isCharge && percent >= 90 && (
        <p className="text-xs font-bold text-red-600">🔥 부화 임박! {100 - percent}번만 더!</p>
      )}
      {!isCharge && percent >= 70 && percent < 90 && (
        <p className="text-xs font-bold text-amber-600">⏰ 70% 도달! 부화까지 {100 - percent}번</p>
      )}

      {/* 충전 모드 표시 */}
      {isCharge && (
        <div className="w-full rounded-md bg-slate-100 px-2 py-1.5 text-center">
          <p className="text-xs font-bold text-slate-700">😴 쉬어가기 모드</p>
          <p className="text-xs text-slate-500">체크인 1번이면 정상으로 돌아와요</p>
        </div>
      )}
    </div>
  );
}
