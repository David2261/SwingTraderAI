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
        title="Strategies"
        description="Library of portfolio strategies and AI-backed execution plans."
      />

      <div className="grid gap-6 lg:grid-cols-3">
        {strategies.map((strategy) => (
          <SectionCard key={strategy.id} title={strategy.name} description={strategy.description}>
            <div className="flex items-center gap-3 text-slate-300">
              <CircleDot className="h-5 w-5 text-cyan-300" />
              <span className="text-sm">Status: {strategy.status}</span>
            </div>
          </SectionCard>
        ))}
      </div>

      <SectionCard title="Strategy Intelligence" description="Signals fused from momentum, trend, and volume indicators.">
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
            <div className="flex items-center gap-3 text-white"><Layers className="h-5 w-5 text-emerald-300" /><span className="font-semibold">Model blend</span></div>
            <p className="mt-3 text-sm text-slate-400">Combines EMA, MACD, RSI, and volume analysis into a single objective score.</p>
          </div>
          <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
            <div className="flex items-center gap-3 text-white"><ShieldCheck className="h-5 w-5 text-violet-300" /><span className="font-semibold">Risk overlay</span></div>
            <p className="mt-3 text-sm text-slate-400">Adaptive exposure management reduces drawdown in volatile regimes.</p>
          </div>
        </div>
      </SectionCard>
    </div>
  )
}
