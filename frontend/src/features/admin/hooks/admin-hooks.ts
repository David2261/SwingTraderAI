import { useQuery } from '@tanstack/react-query'
import { mockApi } from '@/shared/api/mock-api'
import { queryKeys } from '@/shared/api/query-keys'

export function useAdminProfile() {
  return useQuery({
    queryKey: queryKeys.admin.profile,
    queryFn: mockApi.admin.getProfile,
    staleTime: 10 * 60 * 1000,
    retry: 1,
  })
}

export function useAdminSupportTopics() {
  return useQuery({
    queryKey: queryKeys.admin.support,
    queryFn: mockApi.admin.getSupportTopics,
    staleTime: 10 * 60 * 1000,
    retry: 1,
  })
}

export function useAdminStrategies() {
  return useQuery({
    queryKey: queryKeys.admin.strategies,
    queryFn: mockApi.admin.getStrategies,
    staleTime: 10 * 60 * 1000,
    retry: 1,
  })
}
