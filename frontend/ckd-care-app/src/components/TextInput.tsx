interface TextInputProps {
  label?: string;
  placeholder?: string;
  className?: string;
  type?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  error?: string;
}

export function TextInput({
  label = "Label",
  placeholder = "입력하세요",
  className = "",
  type = "text",
  value,
  onChange,
  error,
}: TextInputProps) {
  return (
    <div className={`flex flex-col gap-[4px] ${className}`}>
      <label className="text-sm font-normal text-text-secondary">{label}</label>
      <div className={`flex h-[40px] items-center rounded-sm border bg-bg px-[12px] py-[8px] ${error ? "border-danger" : "border-border-strong"}`}>
        <input
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={onChange}
          className="w-full bg-transparent text-sm font-normal text-text-primary outline-none placeholder:text-text-muted"
        />
      </div>
      {error && <p className="text-xs text-danger">{error}</p>}
    </div>
  );
}
