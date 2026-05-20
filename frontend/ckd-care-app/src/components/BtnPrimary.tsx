interface BtnPrimaryProps {
  label?: string;
  onClick?: () => void;
  className?: string;
  height?: number;
}

export function BtnPrimary({
  label = "Primary",
  onClick,
  className = "",
  height,
}: BtnPrimaryProps) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center justify-center rounded-md bg-accent px-[16px] py-[12px] text-sm font-bold text-bg ${className}`}
      style={height ? { height } : undefined}
    >
      {label}
    </button>
  );
}
