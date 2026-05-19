import type { Position, PortfolioSummary, Ticker } from '@/shared/api/api-client-types'

const createId = () => `mock-${Math.random().toString(36).slice(2, 10)}`

export function generatePortfolioPositions(tickers: Ticker[]): Position[] {
  return [
    {
      id: createId(),
      ticker_id: 'btc',
      ticker: tickers[0],
      quantity: 0.54,
      avg_price: 63400,
      current_price: 68840.12,
      pnl: 29397.87,
      pnl_percent: 8.47,
      allocation_percent: 42,
    },
    {
      id: createId(),
      ticker_id: 'eth',
      ticker: tickers[1],
      quantity: 4.3,
      avg_price: 3750,
      current_price: 4160.75,
      pnl: 1742.23,
      pnl_percent: 10.86,
      allocation_percent: 18,
    },
    {
      id: createId(),
      ticker_id: 'sber',
      ticker: tickers[2],
      quantity: 180,
      avg_price: 287.5,
      current_price: 306.5,
      pnl: 3420,
      pnl_percent: 6.34,
      allocation_percent: 12,
    },
    {
      id: createId(),
      ticker_id: 'tsla',
      ticker: tickers[6],
      quantity: 22,
      avg_price: 246.7,
      current_price: 254.33,
      pnl: 166.26,
      pnl_percent: 3.04,
      allocation_percent: 9,
    },
    {
      id: createId(),
      ticker_id: 'aapl',
      ticker: tickers[5],
      quantity: 78,
      avg_price: 178,
      current_price: 183.72,
      pnl: 445.92,
      pnl_percent: 3.15,
      allocation_percent: 8,
    },
  ]
}

export const generatePortfolioSummary = (): PortfolioSummary => ({
  total_value: 171_540,
  day_change_percent: 1.12,
  total_pnl: 36_402,
  win_rate: 78,
  positions: 5,
})
