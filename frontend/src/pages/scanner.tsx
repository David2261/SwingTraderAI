import { Activity, Search } from 'lucide-react'
import { useMemo, useState } from 'react'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { PageHeader } from '@/shared/ui/page-header'
import { SectionCard } from '@/shared/ui/section-card'
import { useScannerResults } from '@/features/scanner/hooks/scanner-hooks'

const filters = ['RSI oversold', 'EMA crossover', 'MACD bullish', 'Volume spike', 'Breakout'] as const

export function ScannerPage() {
  const [activeFilter, setActiveFilter] = useState<typeof filters[number]>('RSI oversold')
  const [query, setQuery] = useState('')
  const resultsQuery = useScannerResults()
  const results = resultsQuery.data ?? []

  const filtered = useMemo(
    () => results.filter((item) => item.symbol.toLowerCase().includes(query.toLowerCase()) || item.signal.toLowerCase().includes(query.toLowerCase())),
    [query, results]
  )

  return (
    <div className="space-y-8">
      <PageHeader
        title="Сканер"
        description="Отфильтруйте рынок, чтобы найти высокоэффективные стратегии и сигналы, основанные на искусственном интеллекте."
      />

      <SectionCard title="Фильтры сканера" description="Найдите сделки по техническому условию и силе сигнала.">
        <div className="flex flex-wrap gap-3">
          {filters.map((filterOption) => (
            <Button
              key={filterOption}
              variant={activeFilter === filterOption ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => setActiveFilter(filterOption)}
            >
              {filterOption}
            </Button>
          ))}
        </div>
      </SectionCard>

      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-3xl border border-slate-800/80 bg-slate-950/70 p-5 shadow-lg shadow-slate-950/20">
          <div className="mb-5 flex items-center gap-3">
            <Search className="h-4 w-4 text-slate-400" />
            <Input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Поиск символов или сигналов"
              className="border-0 bg-transparent px-0 text-slate-100 placeholder:text-slate-500 focus-visible:outline-none"
            />
          </div>
          <div className="space-y-4">
            {filtered.map((item) => (
              <div key={item.id} className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4 transition hover:-translate-y-0.5">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-sm text-slate-400">{item.symbol}</p>
                    <p className="mt-1 text-lg font-semibold text-white">{item.signal}</p>
                  </div>
                  <div className="text-right text-slate-300">{(item.confidence * 100).toFixed(0)}%</div>
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  {item.indicators.map((indicator) => (
                    <span key={indicator} className="rounded-full bg-slate-900/80 px-3 py-1 text-xs text-slate-300">
                      {indicator}
                    </span>
                  ))}
                </div>
                <p className="mt-3 text-sm text-slate-400">{item.note}</p>
              </div>
            ))}
          </div>
        </div>

        <SectionCard title="Сводка сканера" description="Количество активных сигналов и их недавняя сила.">
          <div className="space-y-4">
            <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
              <p className="text-sm text-slate-400">Активные выборы</p>
              <p className="mt-2 text-3xl font-semibold text-white">{filtered.length}</p>
            </div>
            <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
              <p className="text-sm text-slate-400">Текущий фильтр</p>
              <p className="mt-2 text-lg font-semibold text-white">{activeFilter}</p>
            </div>
            <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
              <div className="flex items-center justify-between">
                <p className="text-sm text-slate-400">Скорость сканера</p>
                <Activity className="h-5 w-5 text-cyan-300" />
              </div>
              <p className="mt-2 text-white">Прямая трансляция обновляется каждую секунду.</p>
            </div>
          </div>
        </SectionCard>
      </div>
    </div>
  )
}
