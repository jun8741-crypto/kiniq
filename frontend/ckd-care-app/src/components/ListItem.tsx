import { Circle, ChevronRight, type LucideIcon } from "lucide-react";

interface ListItemProps {
  icon?: LucideIcon;
  title?: string;
  subtitle?: string;
  className?: string;
  onClick?: () => void;
}

export function ListItem({
  icon: Icon = Circle,
  title = "List Title",
  subtitle = "sub text",
  className = "",
  onClick,
}: ListItemProps) {
  return (
    <div
      className={`flex items-center gap-[12px] rounded-sm border border-border bg-bg p-[12px] cursor-pointer ${className}`}
      onClick={onClick}
    >
      <Icon size={20} className="shrink-0 text-text-secondary" />
      <div className="flex min-w-0 flex-1 flex-col gap-[2px]">
        <p className="truncate text-sm font-bold text-text-primary">{title}</p>
        <p className="truncate text-xs font-normal text-text-secondary">
          {subtitle}
        </p>
      </div>
      <ChevronRight size={18} className="shrink-0 text-text-secondary" />
    </div>
  );
}
