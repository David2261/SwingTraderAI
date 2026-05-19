import { useMutation, useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { apiClient } from '@/shared/api/api-client'
import { useAuthStore } from '../store/auth-store'
import { tokenManager } from '@/shared/api/tokens'
import { errorHandler } from '@/shared/api/error-handler'
import type { LoginRequest, RegisterRequest } from '../schemas/api-schemas'
import { useEffect } from 'react'


export function useLogin() {
  const login = useAuthStore((state) => state.login)

  return useMutation({
    mutationFn: async (data: LoginRequest) => {
      const response = await apiClient.auth.login(data)
      tokenManager.setTokens(response.access_token, response.refresh_token)
      return response
    },

    onSuccess: async () => {
      try {
        const user = await apiClient.auth.me()
        login(user)
      } catch (error: any) {
        console.error('❌ CRITICAL: Failed to fetch /users/me after login', {
          status: error?.response?.status,
          message: error?.response?.data || error?.message,
          error
        })
      }
    },

    onError: (error: any) => {
      console.error('❌ Login mutation failed:', error?.response?.data || error)
      errorHandler.handleAndShow(error)
    },
  })
}

export function useRegister() {
  const loginAction = useAuthStore((state) => state.login)
  const navigate = useNavigate()

  return useMutation({
    mutationFn: async (data: RegisterRequest) => {
      const response = await apiClient.auth.register(data)
      tokenManager.setTokens(response.access_token, response.refresh_token)
      return response
    },

    onSuccess: async () => {
      try {
        const user = await apiClient.auth.me()
        loginAction(user)
		navigate('/dashboard', { replace: true })
      } catch (error) {
        console.error('Failed to fetch user after registration:', error)
		navigate('/dashboard', { replace: true })
      }
    },

    onError: (error) => {
      console.error('Registration error:', error)
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
    queryFn: () => apiClient.auth.me(),
    enabled: isAuthenticated,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  })

  useEffect(() => {
    if (query.error && isAuthenticated) {
      checkAuth()
    }
  }, [query.error, isAuthenticated, checkAuth])

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
