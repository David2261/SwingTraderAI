import { Activity, ServerCog } from 'lucide-react'
import { PageHeader } from '@/shared/ui/page-header'
import { SectionCard } from '@/shared/ui/section-card'

const statusItems = [
  { label: 'API latency', value: '24 ms', trend: 'stable' },
  { label: 'Signal pipeline', value: 'Healthy', trend: 'up' },
  { label: 'Data feed', value: 'Live', trend: 'up' },
  { label: 'Auth services', value: 'Operational', trend: 'stable' },
]

export function AdminSystemStatusPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Администратор: Состояние системы"
        description="Проверка работоспособности каналов данных, API и сервисов платформы."
      />

      <SectionCard title="Platform status" description="Real-time service health summaries." actions={<ServerCog className="h-4 w-4 text-white" />}>
        <div className="grid gap-4 sm:grid-cols-2">
          {statusItems.map((item) => (
            <div key={item.label} className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
              <div className="flex items-center justify-between gap-3">
                <p className="text-sm text-slate-400">{item.label}</p>
                <span className="text-sm uppercase tracking-[0.18em] text-slate-400">{item.trend}</span>
              </div>
              <p className="mt-3 text-2xl font-semibold text-white">{item.value}</p>
            </div>
          ))}
        </div>
      </SectionCard>

      <SectionCard title="Готовность к инцидентам" description="Подготовка к отключениям электроэнергии и восстановительным работам." actions={<Activity className="h-4 w-4 text-white" />}>
        <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-5 text-slate-400">
          <p className="text-sm">Все основные сервисы мониторятся. Автоматические оповещения будут уведомлять команду эксплуатации, если какой-либо pipeline упадет ниже ожидаемых порогов.</p>
        </div>
      </SectionCard>
    </div>
  )
}
