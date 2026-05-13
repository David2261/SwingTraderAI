import { z } from 'zod'

export const tickerSchema = z.object({
  id: z.string(),
  symbol: z.string(),
  name: z.string(),
  exchange: z.string(),
  price: z.number(),
  change: z.number(),
  change_percent: z.number(),
  logo_url: z.string().url().optional(),
})

export const tickerDetailSchema = tickerSchema.extend({
  sector: z.string().optional(),
  industry: z.string().optional(),
  market_cap: z.number().optional(),
  short_description: z.string().optional(),
  open: z.number().optional(),
  high: z.number().optional(),
  low: z.number().optional(),
  volume: z.number().optional(),
})

export const candleSchema = z.object({
  timestamp: z.number(),
  open: z.number(),
  high: z.number(),
  low: z.number(),
  close: z.number(),
  volume: z.number(),
})

export const signalSchema = z.object({
  id: z.string(),
  name: z.string(),
  direction: z.enum(['bullish', 'bearish', 'neutral']),
  confidence: z.number().min(0).max(1),
  value: z.number(),
})

export const topMoverSchema = z.object({
  symbol: z.string(),
  name: z.string(),
  price: z.number(),
  change_percent: z.number(),
  volume: z.number(),
  direction: z.enum(['up', 'down']),
})

export type Ticker = z.infer<typeof tickerSchema>
export type TickerDetail = z.infer<typeof tickerDetailSchema>
export type Candle = z.infer<typeof candleSchema>
export type Signal = z.infer<typeof signalSchema>
export type TopMover = z.infer<typeof topMoverSchema>
