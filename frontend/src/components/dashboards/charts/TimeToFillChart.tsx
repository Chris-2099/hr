import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

export interface TimeToFillPoint {
  period: string
  avgDays: number
}

interface TimeToFillChartProps {
  data: TimeToFillPoint[]
}

export function TimeToFillChart({ data }: TimeToFillChartProps) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
        <XAxis dataKey="period" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} width={32} unit="d" />
        <Tooltip
          contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }}
          formatter={(value) => [`${value} days`, 'Avg time to fill']}
        />
        <Line type="monotone" dataKey="avgDays" stroke="#059669" strokeWidth={2.5} dot={{ r: 3, fill: '#059669', strokeWidth: 0 }} activeDot={{ r: 5 }} />
      </LineChart>
    </ResponsiveContainer>
  )
}
