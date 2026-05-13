import { toast } from 'sonner'
import type { AxiosError } from 'axios'

export interface ApiError {
  message: string
  code?: string
  status?: number
}

export const errorHandler = {
  handle: (error: unknown): ApiError => {
    if (error instanceof Error) {
      const axiosError = error as AxiosError

      if (axiosError.response) {
        const status = axiosError.response.status
        const data = axiosError.response.data as any

        switch (status) {
          case 400:
            return {
              message: data?.message || 'Bad request',
              code: data?.code,
              status,
            }
          case 401:
            return {
              message: 'Unauthorized',
              status,
            }
          case 403:
            return {
              message: 'Forbidden',
              status,
            }
          case 404:
            return {
              message: 'Not found',
              status,
            }
          case 422:
            return {
              message: data?.message || 'Validation error',
              code: data?.code,
              status,
            }
          case 500:
            return {
              message: 'Internal server error',
              status,
            }
          default:
            return {
              message: data?.message || 'An error occurred',
              status,
            }
        }
      }

      if (axiosError.request) {
        return {
          message: 'Network error',
        }
      }
    }

    return {
      message: 'An unexpected error occurred',
    }
  },

  showToast: (error: ApiError): void => {
    toast.error(error.message)
  },

  handleAndShow: (error: unknown): ApiError => {
    const apiError = errorHandler.handle(error)
    errorHandler.showToast(apiError)
    return apiError
  },
}
