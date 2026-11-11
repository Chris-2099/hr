import { useEffect, useState } from "react";
import { Bar, BarChart, Line, LineChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { api } from "../api";
import { Card, StatTile } from "../components/StatTile";
import { SERIES_HEX, GRID_HEX, AXIS_HEX } from "../palette";

interface EngagementData {
  engagement_trend: { period: string; participation_rate_pct: number; engagement_score: number }[];
  key_drivers_latest: Record<string, number>;
  sentiment_mix_latest: Record<string, number>;
  organizational_health: {
    open_employee_relations_cases: number;
    total_employee_relations_cases_ytd: number;
    avg_pto_utilization_pct: number;
    avg_absenteeism_days: number;
  };
}

function toRows(obj: Record<string, number>) {
  return Object.entries(obj).map(([name, value]) => ({ name: name.replace(/_/g, " "), value }));
}

export default function Engagement() {
  const [data, setData] = useState<EngagementData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get<EngagementData>("/api/dashboard/engagement").then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="error-banner">{error}</div>;
  if (!data) return <div className="loading">Loading…</div>;

  const latest = data.engagement_trend[data.engagement_trend.length - 1];
  const oh = data.organizational_health;

  return (
    <div>
      <div className="page-header">
        <h2>Engagement &amp; Organizational Health</h2>
        <p>HR's leading-indicator dashboard: are people engaged, and is burnout increasing?</p>
      </div>

      <div className="kpi-grid">
        <StatTile label="Latest Engagement Score" value={latest ? `${latest.engagement_score}` : "—"} />
        <StatTile label="Latest Participation Rate" value={latest ? `${latest.participation_rate_pct}%` : "—"} />
        <StatTile label="Open ER Cases" value={oh.open_employee_relations_cases} deltaTone={oh.open_employee_relations_cases > 5 ? "bad" : undefined} />
        <StatTile label="ER Cases (YTD)" value={oh.total_employee_relations_cases_ytd} />
        <StatTile label="Avg PTO Utilization" value={`${oh.avg_pto_utilization_pct}%`} />
        <StatTile label="Avg Absenteeism" value={`${oh.avg_absenteeism_days} days/mo`} />
      </div>

      <div className="card-grid">
        <Card title="Engagement Score Trend">
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={data.engagement_trend}>
              <CartesianGrid stroke={GRID_HEX} vertical={false} />
              <XAxis dataKey="period" tick={{ fontSize: 11, fill: AXIS_HEX }} axisLine={{ stroke: GRID_HEX }} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: AXIS_HEX }} axisLine={false} tickLine={false} width={30} domain={[0, 100]} />
              <Tooltip />
              <Line type="monotone" dataKey="engagement_score" stroke={SERIES_HEX[0]} strokeWidth={2} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Key Engagement Drivers" subtitle="Latest pulse survey">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={toRows(data.key_drivers_latest)} layout="vertical" margin={{ left: 16 }}>
              <CartesianGrid stroke={GRID_HEX} horizontal={false} />
              <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11, fill: AXIS_HEX }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: AXIS_HEX }} axisLine={false} tickLine={false} width={130} />
              <Tooltip />
              <Bar dataKey="value" fill={SERIES_HEX[2]} radius={[0, 4, 4, 0]} barSize={14} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Sentiment Mix" subtitle="Latest pulse survey">
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={toRows(data.sentiment_mix_latest)}>
              <CartesianGrid stroke={GRID_HEX} vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: AXIS_HEX }} axisLine={{ stroke: GRID_HEX }} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: AXIS_HEX }} axisLine={false} tickLine={false} width={30} />
              <Tooltip />
              <Bar dataKey="value" fill={SERIES_HEX[4]} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>
    </div>
  );
}
