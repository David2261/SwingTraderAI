import { HeartPulse } from 'lucide-react'
import { PageHeader } from '@/shared/ui/page-header'
import { SectionCard } from '@/shared/ui/section-card'
import { useJournalEntries } from '@/features/journal/hooks/journal-hooks'

export function JournalPage() {
  const journalQuery = useJournalEntries()
  const entries = journalQuery.data ?? []

  return (
    <div className="space-y-8">
      <PageHeader
        title="Журнал"
        description="Фиксируйте торговые заметки, эмоциональные моменты и отзывы об использовании искусственного интеллекта в качестве тренера."
      />

      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <SectionCard title="Последние заметки" description="Просмотрите последние записи в журнале.">
          <div className="space-y-4">
            {entries.map((entry) => (
              <div key={entry.id} className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-sm text-slate-400">{entry.time}</p>
                    <p className="mt-1 text-lg font-semibold text-white">{entry.title}</p>
                  </div>
                  <span className="rounded-full bg-slate-900 px-3 py-1 text-xs uppercase tracking-[0.18em] text-slate-300">{entry.emotion}</span>
                </div>
                <p className="mt-3 text-sm text-slate-400">{entry.notes}</p>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Журнал тренинга" description="Инсайты ИИ для улучшения вашего процесса принятия решений.">
          <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-5">
            <div className="flex items-center gap-3 text-white">
              <HeartPulse className="h-5 w-5 text-rose-400" />
              <span className="font-semibold">Менталитет трейдинга</span>
            </div>
            <p className="mt-3 text-sm text-slate-400">Держите эмоции под контролем, просматривая подготовленные ситуации перед выполнением и регистрируя теорию, стоящую за каждым сделкой.</p>
          </div>
          <SectionCard title="Структура" description="Улучшите частоту обзора сделок." />
        </SectionCard>
      </div>
    </div>
  )
}
