import { z } from 'zod'
import { tickerSchema } from '@/features/tickers/schemas/api-schemas'

export const positionSchema = z.object({
  id: z.string(),
  ticker_id: z.string(),
  ticker: tickerSchema,
  quantity: z.number(),
  avg_price: z.number(),
  current_price: z.number(),
  pnl: z.number(),
  pnl_percent: z.number(),
  allocation_percent: z.number().optional(),
})

export const portfolioSummarySchema = z.object({
  total_value: z.number(),
  day_change_percent: z.number(),
  total_pnl: z.number(),
  win_rate: z.number(),
  positions: z.number(),
})

export const createPositionRequestSchema = z.object({
  ticker_id: z.string(),
  quantity: z.number().min(1),
  avg_price: z.number().positive(),
})

export const updatePositionRequestSchema = z.object({
  quantity: z.number().min(1).optional(),
  avg_price: z.number().positive().optional(),
})

export type Position = z.infer<typeof positionSchema>
export type PortfolioSummary = z.infer<typeof portfolioSummarySchema>
export type CreatePositionRequest = z.infer<typeof createPositionRequestSchema>
export type UpdatePositionRequest = z.infer<typeof updatePositionRequestSchema>
