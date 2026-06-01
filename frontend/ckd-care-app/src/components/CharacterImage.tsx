import { useState } from "react";
import type { CharacterSpecies } from "../api/gamification";
import { characterImagePath, SPECIES_EMOJI } from "../api/gamification";

interface Props {
  species: CharacterSpecies | null;
  stage: number; // 0=알, 1~4=캐릭터 단계
  size?: number; // 정사각 px
  emojiClass?: string; // 이모지 fallback 시 폰트 사이즈 클래스 (예: 'text-5xl')
}

/**
 * 캐릭터·알 이미지. public/characters/*.png 우선, 실패 시 이모지 fallback.
 * 일러스트 0장이어도 정상 동작.
 */
export function CharacterImage({ species, stage, size = 110, emojiClass = "text-5xl" }: Props) {
  const [imageOk, setImageOk] = useState(true);
  const src = characterImagePath(species, stage);
  const safeStage = Math.max(0, Math.min(stage, 4));
  const fallbackEmoji = stage === 0
    ? "🥚"
    : (species ? SPECIES_EMOJI[species] : ["🥚", "🐣", "🐥", "🐤", "🌟"][safeStage]);

  if (!src || !imageOk) {
    return <span className={emojiClass}>{fallbackEmoji}</span>;
  }

  return (
    <img
      src={src}
      alt={species ? `${species} stage${safeStage}` : "egg"}
      width={size}
      height={size}
      className="object-contain"
      onError={() => setImageOk(false)}
    />
  );
}
