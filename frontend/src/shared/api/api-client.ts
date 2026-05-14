import { api } from './axios'
import { z } from 'zod'
import { parseResponse } from './schema-utils'
import type {
  AuthResponse,
  Candle,
  CreatePositionRequest,
  CreateWatchlistRequest,
  Indicator,
  IndicatorSummary,
  LoginRequest,
  PortfolioSummary,
  Position,
  RegisterRequest,
  Signal,
  Ticker,
  TickerDetail,
  TopMover,
  UpdatePositionRequest,
  User,
  WatchlistItem,
} from '@/shared/api/api-client-types'
import {
  authResponseSchema,
  loginRequestSchema,
  registerRequestSchema,
  userSchema,
} from '@/features/auth/schemas/api-schemas'
import {
  candleSchema,
  signalSchema,
  tickerDetailSchema,
  tickerSchema,
  topMoverSchema,
} from '@/features/tickers/schemas/api-schemas'
import {
  createWatchlistSchema,
  watchlistItemSchema,
} from '@/features/watchlist/schemas/api-schemas'
import {
  createPositionRequestSchema,
  portfolioSummarySchema,
  positionSchema,
  updatePositionRequestSchema,
} from '@/features/portfolio/schemas/api-schemas'
import { indicatorSchema, indicatorSummarySchema } from '@/features/indicators/schemas/api-schemas'

export const apiClient = {
  auth: {
    login: async (data: LoginRequest) => {
        const request = loginRequestSchema.parse(data)

        const formData = new URLSearchParams()

        formData.append('username', request.email)
        formData.append('password', request.password)
        formData.append('grant_type', 'password')

        const response = await api.post(
        '/auth/login',
        formData,
        {
            headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            },
        }
        )

        return parseResponse<AuthResponse>(
        authResponseSchema,
        response.data
        )
    },


    register: async (data: RegisterRequest) => {
        const request = registerRequestSchema.parse(data)

        const response = await api.post(
            '/auth/register',
            request
        )

        console.log('Register raw response:', response.data)

        return parseResponse<AuthResponse>(
            authResponseSchema,
            response.data
        )
    },

    logout: async () => {
        await api.post('/auth/logout')
    },

    refresh: async () => {
        const response = await api.post('/auth/refresh')

        return parseResponse<AuthResponse>(
        authResponseSchema,
        response.data
        )
    },

    me: async () => {
        const response = await api.get('/users/me')

        return parseResponse<User>(
        userSchema,
        response.data
        )
    },
    },

  tickers: {
    search: async (query: string) => {
      const response = await api.get('/tickers/search', {
        params: { q: query },
      })
      return parseResponse<Ticker[]>(z.array(tickerSchema), response.data)
    },

    getById: async (symbol: string) => {
      const response = await api.get(`/tickers/${symbol}`)
      return parseResponse<TickerDetail>(tickerDetailSchema, response.data)
    },

    getCandles: async (symbol: string, timeframe: string, limit = 100) => {
      const response = await api.get(`/tickers/${symbol}/candles`, {
        params: { timeframe, limit },
      })
      return parseResponse<Candle[]>(z.array(candleSchema), response.data)
    },

    getTopMovers: async () => {
      const response = await api.get('/tickers/top-movers')
      return parseResponse<TopMover[]>(z.array(topMoverSchema), response.data)
    },

    getSignals: async (symbol: string) => {
      const response = await api.get(`/tickers/${symbol}/signals`)
      return parseResponse<Signal[]>(z.array(signalSchema), response.data)
    },
  },

  watchlist: {
    getAll: async () => {
      const response = await api.get('/watchlist')
      return parseResponse<WatchlistItem[]>(z.array(watchlistItemSchema), response.data)
    },

    add: async (data: CreateWatchlistRequest) => {
      const request = createWatchlistSchema.parse(data)
      const response = await api.post('/watchlist', request)
      return parseResponse<WatchlistItem>(watchlistItemSchema, response.data)
    },

    remove: async (id: string) => {
      await api.delete(`/watchlist/${id}`)
    },
  },

  portfolio: {
    getPositions: async () => {
      const response = await api.get('/portfolio/positions')
      return parseResponse<Position[]>(z.array(positionSchema), response.data)
    },

    getSummary: async () => {
      const response = await api.get('/portfolio/summary')
      return parseResponse<PortfolioSummary>(portfolioSummarySchema, response.data)
    },

    addPosition: async (data: CreatePositionRequest) => {
      const request = createPositionRequestSchema.parse(data)
      const response = await api.post('/portfolio/positions', request)
      return parseResponse<Position>(positionSchema, response.data)
    },

    updatePosition: async (id: string, data: UpdatePositionRequest) => {
      const request = updatePositionRequestSchema.parse(data)
      const response = await api.patch(`/portfolio/positions/${id}`, request)
      return parseResponse<Position>(positionSchema, response.data)
    },

    removePosition: async (id: string) => {
      await api.delete(`/portfolio/positions/${id}`)
    },
  },

  indicators: {
    getForTicker: async (symbol: string) => {
      const response = await api.get(`/indicators/${symbol}`)
      return parseResponse<IndicatorSummary>(indicatorSummarySchema, response.data)
    },

    getAll: async () => {
      const response = await api.get('/indicators')
      return parseResponse<Indicator[]>(z.array(indicatorSchema), response.data)
    },
  },
}
