import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/shared/api/api-client'
import type { User } from '@/shared/api/api-client-types'

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/shared/ui/dialog'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import type { ProfileUpdateRequest } from '@/features/auth/schemas/api-schemas'
import { timezone } from '@/shared/lib/timezone'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/shared/ui/dropdown'
import { Check, ChevronDown } from 'lucide-react'

interface ProfileEditModalProps {
  isOpen: boolean
  onClose: () => void
  initialData?: User | null
}

export function ProfileEditModal({ isOpen, onClose, initialData }: ProfileEditModalProps) {
  const queryClient = useQueryClient()

  const [formData, setFormData] = useState({
    username: '',
    telegram_id: '',
    timezone: 'Europe/Moscow',
  })

  const updateMutation = useMutation({
    mutationFn: (data: ProfileUpdateRequest) => apiClient.profile.update(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user', 'profile'] })
      onClose()
    },
  })

  useEffect(() => {
    if (initialData) {
      setFormData({
        username: initialData.username || '',
        telegram_id: initialData.telegram_id?.toString() || '',
        timezone: initialData.timezone || 'Europe/Moscow',
      })
    }
  }, [initialData])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const payload: ProfileUpdateRequest = {
      username: formData.username || undefined,
      timezone: formData.timezone,
      telegram_id: formData.telegram_id.trim() === '' ? null : Number(formData.telegram_id),
    }
    updateMutation.mutate(payload)
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Редактирование профиля</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4 py-4">
          {/* Имя пользователя */}
          <div className="space-y-2">
            <Label htmlFor="username">Имя пользователя</Label>
            <Input
              id="username"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              required
              minLength={3}
              maxLength={50}
            />
          </div>

          {/* Telegram ID */}
          <div className="space-y-2">
            <Label htmlFor="telegram_id">Telegram ID</Label>
            <Input
              id="telegram_id"
              type="number"
              placeholder="Не указан"
              value={formData.telegram_id}
              onChange={(e) => setFormData({ ...formData, telegram_id: e.target.value })}
            />
          </div>

          {/* Временная зона */}
          <div className="space-y-2">
            <Label htmlFor="timezone">Временная зона</Label>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" className="w-full justify-between">
                  {timezone.find((tz) => tz.value === formData.timezone)?.label || "Выберите временную зону"}
                  <ChevronDown className="h-4 w-4 opacity-50" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="start" className="w-[var(--radix-dropdown-menu-trigger-width)] max-h-80 overflow-y-auto">
                {timezone.map((tz) => (
                  <DropdownMenuItem
                    key={tz.value}
                    onClick={() => setFormData({ ...formData, timezone: tz.value })}
                    className={formData.timezone === tz.value ? "bg-accent" : ""}
                  >
                    {tz.label}
                    {formData.timezone === tz.value && <Check className="ml-auto h-4 w-4" />}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>

          <DialogFooter className="pt-2">
            <Button type="button" variant="outline" onClick={onClose}>
              Отмена
            </Button>
            <Button type="submit" disabled={updateMutation.isPending}>
              {updateMutation.isPending ? 'Сохранение...' : 'Сохранить изменения'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
