import { Cpu, Sparkles } from 'lucide-react'
import { PageHeader } from '@/shared/ui/page-header'
import { SectionCard } from '@/shared/ui/section-card'
import { useAILabTrainingJobs } from '@/features/ai-lab/hooks/ai-lab-hooks'

export function AdminMLTrainingPage() {
  const trainingQuery = useAILabTrainingJobs()
  const jobs = trainingQuery.data ?? []

  return (
    <div className="space-y-8">
      <PageHeader
        title="Администратор: Обучение ML"
        description="Мониторинг задач обучения моделей ИИ и использования вычислительных ресурсов."
      />

      <SectionCard title="Очередь обучения" description="Последние задачи лаборатории ИИ и их статус." actions={<Cpu className="h-4 w-4 text-white" />}>
        <div className="space-y-4">
          {jobs.map((job) => (
            <div key={job.id} className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-white">{job.name}</p>
                <span className="text-xs uppercase tracking-[0.18em] text-slate-400">{job.status}</span>
              </div>
              <p className="mt-2 text-sm text-slate-400">{job.description}</p>
            </div>
          ))}
        </div>
      </SectionCard>

      <SectionCard title="Прогноз ресурсов" description="Ожидаемые окна вычислительных ресурсов и развертывания моделей." actions={<Sparkles className="h-4 w-4 text-white" />}>
        <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-5 text-slate-400">
          <p className="text-sm">Вместимость обучения оптимизирована для ночных пакетных окон. Планируйте новые запуски моделей после закрытия рынка, чтобы избежать скачков задержки.</p>
        </div>
      </SectionCard>
    </div>
  )
}
