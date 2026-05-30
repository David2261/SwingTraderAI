import { ArrowUpRight, Sparkles } from 'lucide-react'
import { PageHeader } from '@/shared/ui/page-header'
import { SectionCard } from '@/shared/ui/section-card'
import { SignalBadge } from '@/shared/ui/signal-badge'
import { mockMarketSnapshot, mockMarketHeatmap } from '@/shared/mock/mock-data'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/shared/ui/tabs'

export function MarketsPage() {
  const cryptoAssets = mockMarketSnapshot.filter(item =>
    ['BTC', 'ETH', 'SOL', 'TON'].includes(item.symbol.split('/')[0])
  )
  const moexAssets = mockMarketSnapshot.filter(item =>
    ['SBER', 'GAZP', 'LKOH', 'IMOEX'].includes(item.symbol)
  )
  const nasdaqAssets = mockMarketSnapshot.filter(item =>
    ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'AMZN'].includes(item.symbol)
  )

  // Вспомогательный рендер списка карточек инструментов
  const renderMarketList = (assetsList: typeof mockMarketSnapshot) => (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-1">
      {assetsList.map((item) => (
        <div
          key={item.id}
          className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4 transition hover:-translate-y-0.5 hover:border-slate-700/80"
        >
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-sm font-medium text-slate-400">{item.symbol}</p>
              <p className="mt-1 text-lg font-semibold text-white">${item.price.toFixed(2)}</p>
            </div>
            <div className={`text-sm font-semibold ${item.change_percent >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
              {item.change_percent >= 0 ? '+' : ''}{item.change_percent.toFixed(2)}%
            </div>
          </div>
        </div>
      ))}
      {assetsList.length === 0 && (
        <p className="text-sm text-slate-500 py-4 text-center">Нет доступных инструментов</p>
      )}
    </div>
  )

  return (
    <div className="space-y-8">
      <PageHeader
        title="Рынки"
        description="Ознакомьтесь с ключевыми инструментами, изменениями динамики и общими сигналами рыночной конъюнктуры."
      />

      {/* Основной блок с табами а-ля TradingView */}
      <div className="grid gap-6 lg:grid-cols-[1.8fr_1fr]">
        <SectionCard
          title="Top Market Pulse"
          description="Глобальные компании-лидеры, отобранные с помощью AI и технических решений."
        >
          <Tabs defaultValue="all" className="w-full">
            {/* Панель переключения вкладок */}
            <TabsList className="mb-4">
              <TabsTrigger value="all">Все рынки</TabsTrigger>
              <TabsTrigger value="crypto">Crypto</TabsTrigger>
              <TabsTrigger value="moex">MOEX</TabsTrigger>
              <TabsTrigger value="nasdaq">NASDAQ</TabsTrigger>
            </TabsList>

            {/* Контент вкладок */}
            <TabsContent value="all">
              {renderMarketList(mockMarketSnapshot)}
            </TabsContent>

            <TabsContent value="crypto">
              {renderMarketList(cryptoAssets)}
            </TabsContent>

            <TabsContent value="moex">
              {renderMarketList(moexAssets)}
            </TabsContent>

            <TabsContent value="nasdaq">
              {renderMarketList(nasdaqAssets)}
            </TabsContent>
          </Tabs>
        </SectionCard>

        {/* Секция секторов (остается без изменений или тоже можно категоризировать) */}
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
                <SignalBadge signal={item.regime === 'Bullish' ? 'BUY' : item.regime === 'Bearish' ? 'SELL' : 'NEUTRAL'} />
              </div>
            ))}
          </div>
        </SectionCard>
      </div>

      {/* Нижняя часть страницы (Статистика AI и маркетскан) */}
      <div className="grid gap-6 lg:grid-cols-2">
        <SectionCard title="Сила режима" description="AI Уровень доверия по основным индексам.">
          <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-6">
            <div className="flex items-center gap-3 text-white">
              <Sparkles className="h-5 w-5 text-amber-400" />
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
