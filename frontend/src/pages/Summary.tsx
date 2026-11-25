import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { Users, Briefcase, UserPlus, CheckCircle2 } from "lucide-react";
import { api } from "../api";
import KpiCard from "../components/kpi/KpiCard";

type DashboardSummary = {
  active_headcount: number;
  open_requisitions: number;
  total_candidates: number;
  hires_to_date: number;
};

type Employee = { department_id: string };
type Department = { department_id: string; name: string };

export default function Summary() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [headcountByDept, setHeadcountByDept] = useState<{ name: string; headcount: number }[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void (async () => {
      try {
        const [summaryData, employees, departments] = await Promise.all([
          api.get<DashboardSummary>("/dashboard/summary"),
          api.get<Employee[]>("/employees"),
          api.get<Department[]>("/departments"),
        ]);
        setSummary(summaryData);

        const nameById = new Map(departments.map((d) => [d.department_id, d.name]));
        const counts = new Map<string, number>();
        for (const e of employees) {
          counts.set(e.department_id, (counts.get(e.department_id) ?? 0) + 1);
        }
        setHeadcountByDept(
          [...counts.entries()]
            .map(([id, headcount]) => ({ name: nameById.get(id) ?? id, headcount }))
            .sort((a, b) => b.headcount - a.headcount)
        );
      } catch {
        setError("Couldn't load dashboard data.");
      }
    })();
  }, []);

  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (!summary) return <p className="text-sm text-slate-500">Loading…</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-slate-900">Executive Snapshot</h1>
        <p className="mt-1 text-sm text-slate-500">A top-level view of workforce and recruiting health.</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard label="Active Headcount" value={summary.active_headcount} icon={Users} accent="indigo" />
        <KpiCard label="Open Requisitions" value={summary.open_requisitions} icon={Briefcase} accent="amber" />
        <KpiCard label="Total Candidates" value={summary.total_candidates} icon={UserPlus} accent="emerald" />
        <KpiCard label="Hires to Date" value={summary.hires_to_date} icon={CheckCircle2} accent="rose" />
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-sm font-semibold text-slate-700">Headcount by Department</h2>
        <ResponsiveContainer width="100%" height={340}>
          <BarChart data={headcountByDept} layout="vertical" margin={{ left: 24 }}>
            <CartesianGrid horizontal={false} stroke="#e2e8f0" />
            <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12, fill: "#64748b" }} />
            <YAxis type="category" dataKey="name" width={170} tick={{ fontSize: 12, fill: "#475569" }} />
            <Tooltip
              cursor={{ fill: "#f1f5f9" }}
              contentStyle={{ borderRadius: 12, border: "1px solid #e2e8f0", fontSize: 13 }}
            />
            <Bar dataKey="headcount" fill="#4f46e5" radius={[0, 6, 6, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
