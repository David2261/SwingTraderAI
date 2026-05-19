import { Sparkles, TrendingUp, AlertTriangle, Zap } from 'lucide-react'
import {
  GlassCard,
  SectionHeader,
  MetricRow,
  LivePulseIndicator,
  MarketStatusBadge,
  SignalBadge,
} from '@/shared/ui'
import { mockPortfolioSummary, mockSignalsFeed, mockAiMarketBriefing, mockExplainability, mockAlerts, mockPredictions } from '@/shared/mock/mock-data'

export function DashboardPage() {
  return (
    <div className="space-y-6">
      {/* AI Market Briefing - Hero Section */}
      <div className="rounded-3xl border border-slate-800/90 bg-gradient-to-br from-slate-900/80 to-slate-950/90 p-6 backdrop-blur-sm shadow-[0_0_40px_rgba(59,130,246,0.1)]">
        <div className="flex items-start justify-between gap-4 mb-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-blue-400" />
              AI Market Briefing
            </h2>
            <p className="text-xs text-slate-400 mt-1">Real-time market regime analysis</p>
          </div>
          <MarketStatusBadge status="bullish" />
        </div>

        <div className="grid gap-4">
          <div>
            <p className="text-sm font-semibold text-white mb-2">{mockAiMarketBriefing.narrative}</p>
          </div>

          <div className="grid gap-3 sm:grid-cols-4">
            <div className="rounded-2xl bg-slate-800/50 p-3">
              <p className="text-xs text-slate-400">Regime</p>
              <p className="text-sm font-semibold text-emerald-400 mt-1">{mockAiMarketBriefing.regime}</p>
            </div>
            <div className="rounded-2xl bg-slate-800/50 p-3">
              <p className="text-xs text-slate-400">Volatility</p>
              <p className="text-sm font-semibold text-orange-400 mt-1">{mockAiMarketBriefing.volatility}</p>
            </div>
            <div className="rounded-2xl bg-slate-800/50 p-3">
              <p className="text-xs text-slate-400">AI Confidence</p>
              <div className="flex items-center gap-2 mt-1">
                <div className="h-2 w-12 rounded-full bg-slate-700">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-blue-500 to-blue-400"
                    style={{ width: `${mockAiMarketBriefing.confidence * 100}%` }}
                  />
                </div>
                <span className="text-sm font-semibold text-blue-400">{Math.round(mockAiMarketBriefing.confidence * 100)}%</span>
              </div>
            </div>
            <div className="rounded-2xl bg-slate-800/50 p-3">
              <p className="text-xs text-slate-400">Sentiment</p>
              <p className="text-sm font-semibold text-emerald-400 mt-1">{mockAiMarketBriefing.sentiment}</p>
            </div>
          </div>

          <div className="rounded-2xl bg-slate-800/30 border border-slate-700/50 p-3">
            <p className="text-xs text-slate-400 mb-2">Strongest Setups</p>
            <ul className="space-y-1">
              {mockAiMarketBriefing.strongest_setups.map((setup, i) => (
                <li key={i} className="text-sm text-slate-300 flex items-center gap-2">
                  <div className="h-1 w-1 rounded-full bg-emerald-400" />
                  {setup}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="mt-4 flex items-center justify-between pt-4 border-t border-slate-800/50">
          <div className="flex items-center gap-2">
            <LivePulseIndicator active={true} size="sm" />
            <span className="text-xs text-slate-500">Live updated {new Date().toLocaleTimeString()}</span>
          </div>
        </div>
      </div>

      {/* Portfolio & Signals - Upper Row */}
      <div className="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
        {/* Portfolio Summary */}
        <GlassCard>
          <div className="p-6 space-y-4">
            <SectionHeader title="Portfolio" description="Real-time allocation snapshot" />

            <MetricRow label="Total Value" value={`$${mockPortfolioSummary.total_value.toLocaleString()}`} trend="up" />
            <MetricRow label="Day P&L" value={`${mockPortfolioSummary.day_change_percent > 0 ? '+' : ''}${mockPortfolioSummary.day_change_percent}%`} trend={mockPortfolioSummary.day_change_percent > 0 ? 'up' : 'down'} />
            <MetricRow label="Total P&L" value={`$${mockPortfolioSummary.total_pnl.toLocaleString()}`} trend="up" secondary={`Win rate: ${mockPortfolioSummary.win_rate}%`} />

            <div className="pt-3 border-t border-slate-800/50">
              <div className="h-6 rounded-full bg-slate-800/50 overflow-hidden">
                <div className="flex h-full">
                  {[
                    { pct: 42, color: 'bg-blue-500' },
                    { pct: 18, color: 'bg-emerald-500' },
                    { pct: 12, color: 'bg-orange-500' },
                    { pct: 9, color: 'bg-rose-500' },
                    { pct: 8, color: 'bg-purple-500' },
                  ].map((segment, i) => (
                    <div key={i} className={segment.color} style={{ width: `${segment.pct}%` }} />
                  ))}
                </div>
              </div>
              <p className="text-xs text-slate-500 mt-2">{mockPortfolioSummary.positions} positions</p>
            </div>
          </div>
        </GlassCard>

        {/* AI Signals Feed */}
        <GlassCard>
          <div className="p-6 space-y-3">
            <SectionHeader title="Latest Signals" description="AI-generated trading ideas" action={<TrendingUp className="h-4 w-4 text-slate-400" />} />

            {mockSignalsFeed.slice(0, 3).map((signal) => (
              <div key={signal.id} className="rounded-2xl bg-slate-800/50 p-3 flex items-center justify-between gap-3">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-white">{signal.ticker}</span>
                    <SignalBadge signal={signal.signal} />
                  </div>
                  <p className="text-xs text-slate-500 mt-1">{signal.indicators[0]}</p>
                </div>
                <div className="text-right">
                  <div className="h-5 w-12 rounded-full bg-slate-700/50 flex items-center justify-center">
                    <div
                      className="h-4 w-11 rounded-full bg-gradient-to-r from-blue-500 to-emerald-400"
                      style={{ width: `${signal.confidence * 100 * 0.95}px` }}
                    />
                  </div>
                  <p className="text-xs text-slate-500 mt-1">{Math.round(signal.confidence * 100)}%</p>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>

      {/* Heatmap & Explainability */}
      <div className="grid gap-6 lg:grid-cols-[1fr_1.2fr]">
        {/* Market Heatmap */}
        <GlassCard>
          <div className="p-6 space-y-4">
            <SectionHeader title="Market Heatmap" description="Real-time performance grid" />

            <div className="grid grid-cols-2 gap-3">
              {[
                { symbol: 'BTC', change: 1.84, regime: 'Bullish', active: true },
                { symbol: 'ETH', change: -0.44, regime: 'Neutral', active: false },
                { symbol: 'SBER', change: 2.27, regime: 'Bullish', active: true },
                { symbol: 'GAZP', change: -1.69, regime: 'Bearish', active: false },
              ].map((item) => (
                <div
                  key={item.symbol}
                  className="rounded-2xl bg-slate-800/50 p-3 relative overflow-hidden"
                >
                  {item.active && <div className="absolute inset-0 opacity-5 bg-gradient-to-br from-emerald-500 to-transparent" />}
                  <div className="relative">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-semibold text-white">{item.symbol}</span>
                      {item.active && <LivePulseIndicator active size="sm" />}
                    </div>
                    <p className={`text-sm font-semibold mt-1 ${item.change > 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {item.change > 0 ? '+' : ''}{item.change}%
                    </p>
                    <p className="text-xs text-slate-500">{item.regime}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </GlassCard>

        {/* AI Explainability */}
        <GlassCard>
          <div className="p-6 space-y-3">
            <SectionHeader title="AI Explainability" description="Why signals were generated" action={<Sparkles className="h-4 w-4 text-blue-400" />} />

            {mockExplainability.map((exp) => (
              <div key={exp.id} className="rounded-2xl bg-slate-800/50 p-3 space-y-2">
                <p className="text-sm font-semibold text-slate-300">{exp.title}</p>
                <ul className="space-y-1">
                  {exp.reasons.slice(0, 2).map((reason, i) => (
                    <li key={i} className="text-xs text-slate-500 flex items-start gap-2">
                      <span className="text-blue-400 mt-0.5">→</span>
                      <span>{reason}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>

      {/* Alerts & Predictions */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Active Alerts */}
        <GlassCard>
          <div className="p-6 space-y-3">
            <SectionHeader title="Active Alerts" description="Real-time trading warnings" action={<AlertTriangle className="h-4 w-4 text-orange-400" />} />

            {mockAlerts.slice(0, 2).map((alert) => (
              <div key={alert.id} className={`rounded-2xl p-3 flex items-start gap-3 ${
                alert.severity === 'high' ? 'bg-rose-950/50 border border-rose-900/30' :
                alert.severity === 'medium' ? 'bg-orange-950/50 border border-orange-900/30' :
                'bg-blue-950/50 border border-blue-900/30'
              }`}>
                <div className={`h-2 w-2 rounded-full mt-1 flex-shrink-0 ${
                  alert.severity === 'high' ? 'bg-rose-500' :
                  alert.severity === 'medium' ? 'bg-orange-500' :
                  'bg-blue-500'
                }`} />
                <div>
                  <p className="text-sm font-semibold text-white">{alert.label}</p>
                  <p className="text-xs text-slate-400 mt-1">{alert.description}</p>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>

        {/* Recent Predictions */}
        <GlassCard>
          <div className="p-6 space-y-3">
            <SectionHeader title="Recent Predictions" description="AI model forecasts" action={<Zap className="h-4 w-4 text-yellow-400" />} />

            {mockPredictions.slice(0, 2).map((pred) => (
              <div key={pred.id} className="rounded-2xl bg-slate-800/50 p-3 space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-semibold text-white">{pred.symbol}</span>
                  <span className={`text-xs font-semibold uppercase tracking-wider ${pred.prediction === 'bullish' ? 'text-emerald-400' : 'text-rose-400'}`}>
                    {pred.prediction}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-500">Probability</span>
                  <span className="text-sm font-semibold text-blue-400">{Math.round(pred.probability * 100)}%</span>
                </div>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>

      {/* Quick Actions */}
      <GlassCard>
        <div className="p-6 space-y-4">
          <SectionHeader title="Quick Actions" description="One-click trading commands" />

          <div className="grid gap-3 sm:grid-cols-4">
            {[
              { label: 'View Setup', color: 'blue' },
              { label: 'Place Order', color: 'emerald' },
              { label: 'Risk Check', color: 'orange' },
              { label: 'Backtest', color: 'purple' },
            ].map((action) => (
              <button
                key={action.label}
                className={`rounded-2xl px-4 py-3 text-sm font-semibold transition-all transform hover:scale-105 hover:shadow-lg ${
                  action.color === 'blue' ? 'bg-blue-900/50 text-blue-300 hover:bg-blue-800/60' :
                  action.color === 'emerald' ? 'bg-emerald-900/50 text-emerald-300 hover:bg-emerald-800/60' :
                  action.color === 'orange' ? 'bg-orange-900/50 text-orange-300 hover:bg-orange-800/60' :
                  'bg-purple-900/50 text-purple-300 hover:bg-purple-800/60'
                }`}
              >
                {action.label}
              </button>
            ))}
          </div>
        </div>
      </GlassCard>
    </div>
  )
}
