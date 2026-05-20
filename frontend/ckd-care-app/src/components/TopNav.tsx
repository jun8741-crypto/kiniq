import { User, Bell, LogOut, LayoutDashboard, Trophy } from "lucide-react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { notificationApi } from "../api/notification";

interface TopNavProps {
  brand?: string;
}

export function TopNav({ brand = "CKD CARE" }: TopNavProps) {
  const { logout, token } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    if (!token) return;
    notificationApi.list(true, 1).then((r) => setUnread(r.unread_count)).catch(() => {});
  }, [token, location.pathname]);

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
          className="relative flex h-[36px] w-[36px] items-center justify-center rounded-md text-text-secondary hover:bg-bg-alt"
        >
          <Bell size={20} />
          {unread > 0 && (
            <span className="absolute right-[4px] top-[4px] flex h-[16px] min-w-[16px] items-center justify-center rounded-full bg-danger px-[3px] text-[10px] font-bold text-bg">
              {unread > 99 ? "99+" : unread}
            </span>
          )}
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
