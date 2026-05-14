import { useQuery } from '@tanstack/react-query'
import { mockApi } from '@/shared/api/mock-api'
import { queryKeys } from '@/shared/api/query-keys'

export function useSignalsHistory() {
  return useQuery({
    queryKey: queryKeys.signals.history,
    queryFn: mockApi.signals.getHistory,
    staleTime: 3 * 60 * 1000,
    retry: 1,
  })
}
