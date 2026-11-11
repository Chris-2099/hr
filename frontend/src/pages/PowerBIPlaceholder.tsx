import { BarChart3 } from 'lucide-react'

interface PowerBIPlaceholderProps {
  title: string
  subtitle: string
}

/**
 * Route + nav entry exist; the actual Power BI embed does not yet (no
 * workspace/report published, no MSAL wiring here - that lives on the
 * separate /powerbi route, see pages/PowerBIEmbed.tsx). This is
 * intentionally just a layout placeholder for the charter's other 5
 * dashboard themes until each gets either a real embedded report or a
 * custom-built page.
 */
export function PowerBIPlaceholder({ title, subtitle }: PowerBIPlaceholderProps) {
  return (
    <div className="mx-auto flex w-full max-w-[1400px] flex-col gap-8">
      <div>
        <h1 className="text-xl font-semibold tracking-tight text-slate-900 sm:text-2xl">{title}</h1>
        <p className="mt-1 text-sm text-slate-500">{subtitle}</p>
      </div>

      <div className="flex min-h-[420px] flex-col items-center justify-center gap-3 rounded-xl border border-dashed border-slate-300 bg-white/60 p-10 text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-indigo-50 text-indigo-600">
          <BarChart3 className="h-6 w-6" strokeWidth={1.75} />
        </div>
        <p className="text-sm font-medium text-slate-700">Power BI report not connected yet</p>
        <p className="max-w-sm text-xs text-slate-500">
          This page is ready for an embedded Power BI report (workspace + report id, delegated sign-in) once a
          semantic model with RLS is published here.
        </p>
      </div>
    </div>
  )
}
