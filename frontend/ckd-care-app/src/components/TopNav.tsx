import { User, Bell, LogOut, LayoutDashboard, Trophy } from "lucide-react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

interface TopNavProps {
  brand?: string;
}

export function TopNav({ brand = "CKD CARE" }: TopNavProps) {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  function handleLogout() {
    logout();
    navigate("/");
  }

  const navItems = [
    { to: "/dashboard", icon: LayoutDashboard, label: "대시보드" },
    { to: "/challenge", icon: Trophy, label: "챌린지" },
  ];

  return (
    <nav className="flex h-[56px] w-full items-center justify-between border-b border-border bg-bg px-[16px] py-[12px]">
      <div className="flex items-center gap-[24px]">
        <Link to="/dashboard" className="text-lg font-bold text-text-primary">
          {brand}
        </Link>
        <div className="flex items-center gap-[4px]">
          {navItems.map(({ to, icon: Icon, label }) => (
            <Link
              key={to}
              to={to}
              className={`flex items-center gap-[6px] rounded-md px-[10px] py-[6px] text-sm transition-colors ${
                location.pathname === to
                  ? "bg-accent text-bg font-bold"
                  : "text-text-secondary hover:bg-bg-alt"
              }`}
            >
              <Icon size={16} />
              {label}
            </Link>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-[4px]">
        <Link
          to="/notifications"
          className="flex h-[36px] w-[36px] items-center justify-center rounded-md text-text-secondary hover:bg-bg-alt"
        >
          <Bell size={20} />
        </Link>
        <Link
          to="/mypage"
          className="flex h-[36px] w-[36px] items-center justify-center rounded-md text-text-secondary hover:bg-bg-alt"
        >
          <User size={20} />
        </Link>
        <button
          onClick={handleLogout}
          className="flex h-[36px] w-[36px] items-center justify-center rounded-md text-text-secondary hover:bg-bg-alt"
          title="로그아웃"
        >
          <LogOut size={20} />
        </button>
      </div>
    </nav>
  );
}
