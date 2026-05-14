import { ArrowUpRight, BarChart3, ChartPie, ShieldCheck } from 'lucide-react'
import { PageHeader } from '@/shared/ui/page-header'
import { SectionCard } from '@/shared/ui/section-card'
import { StatCard } from '@/shared/ui/stat-card'
import { usePortfolioPositions, usePortfolioSummary } from '@/features/portfolio/hooks/portfolio-hooks'

function formatCurrency(value: number) {
  return `$${value.toLocaleString('en-US', { maximumFractionDigits: 0 })}`
}

export function PortfolioPage() {
  const summaryQuery = usePortfolioSummary()
  const positionsQuery = usePortfolioPositions()
  const summary = summaryQuery.data
  const positions = positionsQuery.data ?? []

  return (
    <div className="space-y-8">
      <PageHeader
        title="Portfolio"
        description="Monitor allocation, risk, and PnL across open positions."
      />

      <div className="grid gap-6 xl:grid-cols-3">
        <StatCard
          title="Total Equity"
          value={summary ? formatCurrency(summary.total_value) : 'Loading'}
          change={{ value: summary?.day_change_percent ?? 0, label: 'daily' }}
          icon={<ChartPie className="h-4 w-4" />}
          className="bg-slate-950/80"
        />
        <StatCard
          title="Unrealized PnL"
          value={summary ? formatCurrency(summary.total_pnl) : 'Loading'}
          change={{ value: summary?.win_rate ?? 0, label: 'win rate' }}
          icon={<ArrowUpRight className="h-4 w-4" />}
          className="bg-slate-950/80"
        />
        <StatCard
          title="Risk Exposure"
          value={summary ? `${(summary.positions * 8).toFixed(0)}%` : 'Loading'}
          icon={<ShieldCheck className="h-4 w-4" />}
          className="bg-slate-950/80"
        />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.4fr_0.6fr]">
        <SectionCard
          title="Open Positions"
          description="Current holdings with entry, current price, and PnL details."
        >
          <div className="space-y-4">
            {positions.map((position) => {
              const gain = position.pnl >= 0
              return (
                <div key={position.id} className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4 transition hover:-translate-y-0.5">
                  <div className="flex flex-wrap items-center justify-between gap-4">
                    <div>
                      <p className="text-sm text-slate-400">{position.ticker.symbol}</p>
                      <p className="mt-1 text-lg font-semibold text-white">{position.ticker.name}</p>
                    </div>
                    <div className="rounded-full bg-slate-900 px-3 py-1 text-xs uppercase tracking-[0.18em] text-slate-300">
                      {position.allocation_percent?.toFixed(0)}% allocation
                    </div>
                  </div>
                  <div className="mt-4 grid gap-3 sm:grid-cols-3">
                    <div>
                      <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Entry</p>
                      <p className="mt-2 text-white">${position.avg_price.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Current</p>
                      <p className="mt-2 text-white">${position.current_price.toFixed(2)}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs uppercase tracking-[0.18em] text-slate-500">PnL</p>
                      <p className={gain ? 'mt-2 text-emerald-300' : 'mt-2 text-rose-300'}>
                        {gain ? '+' : ''}${position.pnl.toFixed(2)} ({gain ? '+' : ''}{position.pnl_percent.toFixed(2)}%)
                      </p>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </SectionCard>

        <SectionCard
          title="Portfolio Allocation"
          description="High-level exposure by strategy and sector."
        >
          <div className="space-y-4">
            <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
              {positions.map((position) => (
                <div key={position.id} className="mb-3 last:mb-0">
                  <div className="flex items-center justify-between text-sm text-slate-200">
                    <span>{position.ticker.symbol}</span>
                    <span>{position.allocation_percent?.toFixed(0)}%</span>
                  </div>
                  <div className="mt-2 h-2.5 overflow-hidden rounded-full bg-slate-800">
                    <div className="h-full rounded-full bg-gradient-to-r from-emerald-400 via-cyan-400 to-sky-400" style={{ width: `${position.allocation_percent ?? 0}%` }} />
                  </div>
                </div>
              ))}
            </div>
            <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
              <p className="text-sm text-slate-400">Best position</p>
              <p className="mt-2 text-lg font-semibold text-white">{positions[0]?.ticker.symbol ?? '—'} / {positions[0]?.ticker.name ?? '—'}</p>
              <p className="mt-1 text-sm text-slate-500">{positions[0] ? `${positions[0].pnl_percent.toFixed(2)}%` : '—'}</p>
            </div>
            <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
              <p className="text-sm text-slate-400">AI Risk Summary</p>
              <p className="mt-2 text-white">Core exposure remains balanced. Monitor overleveraged names and volatility around premium levels.</p>
            </div>
          </div>
        </SectionCard>
      </div>
    </div>
  )
}
