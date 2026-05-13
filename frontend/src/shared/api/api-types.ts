import type { ZodIssue } from 'zod'

export interface ApiError {
  message: string
  status?: number
  code?: string
  issues?: ZodIssue[]
}

export class ApiValidationError extends Error {
  public issues: ZodIssue[]

  constructor(message: string, issues: ZodIssue[]) {
    super(message)
    this.name = 'ApiValidationError'
    this.issues = issues
  }
}
