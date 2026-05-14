import { ArrowUpRight, Globe2, Sparkles } from 'lucide-react'
import { PageHeader } from '@/shared/ui/page-header'
import { SectionCard } from '@/shared/ui/section-card'
import { SignalBadge } from '@/shared/ui/signal-badge'
import { mockMarketSnapshot, mockMarketHeatmap } from '@/shared/mock/mock-data'

export function MarketsPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Markets"
        description="Browse key instruments, momentum shifts, and broad market regime signals."
      />

      <div className="grid gap-6 lg:grid-cols-[1.8fr_1fr]">
        <SectionCard
          title="Top Market Pulse"
          description="Global movers selected by AI and technical flow."
        >
          <div className="grid gap-4">
            {mockMarketSnapshot.map((item) => (
              <div key={item.id} className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4 transition hover:-translate-y-0.5">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="text-sm text-slate-400">{item.symbol}</p>
                    <p className="mt-1 text-lg font-semibold text-white">${item.price.toFixed(2)}</p>
                  </div>
                  <div className={item.change_percent >= 0 ? 'text-emerald-300' : 'text-rose-300'}>
                    {item.change_percent >= 0 ? '+' : ''}{item.change_percent.toFixed(2)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard
          title="Live Sector Heat"
          description="Signals relate to momentum, volatility, and risk appetite."
        >
          <div className="space-y-4">
            {mockMarketHeatmap.map((item) => (
              <div key={item.symbol} className="flex items-center justify-between rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
                <div>
                  <p className="text-sm text-slate-400">{item.symbol}</p>
                  <p className="mt-1 font-semibold text-white">{item.name}</p>
                </div>
                <SignalBadge signal={item.status === 'Bullish' ? 'BUY' : item.status === 'Bearish' ? 'SELL' : 'NEUTRAL'} />
              </div>
            ))}
          </div>
        </SectionCard>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <SectionCard title="Regime Strength" description="AI confidence across the major indices.">
          <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-6">
            <div className="flex items-center gap-3 text-white">
              <Sparkles className="h-5 w-5" />
              <span className="font-semibold">Bullish momentum remains dominant</span>
            </div>
            <p className="mt-4 text-sm text-slate-400">Watch for range extension on BTC and SBER while ETH holds above key support.</p>
          </div>
        </SectionCard>

        <SectionCard title="Market Scan" description="Top actionable opportunities from the AI engine.">
          <div className="grid gap-4">
            <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm text-slate-400">Momentum indicator</p>
                  <p className="mt-1 text-base font-semibold text-white">BTC above 50-day moving average</p>
                </div>
                <ArrowUpRight className="h-5 w-5 text-emerald-300" />
              </div>
            </div>
            <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm text-slate-400">Resistance watch</p>
                  <p className="mt-1 text-base font-semibold text-white">AAPL near 186 with fading momentum</p>
                </div>
                <ArrowUpRight className="h-5 w-5 text-slate-400" />
              </div>
            </div>
          </div>
        </SectionCard>
      </div>
    </div>
  )
}
