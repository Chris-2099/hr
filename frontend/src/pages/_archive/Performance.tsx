import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { api } from "../api";
import { Card, StatTile } from "../components/StatTile";
import { SERIES_HEX, GRID_HEX, AXIS_HEX } from "../palette";

interface PerformanceData {
  rating_distribution: Record<string, number>;
  high_performer_pct: number;
  low_performer_pct: number;
  promotions_ytd: number;
  promotion_rate_pct: number;
  manager_effectiveness: {
    manager_name: string;
    team_size: number;
    team_attrition_pct: number;
    avg_rating_score: number;
  }[];
}

const RATING_ORDER = ["Low", "Meets", "Exceeds", "High Performer"];

export default function Performance() {
  const [data, setData] = useState<PerformanceData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get<PerformanceData>("/api/dashboard/performance").then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="error-banner">{error}</div>;
  if (!data) return <div className="loading">Loading…</div>;

  const ratingRows = RATING_ORDER.map((name) => ({ name, value: data.rating_distribution[name] ?? 0 }));

  return (
    <div>
      <div className="page-header">
        <h2>Performance &amp; Productivity</h2>
        <p>Do we have enough top talent, and which leaders create the strongest outcomes?</p>
      </div>

      <div className="kpi-grid">
        <StatTile label="High Performer %" value={`${data.high_performer_pct}%`} deltaTone="good" />
        <StatTile label="Low Performer %" value={`${data.low_performer_pct}%`} deltaTone={data.low_performer_pct > 10 ? "bad" : undefined} />
        <StatTile label="Promotions (YTD)" value={data.promotions_ytd} />
        <StatTile label="Promotion Rate" value={`${data.promotion_rate_pct}%`} />
      </div>

      <div className="card-grid">
        <Card title="Performance Rating Distribution" subtitle="Most recent review period per employee">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={ratingRows}>
              <CartesianGrid stroke={GRID_HEX} vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: AXIS_HEX }} axisLine={{ stroke: GRID_HEX }} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: AXIS_HEX }} axisLine={false} tickLine={false} width={30} />
              <Tooltip />
              <Bar dataKey="value" fill={SERIES_HEX[0]} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card title="Manager Effectiveness" subtitle="Managers with 3+ direct reports, sorted by team attrition">
          <table className="data-table">
            <thead>
              <tr>
                <th>Manager</th>
                <th>Team Size</th>
                <th>Team Attrition</th>
                <th>Avg Rating</th>
              </tr>
            </thead>
            <tbody>
              {data.manager_effectiveness.map((m) => (
                <tr key={m.manager_name}>
                  <td>{m.manager_name}</td>
                  <td>{m.team_size}</td>
                  <td>{m.team_attrition_pct}%</td>
                  <td>{m.avg_rating_score}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </div>
    </div>
  );
}
