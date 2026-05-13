import { z } from 'zod'
import { tickerSchema } from '@/features/tickers/schemas/api-schemas'

export const watchlistItemSchema = z.object({
  id: z.string(),
  ticker_id: z.string(),
  ticker: tickerSchema,
  added_at: z.string(),
})

export const createWatchlistSchema = z.object({
  ticker_id: z.string(),
})

export type WatchlistItem = z.infer<typeof watchlistItemSchema>
export type CreateWatchlistRequest = z.infer<typeof createWatchlistSchema>
