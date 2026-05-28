import { useEffect, useState } from "react";
import { challengeApi, type HeatmapResponse } from "../api/challenge";

const DAY_LABELS = ["월", "화", "수", "목", "금", "토", "일"];

function colorForCount(count: number, max: number): string {
  if (count === 0) return "#E5E7EB"; // 회색 (체크인 없음)
  // 4단계 농도 (GitHub 잔디 스타일)
  const ratio = max > 0 ? count / max : 0;
  if (ratio <= 0.25) return "#BBF7D0";
  if (ratio <= 0.5) return "#86EFAC";
  if (ratio <= 0.75) return "#4ADE80";
  return "#16A34A";
}

export function HeatmapWidget() {
  const [data, setData] = useState<HeatmapResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    challengeApi
      .heatmap(26)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="rounded-md border border-border bg-bg p-4">
        <p className="text-sm text-text-muted">로딩 중...</p>
      </div>
    );
  }
  if (!data || data.days.length === 0) {
    return (
      <div className="rounded-md border border-border bg-bg p-4">
        <p className="text-sm font-bold text-text-primary">챌린지 잔디 (26주)</p>
        <p className="mt-2 text-xs text-text-muted">아직 체크인 기록이 없어요.</p>
      </div>
    );
  }

  // 일자별 데이터를 주x요일 그리드로 변환 (주 시작 = 월요일)
  // days 배열은 주 시작 월요일부터 시작하므로 7개씩 자르면 됨
  const weeks: { date: string; count: number }[][] = [];
  for (let i = 0; i < data.days.length; i += 7) {
    weeks.push(data.days.slice(i, i + 7));
  }

  const totalCheckins = data.days.reduce((sum, d) => sum + d.count, 0);

  return (
    <div className="rounded-md border border-border bg-bg p-4">
      <div className="mb-3 flex items-center justify-between">
        <p className="text-sm font-bold text-text-primary">챌린지 잔디 ({data.weeks}주)</p>
        <p className="text-xs text-text-muted">
          누적 {totalCheckins}회 · 최고 {data.max_count}회/일
        </p>
      </div>

      <div className="flex gap-[6px]">
        {/* 요일 라벨 (왼쪽) */}
        <div className="flex flex-col justify-between py-[2px]">
          {DAY_LABELS.map((d, i) => (
            <span
              key={d}
              className="h-[12px] text-[9px] text-text-muted"
              style={{ visibility: i % 2 === 0 ? "visible" : "hidden" }}
            >
              {d}
            </span>
          ))}
        </div>

        {/* 잔디 그리드 (가로 = 주, 세로 = 요일) */}
        <div className="flex flex-1 gap-[3px] overflow-x-auto">
          {weeks.map((week, wi) => (
            <div key={wi} className="flex flex-col gap-[3px]">
              {week.map((day) => (
                <div
                  key={day.date}
                  className="h-[12px] w-[12px] rounded-[2px]"
                  style={{ backgroundColor: colorForCount(day.count, data.max_count) }}
                  title={`${day.date}: ${day.count}회`}
                />
              ))}
              {/* 빈 칸 채우기 (마지막 주가 7일 안 될 때) */}
              {Array.from({ length: 7 - week.length }).map((_, i) => (
                <div key={`empty-${i}`} className="h-[12px] w-[12px]" />
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* 범례 */}
      <div className="mt-3 flex items-center justify-end gap-[6px] text-[10px] text-text-muted">
        <span>적게</span>
        {[0, 0.25, 0.5, 0.75, 1].map((r, i) => (
          <div
            key={i}
            className="h-[10px] w-[10px] rounded-[2px]"
            style={{ backgroundColor: colorForCount(r * (data.max_count || 1), data.max_count || 1) }}
          />
        ))}
        <span>많이</span>
      </div>
    </div>
  );
}
