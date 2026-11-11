export function StatTile({
  label,
  value,
  delta,
  deltaTone,
}: {
  label: string;
  value: string | number;
  delta?: string;
  deltaTone?: "good" | "bad";
}) {
  return (
    <div className="kpi-tile">
      <div className="label">{label}</div>
      <div className="value">{value}</div>
      {delta && <div className={`delta ${deltaTone ?? ""}`}>{delta}</div>}
    </div>
  );
}

export function Card({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="card">
      <h3>{title}</h3>
      {subtitle && <p className="card-subtitle">{subtitle}</p>}
      {children}
    </div>
  );
}

export const SERIES_COLORS = [
  "var(--series-1)",
  "var(--series-2)",
  "var(--series-3)",
  "var(--series-4)",
  "var(--series-5)",
  "var(--series-6)",
  "var(--series-7)",
  "var(--series-8)",
];

export function Legend({ entries }: { entries: { label: string; color: string }[] }) {
  return (
    <div className="legend-row">
      {entries.map((e) => (
        <span key={e.label}>
          <span className="legend-dot" style={{ background: e.color }} />
          {e.label}
        </span>
      ))}
    </div>
  );
}
