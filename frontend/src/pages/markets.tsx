import { ArrowUpRight, Globe2, Sparkles } from 'lucide-react'
import { PageHeader } from '@/shared/ui/page-header'
import { SectionCard } from '@/shared/ui/section-card'
import { SignalBadge } from '@/shared/ui/signal-badge'
import { mockMarketSnapshot, mockMarketHeatmap } from '@/shared/mock/mock-data'

export function MarketsPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Рынки"
        description="Ознакомьтесь с ключевыми инструментами, изменениями динамики и общими сигналами рыночной конъюнктуры."
      />

      <div className="grid gap-6 lg:grid-cols-[1.8fr_1fr]">
        <SectionCard
          title="Top Market Pulse"
          description="Глобальные компании-лидеры, отобранные с помощью AI и технических решений."
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
          description="Сигналы связаны с импульсом, волатильностью и склонностью к риску."
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
        <SectionCard title="Сила режима" description="AI Уровень доверия по основным индексам.">
          <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-6">
            <div className="flex items-center gap-3 text-white">
              <Sparkles className="h-5 w-5" />
              <span className="font-semibold">Бычий импульс по-прежнему доминирует.</span>
            </div>
            <p className="mt-4 text-sm text-slate-400">Ожидайте дальнейшего расширения диапазона для BTC и SBER, пока ETH удерживается выше ключевого уровня поддержки.</p>
          </div>
        </SectionCard>

        <SectionCard title="Market Scan" description="Наиболее перспективные возможности, которые предоставляет система искусственного интеллекта.">
          <div className="grid gap-4">
            <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm text-slate-400">Индикатор импульса</p>
                  <p className="mt-1 text-base font-semibold text-white">BTC выше 50-дневной скользящей средней.</p>
                </div>
                <ArrowUpRight className="h-5 w-5 text-emerald-300" />
              </div>
            </div>
            <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm text-slate-400">Слежение за сопротивлением</p>
                  <p className="mt-1 text-base font-semibold text-white">AAPL находится около отметки 186, импульс снижается.</p>
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
