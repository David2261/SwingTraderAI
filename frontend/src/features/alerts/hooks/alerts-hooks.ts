import { useQuery } from '@tanstack/react-query'
import { mockApi } from '@/shared/api/mock-api'
import { queryKeys } from '@/shared/api/query-keys'

export function useActiveAlerts() {
  return useQuery({
    queryKey: queryKeys.alerts.active,
    queryFn: mockApi.alerts.getActive,
    staleTime: 3 * 60 * 1000,
    retry: 1,
  })
}
