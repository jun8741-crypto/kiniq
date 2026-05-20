import { User, Bell } from "lucide-react";

interface TopNavProps {
  brand?: string;
}

export function TopNav({ brand = "CKD CARE" }: TopNavProps) {
  return (
    <nav className="flex h-[56px] w-full items-center justify-between border-b border-border bg-bg px-[16px] py-[12px]">
      <span className="text-lg font-bold text-text-primary">{brand}</span>
      <div className="flex items-center gap-[12px]">
        <User size={24} className="text-text-primary" />
        <Bell size={20} className="text-text-primary" />
      </div>
    </nav>
  );
}
