import { useQuery } from '@tanstack/react-query'
import { mockApi } from '@/shared/api/mock-api'
import { queryKeys } from '@/shared/api/query-keys'

export function useJournalEntries() {
  return useQuery({
    queryKey: queryKeys.journal.entries,
    queryFn: mockApi.journal.getEntries,
    staleTime: 5 * 60 * 1000,
    retry: 1,
  })
}
