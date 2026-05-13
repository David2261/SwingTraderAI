export const queryKeys = {
  auth: {
    me: ['auth', 'me'] as const,
  },
  tickers: {
    all: ['tickers'] as const,
    search: (query: string) => ['tickers', 'search', query] as const,
    detail: (symbol: string) => ['tickers', 'detail', symbol] as const,
    candles: (symbol: string, timeframe: string) => [
      'tickers',
      'detail',
      symbol,
      'candles',
      timeframe,
    ] as const,
    topMovers: ['tickers', 'top-movers'] as const,
  },
  watchlist: {
    list: ['watchlist'] as const,
    item: (id: string) => ['watchlist', id] as const,
  },
  portfolio: {
    positions: ['portfolio', 'positions'] as const,
    summary: ['portfolio', 'summary'] as const,
  },
  indicators: {
    ticker: (symbol: string) => ['indicators', symbol] as const,
  },
}
