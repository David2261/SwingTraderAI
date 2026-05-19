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
        title="Администратор: Пользователи"
        description="Управление доступом команды и проверка разрешений платформы."
      />

      <SectionCard title="Члены команды" description="Активные пользователи и пользователи, ожидающие подтверждения доступа." actions={<Users className="h-4 w-4 text-white" />}>
        <div className="grid gap-4">
          {adminUsers.map((user) => (
            <div key={user.id} className="grid gap-2 rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4 sm:grid-cols-[1fr_0.8fr_0.8fr]">
              <div>
                <p className="text-sm text-slate-400">Имя</p>
                <p className="mt-1 text-base font-semibold text-white">{user.name}</p>
              </div>
              <div>
                <p className="text-sm text-slate-400">Роль</p>
                <p className="mt-1 text-base text-slate-200">{user.role}</p>
              </div>
              <div>
                <p className="text-sm text-slate-400">Статус</p>
                <p className="mt-1 text-base text-white">{user.status}</p>
              </div>
            </div>
          ))}
        </div>
      </SectionCard>

      <SectionCard title="Обзор безопасности" description="Журналы аудита, проверки ролей и контроль доступа." actions={<ShieldCheck className="h-4 w-4 text-white" />}>
        <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-5 text-slate-400">
          <p className="text-sm">Еженедельно проверяйте схемы входа пользователей в систему и убедитесь, что только утвержденные роли имеют расширенный доступ к торговле в режиме реального времени и настройке моделей.</p>
        </div>
      </SectionCard>
    </div>
  )
}
