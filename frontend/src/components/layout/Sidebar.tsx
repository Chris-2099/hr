import { NavLink } from "react-router-dom";
import {
  Home,
  LayoutDashboard,
  Users,
  Briefcase,
  TrendingDown,
  BarChart3,
  Heart,
  DollarSign,
  GitBranch,
  CalendarRange,
  GraduationCap,
  PieChart,
} from "lucide-react";

const DASHBOARD_ITEMS = [
  { to: "/executive-snapshot", label: "Executive Snapshot", icon: LayoutDashboard },
  { to: "/talent-acquisition", label: "Talent Acquisition", icon: Briefcase },
  { to: "/retention", label: "Retention & Flight Risk", icon: TrendingDown },
  { to: "/performance", label: "Performance & Productivity", icon: BarChart3 },
  { to: "/engagement", label: "Engagement & Org Health", icon: Heart },
  { to: "/compensation", label: "Compensation & Rewards", icon: DollarSign },
  { to: "/succession", label: "Succession Planning", icon: GitBranch },
  { to: "/workforce-planning", label: "Workforce Planning", icon: CalendarRange },
  { to: "/learning", label: "Learning & Capability", icon: GraduationCap },
];

const TOOL_ITEMS = [
  { to: "/employees", label: "Employees", icon: Users },
  { to: "/power-bi", label: "Power BI", icon: PieChart },
];

function NavItem({ to, label, icon: Icon }: { to: string; label: string; icon: typeof Home }) {
  return (
    <NavLink
      to={to}
      end={to === "/"}
      className={({ isActive }) =>
        `group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
          isActive
            ? "bg-indigo-600/15 text-white"
            : "text-slate-400 hover:bg-white/5 hover:text-slate-100"
        }`
      }
    >
      {({ isActive }: { isActive: boolean }) => (
        <>
          <span
            className={`flex h-7 w-7 items-center justify-center rounded-md transition-colors ${
              isActive ? "bg-indigo-500 text-white" : "bg-white/5 text-slate-400 group-hover:text-slate-200"
            }`}
          >
            <Icon size={15} />
          </span>
          {label}
        </>
      )}
    </NavLink>
  );
}

function SectionLabel({ children }: { children: string }) {
  return (
    <div className="px-3 pb-1 pt-4 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
      {children}
    </div>
  );
}

export default function Sidebar() {
  return (
    <nav className="flex h-full w-64 flex-col gap-0.5 overflow-y-auto border-r border-slate-800 bg-slate-900 p-3">
      <NavItem to="/" label="Home" icon={Home} />

      <SectionLabel>Dashboards</SectionLabel>
      {DASHBOARD_ITEMS.map((item) => (
        <NavItem key={item.to} {...item} />
      ))}

      <SectionLabel>Tools</SectionLabel>
      {TOOL_ITEMS.map((item) => (
        <NavItem key={item.to} {...item} />
      ))}
    </nav>
  );
}
