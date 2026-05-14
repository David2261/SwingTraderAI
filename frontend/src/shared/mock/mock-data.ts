import type {
  Indicator,
  PortfolioSummary,
  Position,
  Ticker,
  WatchlistItem,
} from '@/shared/api/api-client-types'

const createId = () => `mock-${Math.random().toString(36).slice(2, 10)}`
const timestamp = (minutes: number) => new Date(Date.now() - minutes * 60_000).toISOString()

export const mockTickers: Ticker[] = [
  {
    id: 'btc',
    symbol: 'BTC',
    name: 'Bitcoin',
    exchange: 'Coinbase',
    price: 68840.12,
    change: 1240.45,
    change_percent: 1.84,
    logo_url: 'https://assets.coingecko.com/coins/images/1/large/bitcoin.png',
  },
  {
    id: 'eth',
    symbol: 'ETH',
    name: 'Ethereum',
    exchange: 'Coinbase',
    price: 4160.75,
    change: -18.54,
    change_percent: -0.44,
    logo_url: 'https://assets.coingecko.com/coins/images/279/large/ethereum.png',
  },
  {
    id: 'sber',
    symbol: 'SBER',
    name: 'Sberbank',
    exchange: 'MOEX',
    price: 306.5,
    change: 6.8,
    change_percent: 2.27,
  },
  {
    id: 'gazp',
    symbol: 'GAZP',
    name: 'Gazprom',
    exchange: 'MOEX',
    price: 134.1,
    change: -2.3,
    change_percent: -1.69,
  },
  {
    id: 'imoex',
    symbol: 'IMOEX',
    name: 'IMOEX',
    exchange: 'MOEX',
    price: 2940.45,
    change: 46.1,
    change_percent: 1.59,
  },
  {
    id: 'aapl',
    symbol: 'AAPL',
    name: 'Apple',
    exchange: 'NASDAQ',
    price: 183.72,
    change: 1.24,
    change_percent: 0.68,
  },
  {
    id: 'tsla',
    symbol: 'TSLA',
    name: 'Tesla',
    exchange: 'NASDAQ',
    price: 254.33,
    change: -3.95,
    change_percent: -1.53,
  },
]

export const mockWatchlistItems: WatchlistItem[] = [
  {
    id: createId(),
    ticker_id: 'btc',
    ticker: mockTickers[0],
    added_at: timestamp(120),
  },
  {
    id: createId(),
    ticker_id: 'sber',
    ticker: mockTickers[2],
    added_at: timestamp(240),
  },
  {
    id: createId(),
    ticker_id: 'aapl',
    ticker: mockTickers[5],
    added_at: timestamp(360),
  },
  {
    id: createId(),
    ticker_id: 'tsla',
    ticker: mockTickers[6],
    added_at: timestamp(480),
  },
]

export const mockPortfolioPositions: Position[] = [
  {
    id: createId(),
    ticker_id: 'btc',
    ticker: mockTickers[0],
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
    ticker: mockTickers[1],
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
    ticker: mockTickers[2],
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
    ticker: mockTickers[6],
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
    ticker: mockTickers[5],
    quantity: 78,
    avg_price: 178,
    current_price: 183.72,
    pnl: 445.92,
    pnl_percent: 3.15,
    allocation_percent: 8,
  },
]

export const mockPortfolioSummary: PortfolioSummary = {
  total_value: 171_540,
  day_change_percent: 1.12,
  total_pnl: 36_402,
  win_rate: 78,
  positions: mockPortfolioPositions.length,
}

export const mockMarketHeatmap = [
  { symbol: 'BTC', name: 'Bitcoin', status: 'Bullish', change: 1.84, active: true },
  { symbol: 'ETH', name: 'Ethereum', status: 'Bearish', change: -0.44, active: false },
  { symbol: 'SBER', name: 'Sberbank', status: 'Bullish', change: 2.27, active: true },
  { symbol: 'GAZP', name: 'Gazprom', status: 'Bearish', change: -1.69, active: false },
  { symbol: 'IMOEX', name: 'IMOEX', status: 'Neutral', change: 1.59, active: false },
  { symbol: 'AAPL', name: 'Apple', status: 'Bullish', change: 0.68, active: false },
]

export const mockSignalsFeed = [
  {
    id: createId(),
    ticker: 'BTC',
    signal: 'BUY',
    confidence: 0.91,
    indicators: ['EMA50 > EMA200', 'RSI recover', 'Volume surge'],
    time: timestamp(12),
  },
  {
    id: createId(),
    ticker: 'SBER',
    signal: 'STRONG BUY',
    confidence: 0.85,
    indicators: ['Breakout', 'MACD bullish'],
    time: timestamp(24),
  },
  {
    id: createId(),
    ticker: 'TSLA',
    signal: 'SELL',
    confidence: 0.79,
    indicators: ['RSI overbought', 'Momentum fade'],
    time: timestamp(35),
  },
]

export const mockExplainability = [
  {
    id: createId(),
    title: 'BTC bullish continuation',
    reasons: [
      'EMA50 crossed above EMA200',
      'RSI recovered from oversold territory',
      'volume increased by 28% on the breakout candle',
    ],
  },
  {
    id: createId(),
    title: 'SBER momentum signal',
    reasons: [
      'Price holding above 20-day moving average',
      'MACD histogram turning positive',
      'support anchored at previous resistance',
    ],
  },
]

export const mockAlerts = [
  {
    id: createId(),
    label: 'Breakout Alert',
    description: 'GAZP pushed above the 55-day range on high volume.',
    severity: 'high',
    time: timestamp(18),
  },
  {
    id: createId(),
    label: 'RSI Warning',
    description: 'ETH RSI entered overbought territory near resistance.',
    severity: 'medium',
    time: timestamp(30),
  },
  {
    id: createId(),
    label: 'AI Risk Signal',
    description: 'Portfolio risk ratio climbed under rising volatility.',
    severity: 'low',
    time: timestamp(42),
  },
]

export const mockScannerResults = [
  {
    id: createId(),
    symbol: 'IMOEX',
    confidence: 0.88,
    signal: 'Breakout',
    indicators: ['RSI oversold', 'EMA crossover'],
    note: 'Momentum structure supports continuation.',
  },
  {
    id: createId(),
    symbol: 'AAPL',
    confidence: 0.81,
    signal: 'MACD Bullish',
    indicators: ['MACD bullish', 'volume spike'],
    note: 'Short-term momentum is warming up.',
  },
  {
    id: createId(),
    symbol: 'GAZP',
    confidence: 0.74,
    signal: 'Volume Spike',
    indicators: ['volume spike', 'price rejection'],
    note: 'Watch for follow-through above 136.',
  },
]

export const mockAnalyticsSummary = {
  signalDistribution: [
    { label: 'Strong Buy', value: 22 },
    { label: 'Buy', value: 30 },
    { label: 'Neutral', value: 28 },
    { label: 'Sell', value: 12 },
    { label: 'Strong Sell', value: 8 },
  ],
  winRate: 74,
  avgConfidence: 0.82,
  volatilityIndex: 37,
}

export const mockAICopilotHistory = [
  { id: createId(), role: 'assistant', message: 'Ready to help you uncover the next trading edge.' },
  { id: createId(), role: 'user', message: 'Analyze BTC trend' },
  { id: createId(), role: 'assistant', message: 'BTC remains in a bullish regime, but watch the 68.6k resistance band for possible short-term consolidation.' },
]

export const mockAIPrompts = [
  'Analyze BTC trend',
  'Find oversold MOEX stocks',
  'Explain current portfolio risk',
  'Compare SBER vs IMOEX momentum',
]

export const mockSignalsHistory = [
  {
    id: createId(),
    symbol: 'ETH',
    category: 'BUY',
    confidence: 0.86,
    time: timestamp(90),
    note: 'MACD line moved above signal line after consolidation.',
  },
  {
    id: createId(),
    symbol: 'AAPL',
    category: 'SELL',
    confidence: 0.72,
    time: timestamp(120),
    note: 'Overhead supply testing near 185 resistance.',
  },
  {
    id: createId(),
    symbol: 'SBER',
    category: 'STRONG BUY',
    confidence: 0.93,
    time: timestamp(150),
    note: 'Breakout confirmed with follow-through volume.',
  },
]

export const mockAILabModels = [
  {
    id: createId(),
    name: 'AlphaTrend v2',
    accuracy: 0.82,
    precision: 0.79,
    recall: 0.77,
    sharpe: 1.86,
    status: 'active',
  },
  {
    id: createId(),
    name: 'PatternPulse',
    accuracy: 0.76,
    precision: 0.72,
    recall: 0.69,
    sharpe: 1.34,
    status: 'training',
  },
]

export const mockTrainingJobs = [
  {
    id: createId(),
    model: 'PatternPulse',
    status: 'running',
    progress: 66,
    started_at: timestamp(38),
  },
  {
    id: createId(),
    model: 'AlphaTrend v2',
    status: 'queued',
    progress: 0,
    started_at: timestamp(120),
  },
]

export const mockSystemStatus = [
  { id: createId(), label: 'API latency', value: '72 ms', status: 'good' },
  { id: createId(), label: 'Model queue', value: '2 jobs', status: 'warning' },
  { id: createId(), label: 'Database health', value: 'operational', status: 'good' },
]

export const mockJournalEntries = [
  {
    id: createId(),
    title: 'SBER breakout thesis',
    emotion: 'focused',
    notes: 'Position opened on daily breakout with support from RSI and MACD.',
    time: timestamp(260),
  },
  {
    id: createId(),
    title: 'BTC range observation',
    emotion: 'cautious',
    notes: 'Watching the 68.5k level for either consolidation or continuation.',
    time: timestamp(320),
  },
]

export const mockUserProfile = {
  username: 'ai.trader',
  email: 'ai.trader@swingtrader.ai',
  role: 'admin',
  joined_at: timestamp(720),
}

export const mockSupportTopics = [
  { id: createId(), title: 'Integrate custom strategy signals', status: 'open' },
  { id: createId(), title: 'Request for new AI explainability views', status: 'in-progress' },
]

export const mockStrategyLibrary = [
  { id: createId(), name: 'Momentum Fusion', description: 'Blend EMA, RSI and volume to find high-conviction entries.', status: 'active' },
  { id: createId(), name: 'Mean Reversion', description: 'Target pullback setups in range-bound securities.', status: 'ready' },
]

export const mockAlertsFeed = [
  {
    id: createId(),
    symbol: 'BTC',
    label: 'Price crossed VWAP',
    severity: 'medium',
    time: timestamp(15),
  },
  {
    id: createId(),
    symbol: 'IMOEX',
    label: 'Volume breakout detected',
    severity: 'high',
    time: timestamp(27),
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
