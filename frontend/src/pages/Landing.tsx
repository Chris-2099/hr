import { Link } from "react-router-dom";
import {
  LayoutDashboard,
  Briefcase,
  TrendingDown,
  BarChart3,
  Heart,
  DollarSign,
  GitBranch,
  CalendarRange,
  GraduationCap,
  ArrowRight,
  type LucideIcon,
} from "lucide-react";
import { useAuth } from "../AuthContext";

type ThemeCard = {
  to: string;
  title: string;
  description: string;
  icon: LucideIcon;
  accent: string;
};

const THEMES: ThemeCard[] = [
  {
    to: "/executive-snapshot",
    title: "Executive Snapshot",
    description: "Headcount, requisitions, and hiring at a glance.",
    icon: LayoutDashboard,
    accent: "bg-indigo-50 text-indigo-600",
  },
  {
    to: "/talent-acquisition",
    title: "Talent Acquisition",
    description: "Pipeline health, time-to-fill, and sourcing mix.",
    icon: Briefcase,
    accent: "bg-sky-50 text-sky-600",
  },
  {
    to: "/retention",
    title: "Retention & Flight Risk",
    description: "Attrition trends and who's at risk of leaving.",
    icon: TrendingDown,
    accent: "bg-rose-50 text-rose-600",
  },
  {
    to: "/performance",
    title: "Performance & Productivity",
    description: "Review cycles, ratings distribution, and goals.",
    icon: BarChart3,
    accent: "bg-violet-50 text-violet-600",
  },
  {
    to: "/engagement",
    title: "Engagement & Org Health",
    description: "Survey sentiment, belonging, and manager effectiveness.",
    icon: Heart,
    accent: "bg-pink-50 text-pink-600",
  },
  {
    to: "/compensation",
    title: "Compensation & Rewards",
    description: "Pay equity, compa-ratio, and benchmark comparisons.",
    icon: DollarSign,
    accent: "bg-emerald-50 text-emerald-600",
  },
  {
    to: "/succession",
    title: "Succession Planning",
    description: "Readiness for critical roles and leadership pipeline.",
    icon: GitBranch,
    accent: "bg-amber-50 text-amber-600",
  },
  {
    to: "/workforce-planning",
    title: "Workforce Planning",
    description: "Forecast vs. budget headcount by department.",
    icon: CalendarRange,
    accent: "bg-teal-50 text-teal-600",
  },
  {
    to: "/learning",
    title: "Learning & Capability",
    description: "Training completions and skill development.",
    icon: GraduationCap,
    accent: "bg-fuchsia-50 text-fuchsia-600",
  },
];

export default function Landing() {
  const { user } = useAuth();
  const firstName = user?.full_name.split(" ")[0];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-slate-900">
          Welcome{firstName ? `, ${firstName}` : ""}
        </h1>
        <p className="mt-2 text-sm text-slate-500">
          Nine dashboards, one view of workforce and organizational health. Pick a theme to dive in.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {THEMES.map(({ to, title, description, icon: Icon, accent }) => (
          <Link
            key={to}
            to={to}
            className="group flex flex-col rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md"
          >
            <span className={`flex h-10 w-10 items-center justify-center rounded-xl ${accent}`}>
              <Icon size={20} />
            </span>
            <h2 className="mt-4 text-sm font-semibold text-slate-900">{title}</h2>
            <p className="mt-1 flex-1 text-xs text-slate-500">{description}</p>
            <span className="mt-4 flex items-center gap-1 text-xs font-medium text-indigo-600 opacity-0 transition-opacity group-hover:opacity-100">
              Open <ArrowRight size={14} />
            </span>
          </Link>
        ))}
      </div>
    </div>
  );
}
