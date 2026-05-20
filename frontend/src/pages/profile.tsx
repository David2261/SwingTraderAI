import { useState } from 'react'
import { UserCircle2, Edit2 } from 'lucide-react'
import { PageHeader } from '@/shared/ui/page-header'
import { SectionCard } from '@/shared/ui/section-card'
import { Button } from '@/shared/ui/button'

import { useUserProfile } from '@/features/profile/hooks/useUserProfile'
import { ProfileEditModal } from '@/features/profile/components/ProfileEditModal'

export function ProfilePage() {
  const { data: profile, isLoading } = useUserProfile()
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)

  if (isLoading) {
    return <div className="text-center py-12 text-slate-400">Загрузка профиля...</div>
  }

  return (
    <div className="space-y-8">
      <PageHeader
        title="Профиль"
        description="Управление учетной записью и персональными данными"
      />

      <SectionCard
        title="Профиль пользователя"
        description="Личная информация и уровень доступа"
        actions={
        <>
            <UserCircle2 className="h-5 w-5 text-white" />
            <Button onClick={() => setIsEditModalOpen(true)} className="gap-2">
              <Edit2 className="h-4 w-4" />
              Редактировать профиль
            </Button>
        </>
        }
      >
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
            <p className="text-sm text-slate-400">Имя пользователя</p>
            <p className="mt-2 text-lg font-semibold text-white">{profile?.username}</p>
          </div>

          <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
            <p className="text-sm text-slate-400">Email</p>
            <p className="mt-2 text-lg font-semibold text-white">{profile?.email}</p>
          </div>

          <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
            <p className="text-sm text-slate-400">Роль</p>
            <p className="mt-2 text-lg font-semibold text-white capitalize">{profile?.role}</p>
          </div>

          <div className="rounded-3xl border border-slate-800/90 bg-slate-950/70 p-4">
            <p className="text-sm text-slate-400">Дата регистрации</p>
            <p className="mt-2 text-lg font-semibold text-white">
              {profile?.created_at
                ? new Date(profile.created_at).toLocaleDateString('ru-RU', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric',
                  })
                : '—'}
            </p>
          </div>
        </div>
      </SectionCard>

      {/* Статистика */}
      <SectionCard title="Статистика аккаунта">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-5 bg-slate-950/50 rounded-3xl">
            <p className="text-3xl font-bold text-white">{profile?.watchlist_count ?? 0}</p>
            <p className="text-sm text-slate-400 mt-1">В watchlist</p>
          </div>
          <div className="text-center p-5 bg-slate-950/50 rounded-3xl">
            <p className="text-3xl font-bold text-white">{profile?.positions_count ?? 0}</p>
            <p className="text-sm text-slate-400 mt-1">Позиций</p>
          </div>
          <div className="text-center p-5 bg-slate-950/50 rounded-3xl">
            <p className="text-3xl font-bold text-white">{profile?.active_alerts_count ?? 0}</p>
            <p className="text-sm text-slate-400 mt-1">Алертов</p>
          </div>
        </div>
      </SectionCard>

      {/* Модальное окно редактирования */}
      <ProfileEditModal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        initialData={profile}
      />
    </div>
  )
}
