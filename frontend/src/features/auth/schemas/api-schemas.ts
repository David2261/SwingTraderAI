import { z } from 'zod'

export const loginRequestSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
})

export const registerRequestSchema = z.object({
  first_name: z.string().min(1),
  last_name: z.string().min(1),
  email: z.string().email(),
  password: z.string().min(6),
})

export const refreshRequestSchema = z.object({
  refresh_token: z.string(),
})

export const userSchema = z.object({
  id: z.string(),
  email: z.string().email(),
  first_name: z.string(),
  last_name: z.string(),
  created_at: z.string().optional(),
})

export const authTokenSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string(),
})

export const authResponseSchema = authTokenSchema.extend({
  user: userSchema,
})

export type LoginRequest = z.infer<typeof loginRequestSchema>
export type RegisterRequest = z.infer<typeof registerRequestSchema>
export type AuthResponse = z.infer<typeof authResponseSchema>
export type User = z.infer<typeof userSchema>
