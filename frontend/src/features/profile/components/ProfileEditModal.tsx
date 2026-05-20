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

interface ProfileEditModalProps {
  isOpen: boolean
  onClose: () => void
  initialData?: User | null
}

export function ProfileEditModal({ isOpen, onClose, initialData }: ProfileEditModalProps) {
  const queryClient = useQueryClient()

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    telegram_id: '',
    timezone: 'Europe/Moscow',
  })

  const updateMutation = useMutation({
    mutationFn: (data: Partial<User>) => apiClient.profile.update(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['user', 'profile'] })
      onClose()
    },
  })

  useEffect(() => {
    if (initialData) {
      setFormData({
        username: initialData.username,
        email: initialData.email,
        telegram_id: initialData.telegram_id?.toString() || '',
        timezone: initialData.timezone || 'Europe/Moscow',
      })
    }
  }, [initialData])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const payload: Partial<User> = {
      username: formData.username,
      email: formData.email,
      telegram_id: formData.telegram_id ? Number(formData.telegram_id) : undefined,
      timezone: formData.timezone,
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
          <div className="space-y-2">
            <Label htmlFor="username">Имя пользователя</Label>
            <Input
              id="username"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="telegram_id">Telegram ID</Label>
            <Input
              id="telegram_id"
              type="number"
              placeholder="123456789"
              value={formData.telegram_id}
              onChange={(e) => setFormData({ ...formData, telegram_id: e.target.value })}
            />
          </div>

          <DialogFooter>
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
