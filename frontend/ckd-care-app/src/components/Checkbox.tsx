interface CheckboxProps {
  label?: string;
  checked?: boolean;
  onChange?: (checked: boolean) => void;
}

export function Checkbox({
  label = "체크 항목",
  checked = false,
  onChange,
}: CheckboxProps) {
  return (
    <label className="flex items-center gap-[8px] cursor-pointer">
      <div
        className={`flex h-[18px] w-[18px] items-center justify-center rounded-sm border-[1.5px] border-accent ${
          checked ? "bg-accent" : "bg-bg"
        }`}
        onClick={() => onChange?.(!checked)}
      >
        {checked && (
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M2 6L5 9L10 3" stroke="white" strokeWidth="2" />
          </svg>
        )}
      </div>
      <span className="text-sm font-normal text-text-primary">{label}</span>
    </label>
  );
}
