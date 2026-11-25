import { LogOut } from "lucide-react";
import { useAuth } from "../../AuthContext";

function initials(fullName: string) {
  const parts = fullName.trim().split(/\s+/);
  return (parts[0]?.[0] ?? "").concat(parts.length > 1 ? parts[parts.length - 1][0] : "").toUpperCase();
}

export default function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="flex h-16 shrink-0 items-center justify-between border-b border-slate-200 bg-white/80 px-6 backdrop-blur">
      <div className="flex items-center gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-sm font-bold text-white">
          H
        </div>
        <span className="text-sm font-semibold tracking-tight text-slate-900">
          HR Workforce &amp; Org Health
        </span>
      </div>
      {user && (
        <div className="flex items-center gap-3">
          <div className="hidden text-right sm:block">
            <div className="text-sm font-medium leading-tight text-slate-900">{user.full_name}</div>
            <div className="text-xs capitalize leading-tight text-slate-500">
              {user.role.replace(/_/g, " ")}
            </div>
          </div>
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-900 text-xs font-semibold text-white">
            {initials(user.full_name)}
          </div>
          <button
            onClick={logout}
            title="Sign out"
            className="rounded-lg p-2 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-900"
          >
            <LogOut size={18} />
          </button>
        </div>
      )}
    </header>
  );
}
