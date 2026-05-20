import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/shared/api/api-client'
import type { User } from '@/shared/api/api-client-types'

export const useUserProfile = () => {
  return useQuery({
    queryKey: ['user', 'profile'],
    queryFn: apiClient.profile.get,
    staleTime: 1000 * 60 * 5,
    gcTime: 1000 * 60 * 15,
    retry: 1,
  })
}

export const useUpdateUserProfile = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: Partial<User>) => apiClient.profile.update(data),
    onSuccess: () => {
      // Обновляем кэш профиля после успешного изменения
      queryClient.invalidateQueries({ queryKey: ['user', 'profile'] })
    },
  })
}
