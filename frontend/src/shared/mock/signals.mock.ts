const createId = () => `mock-${Math.random().toString(36).slice(2, 10)}`
const timestamp = (minutes: number) => new Date(Date.now() - minutes * 60_000).toISOString()

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
  {
    id: createId(),
    ticker: 'ETH',
    signal: 'BUY',
    confidence: 0.76,
    indicators: ['MACD positive', 'Volume surge'],
    time: timestamp(48),
  },
  {
    id: createId(),
    ticker: 'IMOEX',
    signal: 'STRONG BUY',
    confidence: 0.88,
    indicators: ['Breakout', 'EMA aligned'],
    time: timestamp(60),
  },
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
