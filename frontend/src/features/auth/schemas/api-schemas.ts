import { z } from 'zod'

export const loginRequestSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
})

export const registerRequestSchema = z.object({
  username: z.string().min(3).max(50),
  email: z.string().email(),
  password: z.string().min(6),
  telegram_id: z.number().nullable().optional().default(null),
})

export type RegisterSchema = z.infer<typeof registerRequestSchema>

export const refreshRequestSchema = z.object({
  refresh_token: z.string(),
})

export const userSchema = z.object({
  id: z.string(),
  username: z.string(),
  email: z.string().email(),
  telegram_id: z.number().nullable().optional(),
  role: z.string().optional(),
  first_name: z.string().optional(),
  last_name: z.string().optional(),
  created_at: z.string().optional(),
})

export const authTokenSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string(),
})

export const authResponseSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string(),
  token_type: z.string().optional().default('bearer'),
});

export const authResponseWithUserSchema = authResponseSchema.extend({
  user: userSchema.optional(),
});

export type LoginRequest = z.infer<typeof loginRequestSchema>
export type RegisterRequest = z.infer<typeof registerRequestSchema>
export type AuthResponse = z.infer<typeof authResponseSchema>
export type User = z.infer<typeof userSchema>
