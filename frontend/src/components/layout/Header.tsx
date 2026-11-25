import { LogOut } from "lucide-react";
import { useAuth } from "../../AuthContext";

export default function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="flex h-14 items-center justify-between border-b border-slate-200 bg-white px-6">
      <span className="text-sm font-semibold text-slate-900">
        HR Workforce & Org Health Dashboard
      </span>
      {user && (
        <div className="flex items-center gap-4">
          <div className="text-right text-sm">
            <div className="font-medium text-slate-900">{user.full_name}</div>
            <div className="text-xs capitalize text-slate-500">{user.role.replace(/_/g, " ")}</div>
          </div>
          <button
            onClick={logout}
            title="Sign out"
            className="rounded-md p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-900"
          >
            <LogOut size={18} />
          </button>
        </div>
      )}
    </header>
  );
}
