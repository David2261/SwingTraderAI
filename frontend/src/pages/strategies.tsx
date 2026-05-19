import { CircleDot, Layers, ShieldCheck } from 'lucide-react'
import { PageHeader } from '@/shared/ui/page-header'
import { SectionCard } from '@/shared/ui/section-card'
import { useAdminStrategies } from '@/features/admin/hooks/admin-hooks'

export function StrategiesPage() {
  const strategiesQuery = useAdminStrategies()
  const strategies = strategiesQuery.data ?? []

  return (
    <div className="space-y-8">
      <PageHeader
        title="Стратегии"
        description="Библиотека стратегий управления портфелем и планов исполнения, основанных на искусственном интеллекте."
      />

      <div className="grid gap-6 lg:grid-cols-3">
        {strategies.map((strategy) => (
          <SectionCard key={strategy.id} title={strategy.name} description={strategy.description}>
            <div className="flex items-center gap-3 text-slate-300">
              <CircleDot className="h-5 w-5 text-cyan-300" />
              <span className="text-sm">Статус: {strategy.status}</span>
            </div>
          </SectionCard>
        ))}
      </div>

      <SectionCard title="Интеллект стратегий" description="Сигналы, объединенные из импульсных, трендовых и объемных индикаторов.">
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
            <div className="flex items-center gap-3 text-white"><Layers className="h-5 w-5 text-emerald-300" /><span className="font-semibold">Комбинация моделей</span></div>
            <p className="mt-3 text-sm text-slate-400">Объединяет EMA, MACD, RSI и анализ объема в единую объективную оценку.</p>
          </div>
          <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
            <div className="flex items-center gap-3 text-white"><ShieldCheck className="h-5 w-5 text-violet-300" /><span className="font-semibold">Наложение рисков</span></div>
            <p className="mt-3 text-sm text-slate-400">Адаптивное управление рисками снижает потери в условиях нестабильности.</p>
          </div>
        </div>
      </SectionCard>
    </div>
  )
}
