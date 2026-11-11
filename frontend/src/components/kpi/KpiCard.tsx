import { useEffect, useState } from 'react'

export interface KpiMetric {
  id: string
  name: string
  value: string
  accent: 'indigo' | 'emerald' | 'amber' | 'rose'
  trends: string[]
}

const accentStyles: Record<KpiMetric['accent'], { bar: string; value: string; chip: string }> = {
  indigo: { bar: 'bg-indigo-500', value: 'text-slate-900', chip: 'text-indigo-700' },
  emerald: { bar: 'bg-emerald-500', value: 'text-slate-900', chip: 'text-emerald-700' },
  amber: { bar: 'bg-amber-500', value: 'text-slate-900', chip: 'text-amber-700' },
  rose: { bar: 'bg-rose-500', value: 'text-slate-900', chip: 'text-rose-700' },
}

interface KpiCardProps {
  metric: KpiMetric
}

export function KpiCard({ metric }: KpiCardProps) {
  const [trendIndex, setTrendIndex] = useState(0)
  const [animKey, setAnimKey] = useState(0)
  const styles = accentStyles[metric.accent]

  useEffect(() => {
    if (metric.trends.length <= 1) return
    const id = window.setInterval(() => {
      setTrendIndex((prev) => (prev + 1) % metric.trends.length)
      setAnimKey((prev) => prev + 1)
    }, 3200)
    return () => window.clearInterval(id)
  }, [metric.trends.length])

  return (
    <article className="relative overflow-hidden rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className={`absolute inset-y-0 left-0 w-1 ${styles.bar}`} />
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{metric.name}</p>
      <p className={`mt-2 text-3xl font-semibold tracking-tight ${styles.value}`}>{metric.value}</p>
      <div className="mt-3 h-5 overflow-hidden">
        <p key={animKey} className={`ticker-animate text-xs font-medium ${styles.chip}`}>
          {metric.trends[trendIndex]}
        </p>
      </div>
    </article>
  )
}
