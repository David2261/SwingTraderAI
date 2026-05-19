import type { WatchlistItem, Ticker } from '@/shared/api/api-client-types'

const createId = () => `mock-${Math.random().toString(36).slice(2, 10)}`
const timestamp = (minutes: number) => new Date(Date.now() - minutes * 60_000).toISOString()

export function generateWatchlistItems(tickers: Ticker[]): WatchlistItem[] {
  return [
    {
      id: createId(),
      ticker_id: 'btc',
      ticker: tickers[0],
      added_at: timestamp(120),
    },
    {
      id: createId(),
      ticker_id: 'sber',
      ticker: tickers[2],
      added_at: timestamp(240),
    },
    {
      id: createId(),
      ticker_id: 'aapl',
      ticker: tickers[5],
      added_at: timestamp(360),
    },
    {
      id: createId(),
      ticker_id: 'tsla',
      ticker: tickers[6],
      added_at: timestamp(480),
    },
    {
      id: createId(),
      ticker_id: 'eth',
      ticker: tickers[1],
      added_at: timestamp(600),
    },
  ]
}

export const mockMarketHeatmap = [
  { id: 'btc-heat', symbol: 'BTC', name: 'Bitcoin', regime: 'Bullish', change: 1.84, active: true },
  { id: 'eth-heat', symbol: 'ETH', name: 'Ethereum', regime: 'Neutral', change: -0.44, active: false },
  { id: 'sber-heat', symbol: 'SBER', name: 'Sberbank', regime: 'Bullish', change: 2.27, active: true },
  { id: 'gazp-heat', symbol: 'GAZP', name: 'Gazprom', regime: 'Bearish', change: -1.69, active: false },
  { id: 'imoex-heat', symbol: 'IMOEX', name: 'IMOEX', regime: 'Neutral', change: 1.59, active: false },
  { id: 'aapl-heat', symbol: 'AAPL', name: 'Apple', regime: 'Bullish', change: 0.68, active: false },
  { id: 'tsla-heat', symbol: 'TSLA', name: 'Tesla', regime: 'Bearish', change: -1.53, active: false },
  { id: 'nvda-heat', symbol: 'NVDA', name: 'Nvidia', regime: 'Bullish', change: 2.14, active: true },
]
