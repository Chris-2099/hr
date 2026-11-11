import { ChevronLeft, ChevronRight } from 'lucide-react'
import { useRef } from 'react'
import { DashboardCard } from './DashboardCard'
import { HeadcountChart, type HeadcountPoint } from './charts/HeadcountChart'
import { RecruitingFunnelChart, type FunnelStage } from './charts/RecruitingFunnelChart'
import { TimeToFillChart, type TimeToFillPoint } from './charts/TimeToFillChart'
import { TurnoverChart, type TurnoverPoint } from './charts/TurnoverChart'

const SCROLL_AMOUNT = 436

interface DashboardCarouselProps {
  headcountTrend: HeadcountPoint[]
  recruitingFunnel: FunnelStage[]
  turnoverTrend: TurnoverPoint[]
  timeToFillTrend: TimeToFillPoint[]
}

export function DashboardCarousel({ headcountTrend, recruitingFunnel, turnoverTrend, timeToFillTrend }: DashboardCarouselProps) {
  const scrollerRef = useRef<HTMLDivElement>(null)

  const scroll = (direction: 'left' | 'right') => {
    const el = scrollerRef.current
    if (!el) return
    el.scrollBy({ left: direction === 'left' ? -SCROLL_AMOUNT : SCROLL_AMOUNT, behavior: 'smooth' })
  }

  return (
    <section aria-labelledby="dashboards-heading">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <h2 id="dashboards-heading" className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Dashboards
          </h2>
          <p className="mt-0.5 text-sm text-slate-600">Interactive views across workforce and talent pipelines</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => scroll('left')}
            aria-label="Scroll dashboards left"
            className="inline-flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-600 transition hover:bg-slate-50 hover:text-slate-900"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
          <button
            type="button"
            onClick={() => scroll('right')}
            aria-label="Scroll dashboards right"
            className="inline-flex h-8 w-8 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-600 transition hover:bg-slate-50 hover:text-slate-900"
          >
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div ref={scrollerRef} className="scrollbar-hide flex gap-4 overflow-x-auto pb-1 scroll-smooth">
        <DashboardCard title="Headcount Trajectory" subtitle="Active employees · trailing 13 months">
          <HeadcountChart data={headcountTrend} />
        </DashboardCard>
        <DashboardCard title="Recruiting Funnel" subtitle="Jobvite pipeline · current open reqs">
          <RecruitingFunnelChart data={recruitingFunnel} />
        </DashboardCard>
        <DashboardCard title="Turnover Mix" subtitle="Voluntary vs involuntary · departures per month">
          <TurnoverChart data={turnoverTrend} />
        </DashboardCard>
        <DashboardCard title="Time to Fill" subtitle="Average days from open to accept">
          <TimeToFillChart data={timeToFillTrend} />
        </DashboardCard>
      </div>
    </section>
  )
}
