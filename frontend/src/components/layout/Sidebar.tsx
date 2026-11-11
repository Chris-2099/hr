import {
  BarChart3,
  BriefcaseBusiness,
  ChartColumn,
  HeartHandshake,
  LayoutDashboard,
  TrendingUp,
  UserMinus,
  Users,
  type LucideIcon,
} from 'lucide-react'
import { NavLink } from 'react-router-dom'
import { useAuth } from '../../AuthContext'

interface NavItem {
  id: string
  label: string
  path: string
  icon: LucideIcon
  roles?: string[] // omitted = visible to every role
}

const NAV_ITEMS: NavItem[] = [
  { id: 'executive', label: 'Executive Snapshot', path: '/', icon: LayoutDashboard },
  { id: 'talent-acquisition', label: 'Talent Acquisition', path: '/talent-acquisition', icon: BriefcaseBusiness },
  { id: 'retention', label: 'Retention & Flight Risk', path: '/retention', icon: UserMinus },
  { id: 'performance', label: 'Performance', path: '/performance', icon: TrendingUp },
  { id: 'engagement', label: 'Engagement', path: '/engagement', icon: HeartHandshake },
  {
    id: 'compensation',
    label: 'Compensation',
    path: '/compensation',
    icon: ChartColumn,
    roles: ['admin', 'executive', 'hr_business_partner'],
  },
]

const RECORDS_ITEMS: NavItem[] = [{ id: 'employees', label: 'Employee Directory', path: '/employees', icon: Users }]

const POWERBI_ITEMS: NavItem[] = [
  { id: 'powerbi', label: 'Embedded Report', path: '/powerbi', icon: BarChart3, roles: ['admin', 'executive'] },
]

interface SidebarProps {
  collapsed: boolean
}

function NavSection({ label, items, collapsed, role }: { label: string; items: NavItem[]; collapsed: boolean; role: string }) {
  const visible = items.filter((item) => !item.roles || item.roles.includes(role))
  if (visible.length === 0) return null

  return (
    <div className="space-y-1">
      {!collapsed && (
        <p className="px-3 pb-1 pt-3 text-[11px] font-semibold uppercase tracking-wide text-slate-400">{label}</p>
      )}
      {visible.map((item) => {
        const Icon = item.icon
        return (
          <NavLink
            key={item.id}
            to={item.path}
            end={item.path === '/'}
            title={collapsed ? item.label : undefined}
            className={({ isActive }) =>
              `group flex items-center rounded-lg transition-colors ${
                collapsed ? 'justify-center px-2 py-2.5' : 'gap-3 px-3 py-2.5'
              } ${
                isActive ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <Icon
                  className={`h-5 w-5 shrink-0 ${isActive ? 'text-indigo-600' : 'text-slate-500 group-hover:text-slate-700'}`}
                  strokeWidth={1.75}
                />
                <span
                  className={`overflow-hidden whitespace-nowrap text-sm font-medium transition-all duration-300 ${
                    collapsed ? 'w-0 opacity-0' : 'w-auto opacity-100'
                  }`}
                >
                  {item.label}
                </span>
              </>
            )}
          </NavLink>
        )
      })}
    </div>
  )
}

export function Sidebar({ collapsed }: SidebarProps) {
  const { user, devInfo, switchDevUser } = useAuth()
  if (!user) return null

  return (
    <aside
      className={`fixed bottom-0 left-0 top-14 z-30 flex flex-col border-r border-slate-200 bg-white shadow-lg transition-[width] duration-300 ease-in-out md:shadow-none ${
        collapsed ? 'w-[68px]' : 'w-64'
      }`}
    >
      <div className={`flex h-16 items-center border-b border-slate-100 ${collapsed ? 'justify-center px-2' : 'gap-3 px-4'}`}>
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-indigo-600 text-sm font-bold text-white">
          HR
        </div>
        <div className={`overflow-hidden transition-all duration-300 ${collapsed ? 'w-0 opacity-0' : 'w-auto opacity-100'}`}>
          <p className="whitespace-nowrap text-sm font-semibold text-slate-900">HR Platform</p>
          <p className="whitespace-nowrap text-xs text-slate-500">Workforce Intelligence</p>
        </div>
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto p-2">
        <NavSection label="Dashboards" items={NAV_ITEMS} collapsed={collapsed} role={user.role} />
        <NavSection label="Records" items={RECORDS_ITEMS} collapsed={collapsed} role={user.role} />
        <NavSection label="Power BI" items={POWERBI_ITEMS} collapsed={collapsed} role={user.role} />
      </nav>

      <div className={`border-t border-slate-100 p-3 ${collapsed ? 'flex justify-center' : 'space-y-2'}`}>
        {!collapsed && devInfo?.disable_auth && devInfo.users && (
          <select
            aria-label="Viewing as (login disabled)"
            value={user.email}
            onChange={(e) => switchDevUser(e.target.value)}
            className="w-full rounded-lg border border-slate-200 bg-slate-50 px-2 py-1.5 text-xs text-slate-700 outline-none focus:border-indigo-300"
          >
            {devInfo.users.map((u) => (
              <option key={u.email} value={u.email}>
                {u.full_name} — {u.role.replace(/_/g, ' ')}
              </option>
            ))}
          </select>
        )}
        {!collapsed && (
          <p className="truncate text-[11px] text-slate-400">
            {user.full_name} · {user.role.replace(/_/g, ' ')}
          </p>
        )}
      </div>
    </aside>
  )
}
