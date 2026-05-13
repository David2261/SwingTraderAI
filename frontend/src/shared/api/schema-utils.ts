import { type ZodSchema } from 'zod'
import { ApiValidationError } from './api-types'

export function parseResponse<T>(schema: ZodSchema<T>, data: unknown): T {
  const result = schema.safeParse(data)

  if (!result.success) {
    throw new ApiValidationError('Response validation failed', result.error.issues)
  }

  return result.data
}
