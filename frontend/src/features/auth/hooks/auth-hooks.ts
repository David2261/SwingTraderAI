import { useMutation, useQuery } from '@tanstack/react-query'
import { apiClient } from '@/shared/api/api-client'
import { useAuthStore } from '../store/auth-store'
import { tokenManager } from '@/shared/api/tokens'
import { errorHandler } from '@/shared/api/error-handler'
import type { LoginSchema, RegisterSchema } from '@/shared/api/api-client'

export function useLogin() {
  const login = useAuthStore((state) => state.login)

  return useMutation({
    mutationFn: async (data: LoginSchema) => {
      const response = await apiClient.auth.login(data)
      tokenManager.setTokens(response.access_token, response.refresh_token)
      return response
    },
    onSuccess: (data) => {
      login(data.user)
    },
    onError: (error) => {
      errorHandler.handleAndShow(error)
    },
  })
}

export function useRegister() {
  const login = useAuthStore((state) => state.login)

  return useMutation({
    mutationFn: async (data: RegisterSchema) => {
      const response = await apiClient.auth.register(data)
      tokenManager.setTokens(response.access_token, response.refresh_token)
      return response
    },
    onSuccess: (data) => {
      login(data.user)
    },
    onError: (error) => {
      errorHandler.handleAndShow(error)
    },
  })
}

export function useLogout() {
  const logout = useAuthStore((state) => state.logout)

  return useMutation({
    mutationFn: apiClient.auth.logout,
    onSuccess: () => {
      logout()
    },
    onError: (error) => {
      // Even if logout fails, clear local state
      logout()
      errorHandler.handleAndShow(error)
    },
  })
}

export function useUser() {
  const { user, isAuthenticated, checkAuth } = useAuthStore()

  const query = useQuery({
    queryKey: ['user'],
    queryFn: apiClient.auth.me,
    enabled: isAuthenticated,
    staleTime: 5 * 60 * 1000, // 5 minutes
    onSuccess: (data) => {
      // Update user data if needed
    },
    onError: () => {
      checkAuth()
    },
  })

  return {
    ...query,
    user: query.data || user,
  }
}

export function useAuth() {
  const { isAuthenticated, isLoading, checkAuth } = useAuthStore()

  return {
    isAuthenticated,
    isLoading,
    checkAuth,
  }
}
