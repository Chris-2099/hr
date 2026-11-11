import { useEffect, useState } from "react";
import { Bar, BarChart, Line, LineChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { api } from "../api";
import { Card, StatTile } from "../components/StatTile";
import { SERIES_HEX, GRID_HEX, AXIS_HEX } from "../palette";

interface RetentionData {
  attrition_trend_last_12mo: { period: string; voluntary: number; involuntary: number; total_attrition_rate: number }[];
  voluntary_involuntary: {
    voluntary: number;
    involuntary: number;
    regrettable: number;
    high_performer_attrition: number;
    leadership_attrition: number;
  };
  segmentation: {
    by_department: Record<string, number>;
    by_location: Record<string, number>;
    by_tenure_band: Record<string, number>;
  };
  flight_risk_indicators: { employees_high_pto_usage: number; active_headcount: number };
}

function toRows(obj: Record<string, number>) {
  return Object.entries(obj).map(([name, value]) => ({ name, value }));
}

export default function Retention() {
  const [data, setData] = useState<RetentionData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get<RetentionData>("/api/dashboard/retention").then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="error-banner">{error}</div>;
  if (!data) return <div className="loading">Loading…</div>;

  const v = data.voluntary_involuntary;

  return (
    <div>
      <div className="page-header">
        <h2>Retention &amp; Flight Risk</h2>
        <p>Where could we lose critical talent, and which areas carry retention risk?</p>
      </div>

      <div className="kpi-grid">
        <StatTile label="Voluntary Attrition" value={v.voluntary} />
        <StatTile label="Involuntary Attrition" value={v.involuntary} />
        <StatTile label="Regrettable Attrition" value={v.regrettable} deltaTone={v.regrettable > 5 ? "bad" : undefined} />
        <StatTile label="High Performer Attrition" value={v.high_performer_attrition} deltaTone={v.high_performer_attrition > 0 ? "bad" : "good"} />
        <StatTile label="Leadership Attrition" value={v.leadership_attrition} />
        <StatTile
          label="High PTO Usage (flight risk)"
          value={`${data.flight_risk_indicators.employees_high_pto_usage} / ${data.flight_risk_indicators.active_headcount}`}
        />
      </div>

      <div className="card-grid">
        <Card title="Total Attrition Rate" subtitle="Monthly, trailing 12 months">
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={data.attrition_trend_last_12mo}>
              <CartesianGrid stroke={GRID_HEX} vertical={false} />
              <XAxis dataKey="period" tick={{ fontSize: 11, fill: AXIS_HEX }} axisLine={{ stroke: GRID_HEX }} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: AXIS_HEX }} axisLine={false} tickLine={false} width={36} unit="%" />
              <Tooltip />
              <Line type="monotone" dataKey="total_attrition_rate" stroke={SERIES_HEX[7]} strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Attrition by Department">
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={toRows(data.segmentation.by_department)} layout="vertical" margin={{ left: 16 }}>
              <CartesianGrid stroke={GRID_HEX} horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 11, fill: AXIS_HEX }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: AXIS_HEX }} axisLine={false} tickLine={false} width={90} />
              <Tooltip />
              <Bar dataKey="value" fill={SERIES_HEX[0]} radius={[0, 4, 4, 0]} barSize={14} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Attrition by Tenure Band">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={toRows(data.segmentation.by_tenure_band)}>
              <CartesianGrid stroke={GRID_HEX} vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: AXIS_HEX }} axisLine={{ stroke: GRID_HEX }} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: AXIS_HEX }} axisLine={false} tickLine={false} width={30} />
              <Tooltip />
              <Bar dataKey="value" fill={SERIES_HEX[4]} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Attrition by Location">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={toRows(data.segmentation.by_location)}>
              <CartesianGrid stroke={GRID_HEX} vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: AXIS_HEX }} axisLine={{ stroke: GRID_HEX }} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: AXIS_HEX }} axisLine={false} tickLine={false} width={30} />
              <Tooltip />
              <Bar dataKey="value" fill={SERIES_HEX[2]} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>
    </div>
  );
}
