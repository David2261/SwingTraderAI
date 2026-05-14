import {
  mockAnalyticsSummary,
  mockAICopilotHistory,
  mockAIPrompts,
  mockAlerts,
  mockAlertsFeed,
  mockExplainability,
  mockJournalEntries,
  mockMarketHeatmap,
  mockMarketPulse,
  mockMarketSnapshot,
  mockPortfolioPositions,
  mockPortfolioSummary,
  mockScannerResults,
  mockSignalsFeed,
  mockSignalsHistory,
  mockStrategyLibrary,
  mockSupportTopics,
  mockTrainingJobs,
  mockUserProfile,
  mockWatchlistItems,
  mockAILabModels,
} from '@/shared/mock/mock-data'

const delay = (ms = 250) => new Promise((resolve) => setTimeout(resolve, ms))
const fetcher = async <T>(payload: T, ms = 250) => {
  await delay(ms)
  return payload
}

export const mockApi = {
  dashboard: {
    getOverview: () => fetcher({
      summary: mockPortfolioSummary,
      regime: 'Bullish',
      volatility: 'Moderate',
      confidence: 0.87,
      opportunities: [
        { symbol: 'BTC', reason: 'Momentum weakening before resistance', score: 91 },
        { symbol: 'SBER', reason: 'Breakout continuation above 300', score: 84 },
        { symbol: 'IMOEX', reason: 'Approaching key resistance with strong volume', score: 79 },
      ],
    }),
    getSignals: () => fetcher(mockSignalsFeed),
    getHeatmap: () => fetcher(mockMarketHeatmap),
    getExplainability: () => fetcher(mockExplainability),
    getAlerts: () => fetcher(mockAlerts),
    getQuickActions: () => fetcher([
      { id: 'run-scan', label: 'Run Scan', variant: 'secondary' },
      { id: 'analyze-asset', label: 'Analyze Asset', variant: 'default' },
      { id: 'open-backtest', label: 'Open Backtest', variant: 'ghost' },
      { id: 'ask-ai', label: 'Ask AI', variant: 'secondary' },
    ]),
  },
  watchlist: {
    getAll: () => fetcher(mockWatchlistItems),
  },
  portfolio: {
    getPositions: () => fetcher(mockPortfolioPositions),
    getSummary: () => fetcher(mockPortfolioSummary),
  },
  analytics: {
    getSummary: () => fetcher(mockAnalyticsSummary),
    getSnapshot: () => fetcher(mockMarketSnapshot),
    getPulse: () => fetcher(mockMarketPulse),
  },
  ai: {
    getHistory: () => fetcher(mockAICopilotHistory),
    getPrompts: () => fetcher(mockAIPrompts),
  },
  scanner: {
    getResults: () => fetcher(mockScannerResults),
  },
  signals: {
    getHistory: () => fetcher(mockSignalsHistory),
  },
  aiLab: {
    getModels: () => fetcher(mockAILabModels),
    getTrainingJobs: () => fetcher(mockTrainingJobs),
  },
  alerts: {
    getActive: () => fetcher(mockAlertsFeed),
  },
  journal: {
    getEntries: () => fetcher(mockJournalEntries),
  },
  admin: {
    getProfile: () => fetcher(mockUserProfile),
    getSupportTopics: () => fetcher(mockSupportTopics),
    getStrategies: () => fetcher(mockStrategyLibrary),
  },
}
