const createId = () => `mock-${Math.random().toString(36).slice(2, 10)}`
const timestamp = (minutes: number) => new Date(Date.now() - minutes * 60_000).toISOString()

export const mockPredictions = [
  {
    id: createId(),
    symbol: 'BTC',
    prediction: 'bullish',
    probability: 0.78,
    confidence: 0.91,
    features: ['EMA', 'RSI', 'Volume'],
    time: timestamp(5),
  },
  {
    id: createId(),
    symbol: 'SBER',
    prediction: 'bullish',
    probability: 0.85,
    confidence: 0.88,
    features: ['Breakout', 'MACD', 'Support'],
    time: timestamp(15),
  },
  {
    id: createId(),
    symbol: 'TSLA',
    prediction: 'bearish',
    probability: 0.72,
    confidence: 0.79,
    features: ['RSI', 'Momentum', 'Resistance'],
    time: timestamp(25),
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
  {
    id: createId(),
    name: 'MarketSense',
    accuracy: 0.79,
    precision: 0.76,
    recall: 0.73,
    sharpe: 1.62,
    status: 'active',
  },
]

export const mockTrainingJobs = [
  {
    id: createId(),
    name: 'PatternPulse v1.2',
    model: 'PatternPulse',
    status: 'running',
    progress: 66,
    started_at: timestamp(38),
    description: 'Retraining with Q2 market data',
  },
  {
    id: createId(),
    name: 'AlphaTrend v3 (beta)',
    model: 'AlphaTrend v2',
    status: 'queued',
    progress: 0,
    started_at: timestamp(120),
    description: 'Testing new ensemble approach',
  },
]
