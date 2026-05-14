import { useMemo } from 'react'
import { Bell, Clock3, LineChart } from 'lucide-react'
import { PageHeader } from '@/shared/ui/page-header'
import { SectionCard } from '@/shared/ui/section-card'
import { SignalBadge } from '@/shared/ui/signal-badge'
import { useSignalsHistory } from '@/features/signals/hooks/signals-hooks'

export function SignalsPage() {
  const historyQuery = useSignalsHistory()
  const history = historyQuery.data ?? []

  const grouped = useMemo(() => {
    return history.reduce<Record<string, typeof history>>((acc, item) => {
      const key = item.category
      if (!acc[key]) acc[key] = []
      acc[key].push(item)
      return acc
    }, {})
  }, [history])

  return (
    <div className="space-y-8">
      <PageHeader
        title="Signals"
        description="Browse signal history, confidence bars, and recent category trends."
      />

      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <SectionCard title="Signal timeline" description="Review recent AI-generated signals and their market rationale.">
          <div className="space-y-4">
            {history.map((signal) => (
              <div key={signal.id} className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4 transition hover:border-slate-600">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-sm text-slate-400">{signal.symbol}</p>
                    <p className="mt-1 text-lg font-semibold text-white">{signal.category}</p>
                  </div>
                  <SignalBadge signal={signal.category as any} />
                </div>
                <div className="mt-3 flex items-center justify-between gap-3 text-slate-400">
                  <span>{signal.time}</span>
                  <span>{(signal.confidence * 100).toFixed(0)}% confidence</span>
                </div>
                <p className="mt-3 text-sm text-slate-500">{signal.note}</p>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Signal categories" description="Distribution by category and trend strength.">
          <div className="space-y-4">
            {Object.entries(grouped).map(([category, items]) => (
              <div key={category} className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
                <div className="flex items-center justify-between gap-3 text-white">
                  <span>{category}</span>
                  <span>{items.length} entries</span>
                </div>
                <div className="mt-3 h-2 rounded-full bg-slate-800">
                  <div className="h-full rounded-full bg-gradient-to-r from-sky-400 to-emerald-400" style={{ width: `${Math.min(items.length * 20, 100)}%` }} />
                </div>
              </div>
            ))}
            <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
              <div className="flex items-center gap-3 text-slate-200">
                <LineChart className="h-5 w-5 text-cyan-300" />
                <span className="font-semibold">Confidence trend</span>
              </div>
              <p className="mt-3 text-sm text-slate-400">Signals are weighted by confidence and strategy consensus.</p>
            </div>
          </div>
        </SectionCard>
      </div>
    </div>
  )
}
