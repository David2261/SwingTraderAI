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
        title="Admin: ML Training"
        description="Monitor AI model training jobs and compute usage."
      />

      <SectionCard title="Training queue" description="Latest AI lab jobs and status." actions={<Cpu className="h-4 w-4 text-white" />}>
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

      <SectionCard title="Resource forecast" description="Expected compute and model deployment windows." actions={<Sparkles className="h-4 w-4 text-white" />}>
        <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-5 text-slate-400">
          <p className="text-sm">Training capacity is optimized for overnight batch windows. Schedule new model runs after market close to avoid latency spikes.</p>
        </div>
      </SectionCard>
    </div>
  )
}
