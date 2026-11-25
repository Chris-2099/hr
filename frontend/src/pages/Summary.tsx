import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
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
      <h1 className="text-lg font-semibold text-slate-900">Executive Snapshot</h1>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard label="Active Headcount" value={summary.active_headcount} />
        <KpiCard label="Open Requisitions" value={summary.open_requisitions} />
        <KpiCard label="Total Candidates" value={summary.total_candidates} />
        <KpiCard label="Hires to Date" value={summary.hires_to_date} />
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h2 className="mb-4 text-sm font-medium text-slate-700">Headcount by Department</h2>
        <ResponsiveContainer width="100%" height={320}>
          <BarChart data={headcountByDept} layout="vertical" margin={{ left: 24 }}>
            <XAxis type="number" allowDecimals={false} />
            <YAxis type="category" dataKey="name" width={160} tick={{ fontSize: 12 }} />
            <Tooltip />
            <Bar dataKey="headcount" fill="#2563eb" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
