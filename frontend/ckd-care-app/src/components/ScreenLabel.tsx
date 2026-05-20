interface ScreenLabelProps {
  label: string;
  variant?: "default" | "danger";
}

export function ScreenLabel({ label, variant = "default" }: ScreenLabelProps) {
  return (
    <div
      className={`flex h-[32px] w-full items-center px-[16px] py-[8px] ${
        variant === "danger" ? "bg-danger" : "bg-accent"
      }`}
    >
      <span className="text-sm font-bold text-bg">{label}</span>
    </div>
  );
}
