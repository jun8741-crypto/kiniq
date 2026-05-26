import { useEffect, useState } from "react";
import { Coins, Sparkles, Flame, Award, Egg } from "lucide-react";
import type { CheckInResponse } from "../api/challenge";
import { SPECIES_EMOJI, SPECIES_LABEL, type CharacterSpecies } from "../api/gamification";

interface Props {
  result: CheckInResponse | null;
  onClose: () => void;
}

/**
 * 체크인 직후 보상·이벤트를 한 번에 보여주는 모달.
 *
 * 우선순위: 부화 > 럭키 > 스트릭 보너스 > 스테이지 보너스 > Goal 알림 > 기본 보상.
 */
export function CheckinResultModal({ result, onClose }: Props) {
  const [confetti, setConfetti] = useState<{ x: number; y: number; rot: number; color: string }[]>([]);

  useEffect(() => {
    if (!result) return;
    const award = result.award;
    const egg = result.egg;
    const shouldConfetti = !!(award?.lucky || egg?.hatched || egg?.stage_milestone);
    if (!shouldConfetti) return;
    // 60개 컨페티 생성
    const colors = ["#F59E0B", "#10B981", "#3B82F6", "#EC4899", "#8B5CF6"];
    const pieces = Array.from({ length: 60 }, () => ({
      x: 40 + Math.random() * 20,
      y: -10 + Math.random() * 20,
      rot: Math.random() * 360,
      color: colors[Math.floor(Math.random() * colors.length)],
    }));
    setConfetti(pieces);
  }, [result]);

  if (!result) return null;

  const award = result.award;
  const egg = result.egg;
  const hatched = egg?.hatched;
  const species = egg?.species as CharacterSpecies | null | undefined;
  const characterName = egg?.character_name;

  // 메인 헤드라인 결정
  let title = "체크인 완료!";
  let subtitle = "";
  let mainIcon = <Coins size={48} className="text-amber-500" />;
  let hatchedBig: React.ReactNode = null;

  if (hatched && species) {
    title = `🎉 ${SPECIES_LABEL[species]} 부화!`;
    subtitle = characterName ? `'${characterName}' 가 태어났어요.` : "새 알이 자동으로 시작됩니다.";
    mainIcon = <Egg size={48} className="text-rose-500" />;
    hatchedBig = <div className="text-7xl">{SPECIES_EMOJI[species]}</div>;
  } else if (hatched) {
    title = "🎉 알 부화!";
    subtitle = `${egg?.new_egg_no}번째 알이 시작됩니다.`;
    mainIcon = <Egg size={64} className="text-rose-500" />;
  } else if (award?.lucky) {
    title = "✨ 럭키 체크인!";
    subtitle = "포인트가 두 배로 적립됐어요.";
    mainIcon = <Sparkles size={48} className="text-amber-500" />;
  } else if (egg?.stage_milestone) {
    title = `🥚 알 ${egg.stage_milestone}% 달성!`;
    subtitle = `다음 단계로 성장 중!`;
    mainIcon = <Award size={48} className="text-rose-500" />;
  } else if (award?.streak_milestone) {
    title = `🔥 연속 ${award.streak_milestone}일 달성!`;
    subtitle = "꾸준함이 빛나는 순간입니다.";
    mainIcon = <Flame size={48} className="text-orange-500" />;
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
      onClick={onClose}
    >
      {/* 컨페티 */}
      {confetti.map((c, i) => (
        <span
          key={i}
          className="confetti-piece pointer-events-none absolute h-2 w-2"
          style={{
            left: `${c.x}%`,
            top: `${c.y}%`,
            backgroundColor: c.color,
            transform: `rotate(${c.rot}deg)`,
            animationDelay: `${i * 30}ms`,
          }}
        />
      ))}

      <div
        className="relative w-full max-w-md rounded-lg bg-bg p-6 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex flex-col items-center gap-3 text-center">
          {hatchedBig ?? <div className="rounded-full bg-amber-50 p-4">{mainIcon}</div>}
          <h2 className="text-xl font-bold text-text-primary">{title}</h2>
          {subtitle && <p className="text-sm text-text-secondary">{subtitle}</p>}
        </div>

        {/* 적립 내역 */}
        {award && (
          <div className="mt-6 space-y-2 rounded-md border border-border bg-bg-alt p-4">
            <RewardRow label="체크인" amount={award.base} />
            {award.lucky && <RewardRow label="럭키 ×2" amount={award.lucky_extra} highlight />}
            {award.streak_bonus > 0 && (
              <RewardRow label={`스트릭 ${award.streak_milestone}일 보너스`} amount={award.streak_bonus} highlight />
            )}
            {egg && egg.stage_bonus > 0 && (
              <RewardRow label={`알 ${egg.stage_milestone}% 보너스`} amount={egg.stage_bonus} highlight />
            )}
            {award.full_participation && (
              <RewardRow label="풀 참여 보너스" amount={award.full_participation_bonus} highlight />
            )}
            <div className="border-t border-border pt-2">
              <RewardRow label="합계" amount={award.total + (egg?.stage_bonus ?? 0)} bold />
            </div>
          </div>
        )}

        {/* Goal Gradient 알림 */}
        {egg?.goal_90_just_alerted && (
          <div className="mt-4 rounded-md bg-red-50 px-3 py-2 text-center text-sm font-bold text-red-700">
            🔥 진행률 90% 도달! 부화까지 10번만 남았어요.
          </div>
        )}
        {egg?.goal_70_just_alerted && !egg.goal_90_just_alerted && (
          <div className="mt-4 rounded-md bg-amber-50 px-3 py-2 text-center text-sm font-bold text-amber-700">
            ⏰ 진행률 70% 도달! 부화까지 30번 남았어요.
          </div>
        )}

        <button
          onClick={onClose}
          className="mt-6 w-full rounded-md bg-accent py-2 text-sm font-bold text-bg hover:bg-accent/90"
        >
          확인
        </button>
      </div>
    </div>
  );
}

function RewardRow({
  label,
  amount,
  highlight = false,
  bold = false,
}: {
  label: string;
  amount: number;
  highlight?: boolean;
  bold?: boolean;
}) {
  return (
    <div className="flex items-center justify-between">
      <span className={`text-sm ${bold ? "font-bold text-text-primary" : "text-text-secondary"}`}>{label}</span>
      <span
        className={`text-sm ${bold ? "text-lg font-bold text-accent" : highlight ? "font-bold text-amber-600" : "text-text-primary"}`}
      >
        +{amount}pt
      </span>
    </div>
  );
}
