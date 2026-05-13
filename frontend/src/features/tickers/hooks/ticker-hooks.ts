import { useQuery, useQueryClient } from '@tanstack/react-query'
import { apiClient } from '@/shared/api/api-client'
import { queryKeys } from '@/shared/api/query-keys'
import type { Candle, Signal, Ticker, TickerDetail, TopMover } from '@/shared/api/api-client-types'

export function useTickerSearch(query: string) {
  return useQuery({
    queryKey: queryKeys.tickers.search(query),
    queryFn: () => apiClient.tickers.search(query),
    enabled: query.length > 0,
    staleTime: 2 * 60 * 1000,
    retry: 2,
    keepPreviousData: true,
  })
}

export function useTickerDetail(symbol: string) {
  return useQuery({
    queryKey: queryKeys.tickers.detail(symbol),
    queryFn: () => apiClient.tickers.getById(symbol),
    staleTime: 5 * 60 * 1000,
    retry: 2,
    enabled: Boolean(symbol),
  })
}

export function useTickerCandles(symbol: string, timeframe: string) {
  return useQuery({
    queryKey: queryKeys.tickers.candles(symbol, timeframe),
    queryFn: () => apiClient.tickers.getCandles(symbol, timeframe),
    staleTime: 2 * 60 * 1000,
    refetchInterval: 10000,
    enabled: Boolean(symbol),
    keepPreviousData: true,
  })
}

export function useTopMovers() {
  return useQuery<TopMover[]>({
    queryKey: queryKeys.tickers.topMovers,
    queryFn: apiClient.tickers.getTopMovers,
    staleTime: 3 * 60 * 1000,
    retry: 2,
  })
}

export function useTickerSignals(symbol: string) {
  return useQuery<Signal[]>({
    queryKey: queryKeys.tickers.detail(symbol).concat('signals') as const,
    queryFn: () => apiClient.tickers.getSignals(symbol),
    staleTime: 2 * 60 * 1000,
    enabled: Boolean(symbol),
  })
}

export function usePrefetchTicker(symbol: string, timeframe: string) {
  const queryClient = useQueryClient()

  return () => {
    if (!symbol) return

    queryClient.prefetchQuery(queryKeys.tickers.detail(symbol), () => apiClient.tickers.getById(symbol))
    queryClient.prefetchQuery(queryKeys.tickers.candles(symbol, timeframe), () => apiClient.tickers.getCandles(symbol, timeframe))
  }
}
