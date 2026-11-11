import { type ReactNode } from 'react'

interface DashboardCardProps {
  title: string
  subtitle?: string
  children: ReactNode
}

export function DashboardCard({ title, subtitle, children }: DashboardCardProps) {
  return (
    <article className="flex w-[420px] shrink-0 flex-col rounded-xl border border-slate-200 bg-white shadow-sm">
      <header className="border-b border-slate-100 px-5 py-4">
        <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
        {subtitle ? <p className="mt-0.5 text-xs text-slate-500">{subtitle}</p> : null}
      </header>
      <div className="flex-1 px-3 pb-4 pt-2">{children}</div>
    </article>
  )
}
