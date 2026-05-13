import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/shared/api/api-client'
import { queryKeys } from '@/shared/api/query-keys'
import type { Indicator, IndicatorSummary } from '@/shared/api/api-client-types'

export function useIndicatorSummary(symbol: string) {
  return useQuery<IndicatorSummary>({
    queryKey: queryKeys.indicators.ticker(symbol),
    queryFn: () => apiClient.indicators.getForTicker(symbol),
    staleTime: 3 * 60 * 1000,
    refetchOnWindowFocus: false,
    enabled: Boolean(symbol),
  })
}

export function useIndicatorsList() {
  return useQuery<Indicator[]>({
    queryKey: ['indicators', 'list'],
    queryFn: apiClient.indicators.getAll,
    staleTime: 5 * 60 * 1000,
    retry: 2,
  })
}
