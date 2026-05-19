import { Headset, MessageSquare } from 'lucide-react'
import { PageHeader } from '@/shared/ui/page-header'
import { SectionCard } from '@/shared/ui/section-card'
import { useAdminSupportTopics } from '@/features/admin/hooks/admin-hooks'

export function SupportPage() {
  const topicsQuery = useAdminSupportTopics()
  const topics = topicsQuery.data ?? []

  return (
    <div className="space-y-8">
      <PageHeader
        title="Support"
        description="Управление заявками в службу поддержки, запросами на добавление новых функций и отзывами о работе лаборатории ИИ."
      />

      <SectionCard title="Заявки в службу поддержки" description="Текущие открытые запросы и отзывы о новых функциях." actions={<Headset className="h-4 w-4 text-white" />}>
        <div className="space-y-4">
          {topics.map((topic) => (
            <div key={topic.id} className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-white">{topic.title}</p>
                <span className="text-xs uppercase tracking-[0.18em] text-slate-400">{topic.status}</span>
              </div>
              <p className="mt-2 text-sm text-slate-400">Служба поддержки рассматривает запрос.</p>
            </div>
          ))}
        </div>
      </SectionCard>

      <SectionCard title="Центр поддержки" description="Руководство и документация по использованию ИИ для торгового терминала." actions={<MessageSquare className="h-4 w-4 text-white" />}>
        <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-5 text-slate-400">
          <p className="text-sm">Используйте Email или сообщения в приложении, чтобы связаться с нашей службой поддержки и совместно работать над стратегическими процессами.</p>
        </div>
      </SectionCard>
    </div>
  )
}
