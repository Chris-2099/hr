import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Users,
  Briefcase,
  TrendingDown,
  BarChart3,
  Heart,
  DollarSign,
  PieChart,
} from "lucide-react";

const NAV_ITEMS = [
  { to: "/", label: "Executive Snapshot", icon: LayoutDashboard },
  { to: "/employees", label: "Employees", icon: Users },
  { to: "/talent-acquisition", label: "Talent Acquisition", icon: Briefcase },
  { to: "/retention", label: "Retention & Flight Risk", icon: TrendingDown },
  { to: "/performance", label: "Performance", icon: BarChart3 },
  { to: "/engagement", label: "Engagement", icon: Heart },
  { to: "/compensation", label: "Compensation", icon: DollarSign },
  { to: "/power-bi", label: "Power BI", icon: PieChart },
];

export default function Sidebar() {
  return (
    <nav className="flex h-full w-60 flex-col gap-1 border-r border-slate-200 bg-white p-3">
      {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === "/"}
          className={({ isActive }) =>
            `flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
              isActive
                ? "bg-blue-50 text-blue-700"
                : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
            }`
          }
        >
          <Icon size={18} />
          {label}
        </NavLink>
      ))}
    </nav>
  );
}
