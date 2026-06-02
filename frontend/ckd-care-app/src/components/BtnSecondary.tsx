interface BtnSecondaryProps {
  label?: string;
  onClick?: () => void;
  className?: string;
  height?: number;
}

export function BtnSecondary({
  label = "Secondary",
  onClick,
  className = "",
  height,
}: BtnSecondaryProps) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center justify-center rounded-md border border-border-strong bg-bg px-[16px] py-[12px] text-sm font-normal text-text-primary ${className}`}
      style={height ? { height } : undefined}
    >
      {label}
    </button>
  );
}
