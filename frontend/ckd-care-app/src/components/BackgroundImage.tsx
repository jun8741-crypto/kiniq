import { useEffect, useState } from "react";

interface Props {
  proficiency: number; // 1=잔디, 2=산, 3=헬스, 4=지옥
}

/**
 * 숙련도 배경 — public/backgrounds/bg_proficiency{N}.png 우선,
 * 실패 시 .svg fallback, 그것도 실패 시 색 그라데이션.
 *
 * PNG 1장만 받아도 작동 (나머지는 SVG로 자동 fallback).
 */
export function BackgroundImage({ proficiency }: Props) {
  const safe = Math.max(1, Math.min(proficiency, 4));
  // PNG → SVG → 색 그라데이션 fallback chain
  const [ext, setExt] = useState<"png" | "svg" | null>("png");

  // proficiency가 바뀌면 PNG부터 다시 시도
  useEffect(() => {
    setExt("png");
  }, [safe]);

  if (ext === null) {
    // 둘 다 없으면 색 그라데이션
    const fallback: Record<number, string> = {
      1: "linear-gradient(180deg, #BBF7D0 0%, #4ADE80 100%)",
      2: "linear-gradient(180deg, #DBEAFE 0%, #86EFAC 100%)",
      3: "linear-gradient(180deg, #475569 0%, #1E293B 100%)",
      4: "radial-gradient(circle at 50% 60%, #F97316 0%, #7F1D1D 100%)",
    };
    return <div className="absolute inset-0" style={{ background: fallback[safe] }} />;
  }

  return (
    <img
      src={`/backgrounds/bg_proficiency${safe}.${ext}`}
      alt=""
      className="absolute inset-0 h-full w-full object-cover"
      onError={() => setExt(ext === "png" ? "svg" : null)}
    />
  );
}
