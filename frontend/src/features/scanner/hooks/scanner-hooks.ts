import { useQuery } from '@tanstack/react-query'
import { mockApi } from '@/shared/api/mock-api'
import { queryKeys } from '@/shared/api/query-keys'

export function useScannerResults() {
  return useQuery({
    queryKey: queryKeys.scanner.results,
    queryFn: mockApi.scanner.getResults,
    staleTime: 3 * 60 * 1000,
    retry: 1,
  })
}
