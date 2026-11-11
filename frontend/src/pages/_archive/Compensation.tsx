import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { api } from "../api";
import { Card, StatTile } from "../components/StatTile";
import { SERIES_HEX, GRID_HEX, AXIS_HEX } from "../palette";

interface CompensationData {
  cost: {
    total_annualized_base: number;
    avg_base_salary: number;
    avg_compa_ratio: number;
    cost_by_department: Record<string, number>;
  };
  equity: {
    avg_salary_by_gender: Record<string, number>;
    avg_salary_by_race_ethnicity: Record<string, number>;
    compression_risk_employees: number;
  };
}

function toRows(obj: Record<string, number>) {
  return Object.entries(obj).map(([name, value]) => ({ name, value: Math.round(value) }));
}

export default function Compensation() {
  const [data, setData] = useState<CompensationData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get<CompensationData>("/api/dashboard/compensation").then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="error-banner">{error}</div>;
  if (!data) return <div className="loading">Loading…</div>;

  return (
    <div>
      <div className="page-header">
        <h2>Compensation &amp; Total Rewards</h2>
        <p>Are pay practices competitive, and where are pay risks emerging?</p>
      </div>

      <div className="kpi-grid">
        <StatTile label="Total Annualized Base" value={`$${(data.cost.total_annualized_base / 1_000_000).toFixed(2)}M`} />
        <StatTile label="Avg Base Salary" value={`$${Math.round(data.cost.avg_base_salary).toLocaleString()}`} />
        <StatTile label="Avg Compa-Ratio" value={data.cost.avg_compa_ratio} />
        <StatTile
          label="Compression Risk (compa &lt; 0.85)"
          value={data.equity.compression_risk_employees}
          deltaTone={data.equity.compression_risk_employees > 10 ? "bad" : undefined}
        />
      </div>

      <div className="card-grid">
        <Card title="Avg Salary by Gender" subtitle="Pay equity check">
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={toRows(data.equity.avg_salary_by_gender)}>
              <CartesianGrid stroke={GRID_HEX} vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: AXIS_HEX }} axisLine={{ stroke: GRID_HEX }} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: AXIS_HEX }} axisLine={false} tickLine={false} width={50} />
              <Tooltip formatter={(v) => `$${Number(v).toLocaleString()}`} />
              <Bar dataKey="value" fill={SERIES_HEX[0]} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Avg Salary by Race/Ethnicity" subtitle="Pay equity check">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={toRows(data.equity.avg_salary_by_race_ethnicity)} layout="vertical" margin={{ left: 16 }}>
              <CartesianGrid stroke={GRID_HEX} horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 10, fill: AXIS_HEX }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 10, fill: AXIS_HEX }} axisLine={false} tickLine={false} width={150} />
              <Tooltip formatter={(v) => `$${Number(v).toLocaleString()}`} />
              <Bar dataKey="value" fill={SERIES_HEX[6]} radius={[0, 4, 4, 0]} barSize={14} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Labor Cost by Department">
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={toRows(data.cost.cost_by_department)}>
              <CartesianGrid stroke={GRID_HEX} vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: AXIS_HEX }} axisLine={{ stroke: GRID_HEX }} tickLine={false} interval={0} angle={-30} textAnchor="end" height={60} />
              <YAxis tick={{ fontSize: 11, fill: AXIS_HEX }} axisLine={false} tickLine={false} width={50} tickFormatter={(v) => `${Math.round(v / 1000)}k`} />
              <Tooltip formatter={(v) => `$${Number(v).toLocaleString()}`} />
              <Bar dataKey="value" fill={SERIES_HEX[1]} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>
    </div>
  );
}
