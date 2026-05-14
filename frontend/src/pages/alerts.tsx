import { Bell, ShieldCheck } from 'lucide-react'
import { PageHeader } from '@/shared/ui/page-header'
import { SectionCard } from '@/shared/ui/section-card'
import { useActiveAlerts } from '@/features/alerts/hooks/alerts-hooks'

export function AlertsPage() {
  const alertsQuery = useActiveAlerts()
  const alerts = alertsQuery.data ?? []

  return (
    <div className="space-y-8">
      <PageHeader
        title="Alerts"
        description="Active alerts and delivery channels for your trading terminal."
      />

      <div className="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
        <SectionCard title="Active alerts" description="Review the latest triggered trade alerts.">
          <div className="space-y-4">
            {alerts.map((alert) => (
              <div key={alert.id} className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
                <div className="flex items-center justify-between gap-3">
                  <span className="font-semibold text-white">{alert.label}</span>
                  <span className="text-xs uppercase tracking-[0.18em] text-slate-400">{alert.severity}</span>
                </div>
                <p className="mt-2 text-sm text-slate-400">{alert.symbol} · {alert.time}</p>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="Delivery channels" description="Where your alerts can be routed.">
          <div className="space-y-3 rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
            {['Email', 'Telegram', 'In-app'].map((channel) => (
              <div key={channel} className="flex items-center justify-between rounded-2xl border border-slate-800/90 bg-slate-900/80 px-4 py-3">
                <span className="text-sm text-slate-200">{channel}</span>
                <span className="text-xs uppercase tracking-[0.18em] text-slate-400">Enabled</span>
              </div>
            ))}
          </div>
          <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
            <div className="flex items-center gap-3 text-white">
              <ShieldCheck className="h-5 w-5 text-emerald-300" />
              <span className="font-semibold">Alert reliability</span>
            </div>
            <p className="mt-3 text-sm text-slate-400">Alerts are delivered with priority routing and low latency.</p>
          </div>
        </SectionCard>
      </div>
    </div>
  )
}
