import { BarChart3, CircleDot, TrendingUp, Zap } from 'lucide-react'
import { PageHeader } from '@/shared/ui/page-header'
import { SectionCard } from '@/shared/ui/section-card'
import { StatCard } from '@/shared/ui/stat-card'
import { useAnalyticsPulse, useAnalyticsSnapshot, useAnalyticsSummary } from '@/features/analytics/hooks/analytics-hooks'

export function AnalyticsPage() {
  const summaryQuery = useAnalyticsSummary()
  const snapshotQuery = useAnalyticsSnapshot()
  const pulseQuery = useAnalyticsPulse()

  const summary = summaryQuery.data
  const snapshot = snapshotQuery.data ?? []
  const pulse = pulseQuery.data ?? []

  return (
    <div className="space-y-8">
      <PageHeader
        title="Analytics"
        description="A complete analytics workspace for signal distribution, volatility, and strategy performance."
      />

      <div className="grid gap-6 xl:grid-cols-4">
        <StatCard
          title="Win/Loss Ratio"
          value={summary ? `${summary.winRate}%` : 'Loading'}
          icon={<TrendingUp className="h-4 w-4" />}
          className="bg-slate-950/80"
        />
        <StatCard
          title="Model Confidence"
          value={summary ? `${(summary.avgConfidence * 100).toFixed(0)}%` : 'Loading'}
          icon={<Zap className="h-4 w-4" />}
          className="bg-slate-950/80"
        />
        <StatCard
          title="Volatility Index"
          value={summary ? summary.volatilityIndex : 'Loading'}
          icon={<CircleDot className="h-4 w-4" />}
          className="bg-slate-950/80"
        />
        <StatCard
          title="Signal Coverage"
          value={`${snapshot.length} assets`}
          icon={<BarChart3 className="h-4 w-4" />}
          className="bg-slate-950/80"
        />
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.4fr_0.6fr]">
        <SectionCard title="Signal Distribution" description="Heatmap view of active signals across the platform.">
          <div className="space-y-4">
            {summary?.signalDistribution.map((segment) => (
              <div key={segment.label} className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
                <div className="flex items-center justify-between gap-3">
                  <span className="text-sm text-slate-300">{segment.label}</span>
                  <span className="text-base font-semibold text-white">{segment.value}%</span>
                </div>
                <div className="mt-3 h-2 rounded-full bg-slate-800">
                  <div className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400" style={{ width: `${segment.value}%` }} />
                </div>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Volatility Analysis" description="AI confidence and trending market pulse.">
          <div className="space-y-4">
            {pulse.map((item) => (
              <div key={item.id} className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
                <div className="flex items-center justify-between gap-3">
                  <span className="text-sm text-slate-300">{item.label}</span>
                  <span className={`rounded-full px-3 py-1 text-xs font-semibold ${item.color}`}>{item.value}%</span>
                </div>
              </div>
            ))}
          </div>
        </SectionCard>
      </div>

      <SectionCard title="Strategy Performance" description="Preview the strongest and weakest recent signals.">
        <div className="grid gap-4 sm:grid-cols-2">
          {snapshot.map((item) => (
            <div key={item.id} className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-white">{item.symbol}</p>
                <span className={item.change_percent >= 0 ? 'text-emerald-300' : 'text-rose-300'}>
                  {(item.change_percent >= 0 ? '+' : '') + item.change_percent.toFixed(2)}%
                </span>
              </div>
              <p className="mt-3 text-sm text-slate-400">Market snapshot indicates a strong short-term bias.</p>
            </div>
          ))}
        </div>
      </SectionCard>
    </div>
  )
}
