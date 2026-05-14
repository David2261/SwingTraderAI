import { TrendingUp, Bolt, Clock3, Sparkles } from 'lucide-react'
import { Button } from '@/shared/ui/button'
import { PageHeader } from '@/shared/ui/page-header'
import { SectionCard } from '@/shared/ui/section-card'
import { AIInsightCard } from '@/shared/ui/ai-insight-card'
import { SignalBadge } from '@/shared/ui/signal-badge'
import { MarketHeatBadge } from '@/shared/ui/market-heat-badge'
import { StatCard } from '@/shared/ui/stat-card'
import { useDashboardAlerts, useDashboardExplainability, useDashboardHeatmap, useDashboardOverview, useDashboardSignals, useDashboardActions } from '@/features/dashboard/hooks/dashboard-hooks'

function formatCurrency(value: number) {
  return `$${value.toLocaleString('en-US', { maximumFractionDigits: 0 })}`
}

export function DashboardPage() {
  const overviewQuery = useDashboardOverview()
  const signalQuery = useDashboardSignals()
  const heatmapQuery = useDashboardHeatmap()
  const explainQuery = useDashboardExplainability()
  const alertsQuery = useDashboardAlerts()
  const actionsQuery = useDashboardActions()

  const overview = overviewQuery.data
  const signals = signalQuery.data ?? []
  const heatmap = heatmapQuery.data ?? []
  const explainability = explainQuery.data ?? []
  const alerts = alertsQuery.data ?? []
  const actions = actionsQuery.data ?? []

  return (
    <div className="space-y-8">
      <PageHeader
        title="AI Market Command Center"
        description="A premium terminal for real-time signals, portfolio insight, and AI-driven trade coaching."
      />

      <div className="grid gap-6 xl:grid-cols-[1.75fr_1fr]">
        <div className="space-y-6">
          <AIInsightCard
            title="AI Market Briefing"
            description="The system is tracking regime shifts across global crypto and equities."
            strength="High Conviction"
            score={overview?.confidence ?? 0}
          >
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="rounded-3xl border border-slate-800/80 bg-slate-950/70 p-4">
                <p className="text-sm text-slate-400">Regime</p>
                <p className="mt-2 text-2xl text-white">{overview?.regime ?? 'Loading'}</p>
              </div>
              <div className="rounded-3xl border border-slate-800/80 bg-slate-950/70 p-4">
                <p className="text-sm text-slate-400">Volatility</p>
                <p className="mt-2 text-2xl text-white">{overview?.volatility ?? 'Loading'}</p>
              </div>
            </div>
            <div className="mt-5 space-y-3">
              {(overview?.opportunities ?? []).map((item) => (
                <div key={item.symbol} className="rounded-3xl border border-slate-800/80 bg-slate-900/80 p-4">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <p className="text-sm text-slate-400">{item.symbol}</p>
                      <p className="mt-1 text-base font-semibold text-white">{item.reason}</p>
                    </div>
                    <div className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-200">Score {item.score}</div>
                  </div>
                </div>
              ))}
            </div>
          </AIInsightCard>

          <div className="grid gap-6 xl:grid-cols-2">
            <StatCard
              title="Total Equity"
              value={overview ? formatCurrency(overview.summary.total_value) : '—'}
              change={{ value: overview?.summary.day_change_percent ?? 0, label: 'daily' }}
              icon={<TrendingUp className="h-4 w-4" />}
              className="bg-slate-950/80"
            />
            <StatCard
              title="Daily PnL"
              value={overview ? formatCurrency(overview.summary.total_pnl) : '—'}
              change={{ value: overview?.summary.day_change_percent ?? 0, label: 'today' }}
              icon={<Bolt className="h-4 w-4" />}
              className="bg-slate-950/80"
            />
            <StatCard
              title="Open Positions"
              value={overview?.summary.positions ?? '—'}
              change={{ value: overview?.summary.win_rate ?? 0, label: 'win rate' }}
              icon={<Clock3 className="h-4 w-4" />}
              className="bg-slate-950/80"
            />
            <StatCard
              title="Win Rate"
              value={overview ? `${overview.summary.win_rate}%` : '—'}
              change={{ value: 2.6, label: 'weekly' }}
              icon={<Sparkles className="h-4 w-4" />}
              className="bg-slate-950/80"
            />
          </div>

          <SectionCard
            title="Watchlist Signals Feed"
            description="Stay ahead with live AI signals on your most important tickers."
          >
            <div className="space-y-4">
              {signals.map((signal) => (
                <div
                  key={signal.id}
                  className="group rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4 transition hover:-translate-y-0.5 hover:border-slate-600"
                >
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                      <p className="text-sm text-slate-400">{signal.ticker}</p>
                      <p className="text-lg font-semibold text-white">{signal.signal}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-xs uppercase text-slate-400">Confidence</span>
                      <div className="rounded-full bg-slate-800/90 px-3 py-1 text-sm font-semibold text-emerald-300">
                        {(signal.confidence * 100).toFixed(0)}%
                      </div>
                    </div>
                  </div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {signal.indicators.map((indicator) => (
                      <span key={indicator} className="rounded-full bg-slate-900/80 px-3 py-1 text-xs text-slate-300">
                        {indicator}
                      </span>
                    ))}
                  </div>
                  <p className="mt-3 text-sm text-slate-400">{signal.time}</p>
                </div>
              ))}
            </div>
          </SectionCard>
        </div>

        <div className="space-y-6">
          <SectionCard
            title="Market Heatmap"
            description="Quick sentiment snapshot for key instruments."
          >
            <div className="grid gap-4 sm:grid-cols-2">
              {heatmap.map((item) => (
                <div key={item.symbol} className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-sm text-slate-400">{item.symbol}</p>
                      <p className="mt-1 text-lg font-semibold text-white">{item.name}</p>
                    </div>
                    <MarketHeatBadge status={item.status as any} active={item.active} />
                  </div>
                  <p className="mt-4 text-xl font-semibold text-white">
                    {item.change > 0 ? '+' : ''}{item.change.toFixed(2)}%
                  </p>
                </div>
              ))}
            </div>
          </SectionCard>

          <SectionCard
            title="AI Explainability"
            description="Why the system flagged these signals."
          >
            <div className="space-y-4">
              {explainability.map((item) => (
                <div key={item.id} className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
                  <p className="font-semibold text-white">{item.title}</p>
                  <ul className="mt-3 space-y-2 text-sm text-slate-400">
                    {item.reasons.map((reason) => (
                      <li key={reason} className="flex items-start gap-2">
                        <span className="mt-1 h-2 w-2 rounded-full bg-emerald-300" />
                        <span>{reason}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </SectionCard>

          <SectionCard
            title="Recent Alerts"
            description="Watch for high-priority trade signals and AI warnings."
          >
            <div className="space-y-3">
              {alerts.map((alert) => (
                <div key={alert.id} className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="font-semibold text-white">{alert.label}</p>
                      <p className="text-sm text-slate-400">{alert.description}</p>
                    </div>
                    <span className="rounded-full bg-slate-900 px-3 py-1 text-xs uppercase tracking-[0.18em] text-slate-300">
                      {alert.severity}
                    </span>
                  </div>
                  <p className="mt-3 text-xs uppercase tracking-[0.18em] text-slate-500">{alert.time}</p>
                </div>
              ))}
            </div>
          </SectionCard>

          <SectionCard
            title="Quick Actions"
            description="Execute core workflows from the terminal."
            actions={
              <div className="hidden items-center gap-2 sm:flex">
                <TrendingUp className="h-4 w-4 text-white" />
                <span className="text-sm text-slate-400">Instant command set</span>
              </div>
            }
          >
            <div className="grid gap-3 sm:grid-cols-2">
              {actions.map((action) => (
                <Button key={action.id} variant={action.variant as any} className="h-14 w-full justify-between px-5 text-sm font-semibold">
                  <span>{action.label}</span>
                  <Bolt className="h-4 w-4" />
                </Button>
              ))}
            </div>
          </SectionCard>
        </div>
      </div>
    </div>
  )
}
