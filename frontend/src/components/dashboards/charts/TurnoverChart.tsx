import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

export interface TurnoverPoint {
  period: string
  voluntary: number
  involuntary: number
}

interface TurnoverChartProps {
  data: TurnoverPoint[]
}

export function TurnoverChart({ data }: TurnoverChartProps) {
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
        <XAxis dataKey="period" tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} />
        <YAxis tick={{ fill: '#64748b', fontSize: 11 }} axisLine={false} tickLine={false} width={32} allowDecimals={false} />
        <Tooltip
          contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }}
          formatter={(value) => [`${value} departures`, '']}
        />
        <Legend wrapperStyle={{ fontSize: 11, paddingTop: 4 }} iconType="circle" iconSize={8} />
        <Bar dataKey="voluntary" stackId="turnover" fill="#f43f5e" name="Voluntary" radius={[0, 0, 0, 0]} />
        <Bar dataKey="involuntary" stackId="turnover" fill="#fda4af" name="Involuntary" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
