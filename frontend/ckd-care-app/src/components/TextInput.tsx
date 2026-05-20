interface TextInputProps {
  label?: string;
  placeholder?: string;
  className?: string;
}

export function TextInput({
  label = "Label",
  placeholder = "입력하세요",
  className = "",
}: TextInputProps) {
  return (
    <div className={`flex flex-col gap-[4px] ${className}`}>
      <label className="text-sm font-normal text-text-secondary">{label}</label>
      <div className="flex h-[40px] items-center rounded-sm border border-border-strong bg-bg px-[12px] py-[8px]">
        <input
          type="text"
          placeholder={placeholder}
          className="w-full bg-transparent text-sm font-normal text-text-primary outline-none placeholder:text-text-muted"
        />
      </div>
    </div>
  );
}
