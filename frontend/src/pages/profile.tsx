import { UserCircle2 } from 'lucide-react'
import { PageHeader } from '@/shared/ui/page-header'
import { SectionCard } from '@/shared/ui/section-card'
import { useAdminProfile } from '@/features/admin/hooks/admin-hooks'

export function ProfilePage() {
  const profileQuery = useAdminProfile()
  const profile = profileQuery.data

  return (
    <div className="space-y-8">
      <PageHeader
        title="Profile"
        description="View your account details and platform access level."
      />

      <SectionCard title="User Profile" description="Personal and role information." actions={<UserCircle2 className="h-4 w-4 text-white" />}>
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
            <p className="text-sm text-slate-400">Username</p>
            <p className="mt-2 text-lg font-semibold text-white">{profile?.username ?? 'Loading'}</p>
          </div>
          <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
            <p className="text-sm text-slate-400">Email</p>
            <p className="mt-2 text-lg font-semibold text-white">{profile?.email ?? 'Loading'}</p>
          </div>
          <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
            <p className="text-sm text-slate-400">Role</p>
            <p className="mt-2 text-lg font-semibold text-white">{profile?.role ?? 'Loading'}</p>
          </div>
          <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
            <p className="text-sm text-slate-400">Joined</p>
            <p className="mt-2 text-lg font-semibold text-white">{profile?.joined_at ?? 'Loading'}</p>
          </div>
        </div>
      </SectionCard>
    </div>
  )
}
