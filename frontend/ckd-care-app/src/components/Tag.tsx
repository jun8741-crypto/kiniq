interface TagProps {
  label?: string;
  className?: string;
}

export function Tag({ label = "G2", className = "" }: TagProps) {
  return (
    <span
      className={`inline-flex items-center rounded-sm border border-border bg-bg-alt px-[8px] py-[4px] text-xs font-bold text-text-primary ${className}`}
    >
      {label}
    </span>
  );
}
