import type {
  Indicator
} from '@/shared/api/api-client-types'

import { mockTickers } from './tickers.mock'
import { generatePortfolioPositions, generatePortfolioSummary } from './portfolio.mock'
import { generateWatchlistItems, mockMarketHeatmap } from './watchlist.mock'
import {
  mockSignalsFeed,
  mockSignalsHistory,
  mockScannerResults,
  mockExplainability,
} from './signals.mock'
import {
  mockPredictions,
  mockAILabModels,
  mockTrainingJobs,
} from './predictions.mock'
import {
  mockAlerts,
  mockAiMarketBriefing,
  mockAICopilotHistory,
  mockAIPrompts,
  mockAnalyticsSummary,
  mockSystemStatus,
  mockStrategyLibrary,
  mockJournalEntries,
  mockUserProfile,
  mockSupportTopics,
} from './ai.mock'

// Re-export organized data
export { mockTickers }
export { generatePortfolioPositions, generatePortfolioSummary }
export { generateWatchlistItems, mockMarketHeatmap }
export {
  mockSignalsFeed,
  mockSignalsHistory,
  mockScannerResults,
  mockExplainability,
}
export {
  mockPredictions,
  mockAILabModels,
  mockTrainingJobs,
}
export {
  mockAlerts,
  mockAiMarketBriefing,
  mockAICopilotHistory,
  mockAIPrompts,
  mockAnalyticsSummary,
  mockSystemStatus,
  mockStrategyLibrary,
  mockJournalEntries,
  mockUserProfile,
  mockSupportTopics,
}

let idCounter = 1000

export const createId = (): string => {
  return `mock_${++idCounter}_${Date.now().toString().slice(-6)}`
}

export const timestamp = (minutesAgo: number = 0): string => {
  const date = new Date(Date.now() - minutesAgo * 60 * 1000)
  return date.toISOString()
}

// Lazy generators for page-level data
export const mockPortfolioPositions = generatePortfolioPositions(mockTickers)
export const mockPortfolioSummary = generatePortfolioSummary()
export const mockWatchlistItems = generateWatchlistItems(mockTickers)


export const mockAlertsFeed = [
  {
    id: createId(),
    symbol: 'IMOEX',
    label: 'Volume breakout detected',
    severity: 'high' as const,
    time: timestamp(27),
    message: 'Unusual volume spike on IMOEX index',
  },
  {
    id: createId(),
    symbol: 'SBER',
    label: 'Price target reached',
    severity: 'medium' as const,
    time: timestamp(45),
    message: 'SBER hit resistance level at 312 ₽',
  },
  {
    id: createId(),
    symbol: 'BTC',
    label: 'RSI overbought',
    severity: 'low' as const,
    time: timestamp(78),
    message: 'BTC RSI(14) above 75 — possible short-term pullback',
  },
]

export const mockMarketPulse = [
  { id: createId(), label: 'SBER', value: 82, color: 'bg-positive/20 text-positive' },
  { id: createId(), label: 'ETH', value: 49, color: 'bg-neutral/20 text-neutral' },
]

export const mockIndicatorSummary: Indicator[] = [
  { id: createId(), name: 'EMA50', type: 'moving_average', value: 68.6, signal: 'bullish', strength: 88 },
  { id: createId(), name: 'RSI', type: 'rsi', value: 64.3, signal: 'neutral', strength: 54 },
  { id: createId(), name: 'MACD', type: 'macd', value: 0.12, signal: 'bullish', strength: 72 },
]

export const mockMarketSnapshot = [
  { id: createId(), symbol: 'BTC', price: 68840.12, change_percent: 1.84 },
  { id: createId(), symbol: 'ETH', price: 4160.75, change_percent: -0.44 },
  { id: createId(), symbol: 'AAPL', price: 183.72, change_percent: 0.68 },
]
