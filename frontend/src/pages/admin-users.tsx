import { ShieldCheck, Users } from 'lucide-react'
import { PageHeader } from '@/shared/ui/page-header'
import { SectionCard } from '@/shared/ui/section-card'

const adminUsers = [
  { id: 'u1', name: 'Mia Lawson', role: 'Operations', status: 'Active' },
  { id: 'u2', name: 'Evan Harper', role: 'Analytics', status: 'Pending' },
  { id: 'u3', name: 'Nora Patel', role: 'Trader', status: 'Active' },
  { id: 'u4', name: 'Liam Cole', role: 'Risk', status: 'Suspended' },
]

export function AdminUsersPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Admin: Users"
        description="Manage team access and review platform permissions."
      />

      <SectionCard title="Team members" description="Active users and pending access approvals." actions={<Users className="h-4 w-4 text-white" />}>
        <div className="grid gap-4">
          {adminUsers.map((user) => (
            <div key={user.id} className="grid gap-2 rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4 sm:grid-cols-[1fr_0.8fr_0.8fr]">
              <div>
                <p className="text-sm text-slate-400">Name</p>
                <p className="mt-1 text-base font-semibold text-white">{user.name}</p>
              </div>
              <div>
                <p className="text-sm text-slate-400">Role</p>
                <p className="mt-1 text-base text-slate-200">{user.role}</p>
              </div>
              <div>
                <p className="text-sm text-slate-400">Status</p>
                <p className="mt-1 text-base text-white">{user.status}</p>
              </div>
            </div>
          ))}
        </div>
      </SectionCard>

      <SectionCard title="Security overview" description="Audit logs, role reviews, and access controls." actions={<ShieldCheck className="h-4 w-4 text-white" />}>
        <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-5 text-slate-400">
          <p className="text-sm">Review user login patterns weekly and ensure only approved roles have elevated access to live trading and model configuration.</p>
        </div>
      </SectionCard>
    </div>
  )
}
