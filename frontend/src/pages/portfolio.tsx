import { ArrowUpRight, ArrowDownRight, TrendingUp, ShieldCheck } from 'lucide-react'

import {
  GlassCard,
  SectionHeader,
  LivePulseIndicator,
} from '@/shared/ui'

import { usePortfolioPositions, usePortfolioSummary } from '@/features/portfolio/hooks/portfolio-hooks'

function formatCurrency(value: number): string {
  return `$${value.toLocaleString('en-US', { maximumFractionDigits: 0 })}`
}

export function PortfolioPage() {
  const summaryQuery = usePortfolioSummary()
  const positionsQuery = usePortfolioPositions()

  const summary = summaryQuery.data
  const positions = positionsQuery.data ?? []

  // Sorted copies for best/worst performers
  const sortedByPnL = [...positions].sort((a, b) => b.pnl_percent - a.pnl_percent)
  const bestPosition = sortedByPnL[0]
  const worstPosition = sortedByPnL[sortedByPnL.length - 1]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Портфель</h1>
        <p className="text-slate-400 mt-1">
          Анализ позиций, распределения и рисков в режиме реального времени.
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid gap-6 sm:grid-cols-3">
        <GlassCard>
          <div className="p-6">
            <p className="text-sm text-slate-400">Общий капитал</p>
            <div className="mt-3 flex items-baseline justify-between">
              <p className="text-3xl font-bold text-white">
                {summary ? formatCurrency(summary.total_value) : '—'}
              </p>
              <p
                className={`text-sm font-semibold flex items-center gap-1 ${
                  (summary?.day_change_percent ?? 0) >= 0 ? 'text-emerald-400' : 'text-rose-400'
                }`}
              >
                {(summary?.day_change_percent ?? 0) >= 0 ? (
                  <ArrowUpRight className="h-4 w-4" />
                ) : (
                  <ArrowDownRight className="h-4 w-4" />
                )}
                {(summary?.day_change_percent ?? 0) >= 0 ? '+' : ''}
                {summary?.day_change_percent ?? 0}%
              </p>
            </div>
          </div>
        </GlassCard>

        <GlassCard>
          <div className="p-6">
            <p className="text-sm text-slate-400">Нереализованный P&L</p>
            <div className="mt-3 flex items-baseline justify-between">
              <p className="text-3xl font-bold text-emerald-400">
                {summary ? formatCurrency(summary.total_pnl) : '—'}
              </p>
              <p className="text-sm font-semibold text-emerald-300">
                {summary?.win_rate ?? 0}% процент побед
              </p>
            </div>
          </div>
        </GlassCard>

        <GlassCard>
          <div className="p-6">
            <p className="text-sm text-slate-400">Открытые позиции</p>
            <div className="mt-3 flex items-baseline justify-between">
              <p className="text-3xl font-bold text-white">{positions.length}</p>
              <p className="text-sm font-semibold text-slate-400">Avg ~32% each</p>
            </div>
          </div>
        </GlassCard>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.65fr_1fr]">
        {/* Open Positions */}
        <GlassCard>
          <div className="p-6">
            <SectionHeader
              title="Открытые позиции"
              description={`${positions.length} активных позиций`}
              action={<TrendingUp className="h-4 w-4 text-slate-400" />}
            />

            <div className="mt-6 space-y-4">
              {positions.length === 0 ? (
                <p className="text-slate-400 py-8 text-center">Нет открытых позиций</p>
              ) : (
                positions.map((position) => {
                  const isGain = position.pnl >= 0

                  return (
                    <div
                      key={position.id}
                      className="rounded-2xl bg-slate-900/50 border border-slate-800 p-5 hover:border-slate-700 transition"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-3">
                          <h4 className="font-bold text-lg">{position.ticker.symbol}</h4>
                          <LivePulseIndicator active={isGain} size="sm" />
                        </div>

                        <span
                          className={`text-xs font-medium px-3 py-1 rounded-full ${
                            isGain
                              ? 'bg-emerald-900/60 text-emerald-300'
                              : 'bg-rose-900/60 text-rose-300'
                          }`}
                        >
                          {position.allocation_percent}%
                        </span>
                      </div>

                      <p className="text-sm text-slate-500 mt-1">{position.ticker.name}</p>

                      <div className="grid grid-cols-3 gap-4 mt-5 text-sm">
                        <div>
                          <p className="text-slate-500 text-xs">Quantity</p>
                          <p className="font-semibold mt-1">
                            {position.quantity.toFixed(position.quantity < 1 ? 4 : 2)}
                          </p>
                        </div>
                        <div>
                          <p className="text-slate-500 text-xs">Avg Entry</p>
                          <p className="font-semibold mt-1">
                            ${position.avg_price.toFixed(2)}
                          </p>
                        </div>
                        <div>
                          <p className="text-slate-500 text-xs">Текущий</p>
                          <p className="font-semibold mt-1">
                            ${position.current_price.toFixed(2)}
                          </p>
                        </div>
                      </div>

                      <div className="mt-5 pt-4 border-t border-slate-800 flex justify-between">
                        <div>
                          <p className="text-xs text-slate-500">P&L</p>
                          <p className={`font-bold text-base ${isGain ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {isGain ? '+' : ''}{formatCurrency(position.pnl)}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-xs text-slate-500">Возвращаться</p>
                          <p className={`font-bold text-base ${isGain ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {isGain ? '+' : ''}{position.pnl_percent.toFixed(2)}%
                          </p>
                        </div>
                      </div>
                    </div>
                  )
                })
              )}
            </div>
          </div>
        </GlassCard>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Allocation */}
          <GlassCard>
            <div className="p-6">
              <SectionHeader title="Распределение" description="По весу позиции" />
              <div className="mt-6 space-y-5">
                {positions.map((position) => (
                  <div key={position.id}>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="font-medium">{position.ticker.symbol}</span>
                      <span className="text-slate-400">{position.allocation_percent}%</span>
                    </div>
                    <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full"
                        style={{ width: `${position.allocation_percent}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </GlassCard>

          {/* Performance */}
          <GlassCard>
            <div className="p-6">
              <SectionHeader title="Performance" description="Top & bottom performers" />
              <div className="mt-6 space-y-4">
                {bestPosition && (
                  <div className="rounded-2xl bg-emerald-950/50 border border-emerald-900/50 p-4">
                    <p className="text-xs text-emerald-400">Лучший performer</p>
                    <p className="text-lg font-semibold mt-1">{bestPosition.ticker.symbol}</p>
                    <p className="text-emerald-400">+{bestPosition.pnl_percent.toFixed(2)}%</p>
                  </div>
                )}

                {worstPosition && (
                  <div className="rounded-2xl bg-rose-950/50 border border-rose-900/50 p-4">
                    <p className="text-xs text-rose-400">Худший performer</p>
                    <p className="text-lg font-semibold mt-1">{worstPosition.ticker.symbol}</p>
                    <p className="text-rose-400">{worstPosition.pnl_percent.toFixed(2)}%</p>
                  </div>
                )}
              </div>
            </div>
          </GlassCard>
        </div>
      </div>

      {/* Risk Analysis */}
      <GlassCard>
        <div className="p-6">
          <SectionHeader
            title="Risk Analysis"
            description="Portfolio exposure and concentration"
            action={<ShieldCheck className="h-4 w-4 text-slate-400" />}
          />

          <div className="grid gap-6 sm:grid-cols-3 mt-8">
            <div className="text-center">
              <p className="text-4xl font-bold text-orange-400">
                {Math.max(...positions.map((p) => p.allocation_percent), 0)}%
              </p>
              <p className="text-sm text-slate-400 mt-2">Largest Position</p>
            </div>
            <div className="text-center">
              <p className="text-4xl font-bold text-blue-400">{positions.length}</p>
              <p className="text-sm text-slate-400 mt-2">Diversified Assets</p>
            </div>
            <div className="text-center">
              <p className="text-4xl font-bold text-emerald-400">{summary?.win_rate ?? 0}%</p>
              <p className="text-sm text-slate-400 mt-2">Win Rate</p>
            </div>
          </div>
        </div>
      </GlassCard>
    </div>
  )
}
