import { BookOpen, HeartPulse } from 'lucide-react'
import { PageHeader } from '@/shared/ui/page-header'
import { SectionCard } from '@/shared/ui/section-card'
import { useJournalEntries } from '@/features/journal/hooks/journal-hooks'

export function JournalPage() {
  const journalQuery = useJournalEntries()
  const entries = journalQuery.data ?? []

  return (
    <div className="space-y-8">
      <PageHeader
        title="Journal"
        description="Capture trading notes, emotional insights, and AI coaching feedback."
      />

      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <SectionCard title="Recent notes" description="Review the latest journal entries.">
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

        <SectionCard title="Journal coaching" description="AI insights to improve your decision process.">
          <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-5">
            <div className="flex items-center gap-3 text-white">
              <HeartPulse className="h-5 w-5 text-rose-400" />
              <span className="font-semibold">Trading mindset</span>
            </div>
            <p className="mt-3 text-sm text-slate-400">Keep emotion in check by reviewing setups before execution and logging the thesis behind each trade.</p>
          </div>
          <SectionCard title="Structure" description="Improve trade review cadence." />
        </SectionCard>
      </div>
    </div>
  )
}
