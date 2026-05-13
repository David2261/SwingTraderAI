import { useAuthStore } from './store/auth-store'
import { apiClient } from '@/shared/api/api-client'
import { tokenManager } from '@/shared/api/tokens'

export async function initAuth() {
  const hasToken = tokenManager.isAuthenticated()

  if (!hasToken) {
    useAuthStore.setState({
      isAuthenticated: false,
      isLoading: false,
    })
    return
  }

  try {
    const user = await apiClient.auth.me()

    useAuthStore.setState({
      user,
      isAuthenticated: true,
      isLoading: false,
    })
  } catch {
    tokenManager.clearTokens()
    useAuthStore.setState({
      user: null,
      isAuthenticated: false,
      isLoading: false,
    })
  }
}
