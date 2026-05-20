import { Activity } from "lucide-react";

interface ChartPlaceholderProps {
  title?: string;
  className?: string;
  height?: number;
}

export function ChartPlaceholder({
  title = "Chart Title",
  className = "",
  height = 200,
}: ChartPlaceholderProps) {
  return (
    <div
      className={`flex flex-col items-center justify-center gap-[8px] rounded-md border border-border-strong bg-placeholder p-[16px] ${className}`}
      style={{ height }}
    >
      <Activity size={32} className="text-text-secondary" />
      <p className="text-md font-bold text-text-secondary">{title}</p>
    </div>
  );
}
