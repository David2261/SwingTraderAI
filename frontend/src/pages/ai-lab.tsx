import { Cpu, Database, ShieldCheck } from 'lucide-react'
import { PageHeader } from '@/shared/ui/page-header'
import { SectionCard } from '@/shared/ui/section-card'
import { useAILabModels, useAILabTrainingJobs } from '@/features/ai-lab/hooks/ai-lab-hooks'

export function AILabPage() {
  const modelsQuery = useAILabModels()
  const jobsQuery = useAILabTrainingJobs()
  const models = modelsQuery.data ?? []
  const jobs = jobsQuery.data ?? []

  return (
    <div className="space-y-8">
      <PageHeader
        title="AI Lab"
        description="Мониторинг регистрации моделей, заданий на обучение и достоверности прогнозов для лаборатории."
      />

      <div className="grid gap-6 xl:grid-cols-3">
        <SectionCard title="Registry моделей" description="Отслеживание производственных и экспериментальных AI моделей.">
          <div className="space-y-4">
            {models.map((model) => (
              <div key={model.id} className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
                <div className="flex items-center justify-between gap-3">
                  <p className="font-semibold text-white">{model.name}</p>
                  <span className="text-xs uppercase tracking-[0.2em] text-slate-400">{model.status}</span>
                </div>
                <div className="mt-3 grid gap-2 text-sm text-slate-400">
                  <span>Accuracy: {(model.accuracy * 100).toFixed(1)}%</span>
                  <span>Precision: {(model.precision * 100).toFixed(1)}%</span>
                  <span>Sharpe: {model.sharpe.toFixed(2)}</span>
                </div>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Задания на обучение" description="Живое состояние переобучения моделей и поставленных в очередь экспериментов.">
          <div className="space-y-4">
            {jobs.map((job) => (
              <div key={job.id} className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
                <div className="flex items-center justify-between gap-3 text-white">
                  <span>{job.model}</span>
                  <span className="text-sm text-slate-400">{job.status}</span>
                </div>
                <div className="mt-3 h-2 rounded-full bg-slate-800">
                  <div className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400" style={{ width: `${job.progress}%` }} />
                </div>
                <p className="mt-2 text-sm text-slate-400">Началось {job.started_at}</p>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Метрики модели" description="Ключевые показатели эффективности AI.">
          <div className="space-y-4 rounded-3xl border border-slate-800/90 bg-slate-950/70 p-5">
            <div className="flex items-center gap-3 text-white">
              <Cpu className="h-5 w-5 text-sky-300" />
              <span className="font-semibold">Операционная точность</span>
            </div>
            <p className="mt-3 text-sm text-slate-400">Прогнозы модели остаются стабильными в течение краткосрочных торговых циклов.</p>
            <div className="flex items-center gap-3 text-white">
              <Database className="h-5 w-5 text-emerald-300" />
              <span className="font-semibold">Использование признаков</span>
            </div>
            <p className="mt-3 text-sm text-slate-400">Объем, RSI и пересечения EMA в настоящее время обеспечивают наибольшую актуальность сигнала.</p>
            <div className="flex items-center gap-3 text-white">
              <ShieldCheck className="h-5 w-5 text-violet-300" />
              <span className="font-semibold">Достоверность прогноза</span>
            </div>
            <p className="mt-3 text-sm text-slate-400">Достоверность остается выше 80% для самых последних пакетов сигналов.</p>
          </div>
        </SectionCard>
      </div>
    </div>
  )
}
