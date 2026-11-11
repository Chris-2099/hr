import { Bell, CircleHelp, LogOut, Menu, Search, UserRound } from 'lucide-react'
import { useAuth } from '../../AuthContext'

interface HeaderProps {
  onToggleSidebar: () => void
}

export function Header({ onToggleSidebar }: HeaderProps) {
  const { user, logout, devInfo } = useAuth()
  const authDisabled = import.meta.env.VITE_DISABLE_AUTH === 'true' || devInfo?.disable_auth === true
  return (
    <header className="fixed inset-x-0 top-0 z-40 flex h-14 items-center justify-between border-b border-slate-200 bg-white/95 px-4 backdrop-blur-sm">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onToggleSidebar}
          aria-label="Toggle sidebar"
          className="inline-flex h-9 w-9 items-center justify-center rounded-lg text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
        >
          <Menu className="h-5 w-5" strokeWidth={1.75} />
        </button>
        <div className="hidden sm:block">
          <p className="text-sm font-semibold tracking-tight text-slate-900">
            HR Workforce &amp; Org Health
          </p>
          <p className="text-xs text-slate-500">Dayforce · Jobvite · Power BI</p>
        </div>
      </div>

      <div className="flex items-center gap-1.5">
        <button
          type="button"
          aria-label="Search"
          className="inline-flex h-9 w-9 items-center justify-center rounded-lg text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
        >
          <Search className="h-4 w-4" strokeWidth={1.75} />
        </button>
        <button
          type="button"
          aria-label="Help"
          className="inline-flex h-9 w-9 items-center justify-center rounded-lg text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
        >
          <CircleHelp className="h-4 w-4" strokeWidth={1.75} />
        </button>
        <button
          type="button"
          aria-label="Notifications"
          className="relative inline-flex h-9 w-9 items-center justify-center rounded-lg text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
        >
          <Bell className="h-4 w-4" strokeWidth={1.75} />
        </button>
        {!authDisabled ? (
          <button
            type="button"
            aria-label={`Sign out (${user?.full_name ?? ""})`}
            title="Sign out"
            onClick={logout}
            className="ml-1 inline-flex h-9 w-9 items-center justify-center rounded-full bg-indigo-600 text-white shadow-sm transition hover:bg-rose-600"
          >
            <LogOut className="h-4 w-4" strokeWidth={1.75} />
          </button>
        ) : (
          <button
            type="button"
            aria-label="User profile"
            title={user?.full_name}
            className="ml-1 inline-flex h-9 w-9 items-center justify-center rounded-full bg-indigo-600 text-white shadow-sm"
          >
            <UserRound className="h-4 w-4" strokeWidth={1.75} />
          </button>
        )}
      </div>
    </header>
  )
}
