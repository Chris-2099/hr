import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { api } from "../api";
import { Card, StatTile } from "../components/StatTile";
import { SERIES_HEX, GRID_HEX, AXIS_HEX } from "../palette";

interface TAData {
  pipeline: {
    open_requisitions: number;
    avg_requisition_age_days: number;
    total_candidates_in_pipeline: number;
    candidates_per_opening: number;
    offer_acceptance_rate_pct: number;
    pipeline_by_stage: Record<string, number>;
  };
  time_metrics: { avg_time_to_fill_days: number; reqs_filled: number };
  quality: {
    new_hire_90day_retention_pct: number | null;
    new_hire_1yr_retention_pct: number | null;
    avg_hiring_manager_satisfaction: number;
    internal_hire_pct: number | null;
    applications_by_source_type: Record<string, number>;
  };
  recruiter_productivity: Record<string, number>;
}

function toRows(obj: Record<string, number>) {
  return Object.entries(obj).map(([name, value]) => ({ name, value }));
}

export default function TalentAcquisition() {
  const [data, setData] = useState<TAData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get<TAData>("/api/dashboard/talent-acquisition").then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="error-banner">{error}</div>;
  if (!data) return <div className="loading">Loading…</div>;

  return (
    <div>
      <div className="page-header">
        <h2>Talent Acquisition Effectiveness</h2>
        <p>Workforce supply and recruiting efficiency, sourced from Jobvite.</p>
      </div>

      <div className="kpi-grid">
        <StatTile label="Open Requisitions" value={data.pipeline.open_requisitions} />
        <StatTile label="Avg Requisition Age" value={`${data.pipeline.avg_requisition_age_days} days`} />
        <StatTile label="Candidates in Pipeline" value={data.pipeline.total_candidates_in_pipeline} />
        <StatTile label="Candidates / Opening" value={data.pipeline.candidates_per_opening} />
        <StatTile label="Offer Acceptance Rate" value={`${data.pipeline.offer_acceptance_rate_pct}%`} />
        <StatTile label="Avg Time to Fill" value={`${data.time_metrics.avg_time_to_fill_days} days`} />
        <StatTile
          label="90-Day New Hire Retention"
          value={data.quality.new_hire_90day_retention_pct != null ? `${data.quality.new_hire_90day_retention_pct}%` : "—"}
        />
        <StatTile
          label="Internal Hire %"
          value={data.quality.internal_hire_pct != null ? `${data.quality.internal_hire_pct}%` : "—"}
        />
      </div>

      <div className="card-grid">
        <Card title="Pipeline by Stage">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={toRows(data.pipeline.pipeline_by_stage)}>
              <CartesianGrid stroke={GRID_HEX} vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: AXIS_HEX }} axisLine={{ stroke: GRID_HEX }} tickLine={false} interval={0} angle={-20} textAnchor="end" height={50} />
              <YAxis tick={{ fontSize: 11, fill: AXIS_HEX }} axisLine={false} tickLine={false} width={30} />
              <Tooltip />
              <Bar dataKey="value" fill={SERIES_HEX[0]} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Applications by Source Type">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={toRows(data.quality.applications_by_source_type)} layout="vertical" margin={{ left: 16 }}>
              <CartesianGrid stroke={GRID_HEX} horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 11, fill: AXIS_HEX }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: AXIS_HEX }} axisLine={false} tickLine={false} width={110} />
              <Tooltip />
              <Bar dataKey="value" fill={SERIES_HEX[2]} radius={[0, 4, 4, 0]} barSize={16} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Open Requisitions by Recruiter" subtitle="Requisition count assigned, all statuses">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={toRows(data.recruiter_productivity)}>
              <CartesianGrid stroke={GRID_HEX} vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: AXIS_HEX }} axisLine={{ stroke: GRID_HEX }} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: AXIS_HEX }} axisLine={false} tickLine={false} width={30} />
              <Tooltip />
              <Bar dataKey="value" fill={SERIES_HEX[6]} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Hiring Quality">
          <table className="data-table">
            <tbody>
              <tr>
                <td>Avg Hiring Manager Satisfaction</td>
                <td>{data.quality.avg_hiring_manager_satisfaction} / 5</td>
              </tr>
              <tr>
                <td>1-Year New Hire Retention</td>
                <td>{data.quality.new_hire_1yr_retention_pct != null ? `${data.quality.new_hire_1yr_retention_pct}%` : "—"}</td>
              </tr>
              <tr>
                <td>Requisitions Filled (all time)</td>
                <td>{data.time_metrics.reqs_filled}</td>
              </tr>
            </tbody>
          </table>
        </Card>
      </div>
    </div>
  );
}
