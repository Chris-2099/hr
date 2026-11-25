import type { LucideIcon } from "lucide-react";

type KpiCardProps = {
  label: string;
  value: string | number;
  hint?: string;
  icon?: LucideIcon;
  accent?: "indigo" | "emerald" | "amber" | "rose";
};

const ACCENT_CLASSES: Record<NonNullable<KpiCardProps["accent"]>, string> = {
  indigo: "bg-indigo-50 text-indigo-600",
  emerald: "bg-emerald-50 text-emerald-600",
  amber: "bg-amber-50 text-amber-600",
  rose: "bg-rose-50 text-rose-600",
};

export default function KpiCard({ label, value, hint, icon: Icon, accent = "indigo" }: KpiCardProps) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md">
      <div className="flex items-start justify-between">
        <div>
          <div className="text-sm font-medium text-slate-500">{label}</div>
          <div className="mt-1 text-3xl font-semibold tracking-tight text-slate-900">{value}</div>
          {hint && <div className="mt-1 text-xs text-slate-400">{hint}</div>}
        </div>
        {Icon && (
          <span className={`flex h-10 w-10 items-center justify-center rounded-xl ${ACCENT_CLASSES[accent]}`}>
            <Icon size={20} />
          </span>
        )}
      </div>
    </div>
  );
}
