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
        description="Manage support tickets, feature requests, and AI lab feedback."
      />

      <SectionCard title="Support tickets" description="Current open requests and feature feedback." actions={<Headset className="h-4 w-4 text-white" />}>
        <div className="space-y-4">
          {topics.map((topic) => (
            <div key={topic.id} className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-white">{topic.title}</p>
                <span className="text-xs uppercase tracking-[0.18em] text-slate-400">{topic.status}</span>
              </div>
              <p className="mt-2 text-sm text-slate-400">Support team is reviewing the request.</p>
            </div>
          ))}
        </div>
      </SectionCard>

      <SectionCard title="Help center" description="AI guidance and documentation for the trading terminal." actions={<MessageSquare className="h-4 w-4 text-white" />}>
        <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-5 text-slate-400">
          <p className="text-sm">Use the AI Copilot or in-app messages to connect with our support team and collaborate on strategy workflows.</p>
        </div>
      </SectionCard>
    </div>
  )
}
