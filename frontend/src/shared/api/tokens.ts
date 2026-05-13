import { storage } from '@/shared/lib/storage'

export const tokenManager = {
  getAccessToken: (): string | null => {
    return storage.get<string>('access_token')
  },

  getRefreshToken: (): string | null => {
    return storage.get<string>('refresh_token')
  },

  setTokens: (accessToken: string, refreshToken: string): void => {
    storage.set('access_token', accessToken)
    storage.set('refresh_token', refreshToken)
  },

  clearTokens: (): void => {
    storage.remove('access_token')
    storage.remove('refresh_token')
  },

  isAuthenticated: (): boolean => {
    return !!tokenManager.getAccessToken()
  },
}
