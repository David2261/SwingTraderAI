import { useQuery } from '@tanstack/react-query'
import { mockApi } from '@/shared/api/mock-api'
import { queryKeys } from '@/shared/api/query-keys'

export function useAILabModels() {
  return useQuery({
    queryKey: queryKeys.aiLab.models,
    queryFn: mockApi.aiLab.getModels,
    staleTime: 5 * 60 * 1000,
    retry: 1,
  })
}

export function useAILabTrainingJobs() {
  return useQuery({
    queryKey: queryKeys.aiLab.trainingJobs,
    queryFn: mockApi.aiLab.getTrainingJobs,
    staleTime: 3 * 60 * 1000,
    retry: 1,
  })
}
