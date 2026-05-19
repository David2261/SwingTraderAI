import { Activity, BarChart3, Clock3 } from 'lucide-react'
import { PageHeader } from '@/shared/ui/page-header'
import { SectionCard } from '@/shared/ui/section-card'

export function BacktestingPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Тестирование на исторических данных"
        description="Смоделируйте стратегии с использованием исторических данных и проанализируйте поведение кривой доходности акций."
      />

      <div className="grid gap-6 xl:grid-cols-[1.25fr_0.75fr]">
        <SectionCard title="Кривая доходности" description="Диаграмма-заполнитель отображает смоделированное поведение стратегии.">
          <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-5">
            <div className="h-72 rounded-3xl bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900" />
          </div>
        </SectionCard>

        <div className="space-y-4">
          <SectionCard title="Краткий обзор результатов" description="Ключевые показатели бэктестинга и сигналы модели.">
            <div className="grid gap-3">
              <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
                <p className="text-sm text-slate-400">Общая доходность</p>
                <p className="mt-2 text-2xl font-semibold text-white">+18.4%</p>
              </div>
              <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
                <p className="text-sm text-slate-400">Коэффициент Шарпа</p>
                <p className="mt-2 text-2xl font-semibold text-white">1.86</p>
              </div>
              <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
                <p className="text-sm text-slate-400">Максимальная просадка</p>
                <p className="mt-2 text-2xl font-semibold text-white">-7.2%</p>
              </div>
            </div>
          </SectionCard>
          <SectionCard title="История сделок" description="Последние смоделированные сигналы входа и выхода.">
            <div className="space-y-3">
              {['BTC long', 'SBER breakout', 'TSLA pullback'].map((item) => (
                <div key={item} className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <span className="font-semibold text-white">{item}</span>
                    <span className="text-xs uppercase tracking-[0.18em] text-slate-400">Активный</span>
                  </div>
                  <p className="mt-2 text-sm text-slate-400">Сигнал генерируется с помощью наложения данных об импульсе и волатильности, полученных с помощью AI.</p>
                </div>
              ))}
            </div>
          </SectionCard>
        </div>
      </div>
    </div>
  )
}
