import { useEffect, useState } from "react";
import { api, ApiError } from "../api";
import { DashboardCarousel } from "../components/dashboards/DashboardCarousel";
import { KpiCard, type KpiMetric } from "../components/kpi/KpiCard";
import { DataTable, type DepartmentRow } from "../components/table/DataTable";

interface SummaryResponse {
  headcount: {
    total_active: number;
    fte: number;
    contractor: number;
    new_hires_ytd: number;
    terminations_ytd: number;
    net_growth_ytd: number;
    avg_tenure_years: number;
  };
  headcount_trend: { period: string; headcount: number }[];
  recruiting_snapshot: { open_requisitions: number; total_open_positions: number };
}

interface TalentAcquisitionResponse {
  pipeline: { pipeline_by_stage: Record<string, number> };
  time_metrics: { time_to_fill_trend_last_6mo: { period: string; avg_days: number | null }[] };
}

interface RetentionResponse {
  attrition_trend_last_12mo: { period: string; voluntary: number; involuntary: number; total_attrition_rate: number }[];
}

interface CompensationResponse {
  cost: { total_annualized_base: number; avg_compa_ratio: number };
  equity: { compression_risk_employees: number };
}

interface DepartmentBreakdownResponse {
  department_id: string;
  department_name: string;
  active_ftes: number;
  open_roles: number;
  turnover_rate_pct: number;
  avg_tenure_years: number;
  status: "Healthy" | "Watch" | "At Risk";
}

const FUNNEL_STAGE_ORDER = ["Screening", "Interview", "Offer", "Hired"];

function formatPeriod(period: string): string {
  const [year, month] = period.split("-");
  const d = new Date(Number(year), Number(month) - 1, 1);
  return d.toLocaleDateString("en-US", { month: "short", year: "numeric" });
}

export default function Summary() {
  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [talentAcquisition, setTalentAcquisition] = useState<TalentAcquisitionResponse | null>(null);
  const [retention, setRetention] = useState<RetentionResponse | null>(null);
  const [compensation, setCompensation] = useState<CompensationResponse | null>(null);
  const [departments, setDepartments] = useState<DepartmentBreakdownResponse[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      api.get<SummaryResponse>("/api/dashboard/summary"),
      api.get<TalentAcquisitionResponse>("/api/dashboard/talent-acquisition"),
      api.get<RetentionResponse>("/api/dashboard/retention"),
      api.get<DepartmentBreakdownResponse[]>("/api/dashboard/department-breakdown"),
    ])
      .then(([s, t, r, d]) => {
        setSummary(s);
        setTalentAcquisition(t);
        setRetention(r);
        setDepartments(d);
      })
      .catch((e) => setError(e instanceof ApiError ? e.message : "Failed to load dashboard data"));

    // Compensation is role-gated (admin/executive/hr_business_partner only);
    // a 403 here just means this viewer doesn't see that KPI, not an error.
    api
      .get<CompensationResponse>("/api/dashboard/compensation")
      .then(setCompensation)
      .catch(() => setCompensation(null));
  }, []);

  if (error) return <div className="error-banner">{error}</div>;
  if (!summary || !talentAcquisition || !retention || !departments) {
    return <div className="loading">Loading…</div>;
  }

  const h = summary.headcount;
  const latestAttrition = retention.attrition_trend_last_12mo[retention.attrition_trend_last_12mo.length - 1];

  const kpiMetrics: KpiMetric[] = [
    {
      id: "headcount",
      name: "Total Headcount",
      value: h.total_active.toLocaleString(),
      accent: "indigo",
      trends: [
        `FTE: ${h.fte} · Contractor: ${h.contractor}`,
        `New hires YTD: ${h.new_hires_ytd}`,
        `Net growth YTD: ${h.net_growth_ytd >= 0 ? "+" : ""}${h.net_growth_ytd}`,
      ],
    },
    {
      id: "attrition",
      name: "Monthly Attrition Rate",
      value: `${latestAttrition.total_attrition_rate}%`,
      accent: "rose",
      trends: [
        `As of ${formatPeriod(latestAttrition.period)}`,
        `Terminations YTD: ${h.terminations_ytd}`,
        `Avg tenure: ${h.avg_tenure_years} yrs`,
      ],
    },
    {
      id: "requisitions",
      name: "Open Requisitions",
      value: summary.recruiting_snapshot.open_requisitions.toLocaleString(),
      accent: "amber",
      trends: [`Total open positions: ${summary.recruiting_snapshot.total_open_positions}`],
    },
    ...(compensation
      ? [
          {
            id: "payroll",
            name: "Total Annualized Labor Cost",
            value: `$${(compensation.cost.total_annualized_base / 1_000_000).toFixed(1)}M`,
            accent: "emerald" as const,
            trends: [
              `Avg compa-ratio: ${compensation.cost.avg_compa_ratio}`,
              `Compression risk: ${compensation.equity.compression_risk_employees} employees`,
            ],
          },
        ]
      : []),
  ];

  const recruitingFunnel = FUNNEL_STAGE_ORDER.map((stage) => ({
    stage,
    count: talentAcquisition.pipeline.pipeline_by_stage[stage] ?? 0,
  }));

  const timeToFillTrend = talentAcquisition.time_metrics.time_to_fill_trend_last_6mo
    .filter((p) => p.avg_days !== null)
    .map((p) => ({ period: formatPeriod(p.period), avgDays: p.avg_days as number }));

  const turnoverTrend = retention.attrition_trend_last_12mo.map((p) => ({
    period: formatPeriod(p.period),
    voluntary: p.voluntary,
    involuntary: p.involuntary,
  }));

  const departmentRows: DepartmentRow[] = departments.map((d) => ({
    id: d.department_id,
    department: d.department_name,
    activeFtes: d.active_ftes,
    openRoles: d.open_roles,
    turnoverRatePct: d.turnover_rate_pct,
    avgTenureYears: d.avg_tenure_years,
    status: d.status,
  }));

  return (
    <div className="mx-auto flex w-full max-w-[1400px] flex-col gap-8">
      <div>
        <h1 className="text-xl font-semibold tracking-tight text-slate-900 sm:text-2xl">Executive Snapshot</h1>
        <p className="mt-1 text-sm text-slate-500">
          A one-page overview of organizational health: do we have the workforce to execute?
        </p>
      </div>

      <section aria-labelledby="highlights-heading">
        <h2 id="highlights-heading" className="mb-4 text-sm font-semibold uppercase tracking-wide text-slate-500">
          Highlights
        </h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {kpiMetrics.map((metric) => (
            <KpiCard key={metric.id} metric={metric} />
          ))}
        </div>
      </section>

      <DashboardCarousel
        headcountTrend={summary.headcount_trend.map((p) => ({ period: formatPeriod(p.period), headcount: p.headcount }))}
        recruitingFunnel={recruitingFunnel}
        turnoverTrend={turnoverTrend}
        timeToFillTrend={timeToFillTrend}
      />

      <DataTable rows={departmentRows} />
    </div>
  );
}
