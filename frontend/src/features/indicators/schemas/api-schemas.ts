import { z } from 'zod'
import { tickerSchema } from '@/features/tickers/schemas/api-schemas'

export const indicatorSchema = z.object({
  id: z.string(),
  name: z.string(),
  type: z.enum(['moving_average', 'rsi', 'macd', 'adx', 'bb']),
  value: z.number(),
  signal: z.enum(['bullish', 'bearish', 'neutral']),
  strength: z.number().min(0).max(100),
})

export const indicatorSummarySchema = z.object({
  ticker: tickerSchema,
  indicators: z.array(indicatorSchema),
})

export const signalSchema = z.object({
  id: z.string(),
  description: z.string(),
  direction: z.enum(['bullish', 'bearish', 'neutral']),
  confidence: z.number().min(0).max(1),
})

export type Indicator = z.infer<typeof indicatorSchema>
export type IndicatorSummary = z.infer<typeof indicatorSummarySchema>
export type Signal = z.infer<typeof signalSchema>
