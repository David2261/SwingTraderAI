import { useQuery } from '@tanstack/react-query'
import { mockApi } from '@/shared/api/mock-api'
import { queryKeys } from '@/shared/api/query-keys'

export function useDashboardOverview() {
  return useQuery({
    queryKey: queryKeys.dashboard.overview,
    queryFn: mockApi.dashboard.getOverview,
    staleTime: 2 * 60 * 1000,
    retry: 1,
  })
}

export function useDashboardSignals() {
  return useQuery({
    queryKey: queryKeys.dashboard.signals,
    queryFn: mockApi.dashboard.getSignals,
    staleTime: 2 * 60 * 1000,
    retry: 1,
  })
}

export function useDashboardHeatmap() {
  return useQuery({
    queryKey: queryKeys.dashboard.heatmap,
    queryFn: mockApi.dashboard.getHeatmap,
    staleTime: 4 * 60 * 1000,
    retry: 1,
  })
}

export function useDashboardExplainability() {
  return useQuery({
    queryKey: queryKeys.dashboard.explainability,
    queryFn: mockApi.dashboard.getExplainability,
    staleTime: 4 * 60 * 1000,
    retry: 1,
  })
}

export function useDashboardAlerts() {
  return useQuery({
    queryKey: queryKeys.dashboard.alerts,
    queryFn: mockApi.dashboard.getAlerts,
    staleTime: 3 * 60 * 1000,
    retry: 1,
  })
}

export function useDashboardActions() {
  return useQuery({
    queryKey: queryKeys.dashboard.quickActions,
    queryFn: mockApi.dashboard.getQuickActions,
    staleTime: 10 * 60 * 1000,
    retry: 1,
  })
}
