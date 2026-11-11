import { Search } from 'lucide-react'
import { useMemo, useState } from 'react'

export interface DepartmentRow {
  id: string
  department: string
  activeFtes: number
  openRoles: number
  turnoverRatePct: number
  avgTenureYears: number
  status: 'Healthy' | 'Watch' | 'At Risk'
}

interface DataTableProps {
  rows: DepartmentRow[]
}

const statusStyles: Record<DepartmentRow['status'], string> = {
  Healthy: 'bg-emerald-50 text-emerald-700 ring-emerald-600/20',
  Watch: 'bg-amber-50 text-amber-700 ring-amber-600/20',
  'At Risk': 'bg-rose-50 text-rose-700 ring-rose-600/20',
}

export function DataTable({ rows }: DataTableProps) {
  const [query, setQuery] = useState('')

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return rows
    return rows.filter((row) => row.department.toLowerCase().includes(q) || row.status.toLowerCase().includes(q))
  }, [rows, query])

  return (
    <section aria-labelledby="detail-grid-heading" className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="flex flex-col gap-3 border-b border-slate-100 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 id="detail-grid-heading" className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Additional Data
          </h2>
          <p className="mt-0.5 text-sm text-slate-600">Department-level workforce detail</p>
        </div>
        <label className="relative block w-full sm:w-72">
          <span className="sr-only">Search departments</span>
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search department or status…"
            className="w-full rounded-lg border border-slate-200 bg-slate-50 py-2 pl-9 pr-3 text-sm text-slate-900 placeholder:text-slate-400 outline-none transition focus:border-indigo-300 focus:bg-white focus:ring-2 focus:ring-indigo-100"
          />
        </label>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead>
            <tr className="border-b border-slate-100 bg-slate-50/80 text-xs font-semibold uppercase tracking-wide text-slate-500">
              <th className="px-5 py-3 font-semibold">Department</th>
              <th className="px-5 py-3 font-semibold">Active FTEs</th>
              <th className="px-5 py-3 font-semibold">Open Roles</th>
              <th className="px-5 py-3 font-semibold">Turnover Rate</th>
              <th className="px-5 py-3 font-semibold">Avg Tenure</th>
              <th className="px-5 py-3 font-semibold">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filtered.map((row) => (
              <tr key={row.id} className="transition hover:bg-slate-50/80">
                <td className="px-5 py-3.5 font-medium text-slate-900">{row.department}</td>
                <td className="px-5 py-3.5 tabular-nums text-slate-700">{row.activeFtes.toLocaleString()}</td>
                <td className="px-5 py-3.5 tabular-nums text-slate-700">{row.openRoles}</td>
                <td className="px-5 py-3.5 tabular-nums text-slate-700">{row.turnoverRatePct.toFixed(1)}%</td>
                <td className="px-5 py-3.5 tabular-nums text-slate-700">{row.avgTenureYears.toFixed(1)} yrs</td>
                <td className="px-5 py-3.5">
                  <span className={`inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium ring-1 ring-inset ${statusStyles[row.status]}`}>
                    {row.status}
                  </span>
                </td>
              </tr>
            ))}
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-5 py-10 text-center text-sm text-slate-500">
                  No departments match "{query}".
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </section>
  )
}
