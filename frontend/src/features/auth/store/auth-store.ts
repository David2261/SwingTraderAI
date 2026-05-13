import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { tokenManager } from '@/shared/api/tokens'
import type { User } from '@/shared/api/api-client'

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (user: User) => void
  logout: () => void
  setLoading: (loading: boolean) => void
  checkAuth: () => boolean
}

export const useAuthStore = create<AuthState>()(
  devtools(
    persist(
      (set, get) => ({
        user: null,
        isAuthenticated: false,
        isLoading: true,

        login: (user: User) => {
          set({ user, isAuthenticated: true, isLoading: false })
        },

        logout: () => {
          tokenManager.clearTokens()
          set({ user: null, isAuthenticated: false, isLoading: false })
        },

        setLoading: (loading: boolean) => {
          set({ isLoading: loading })
        },

        checkAuth: () => {
          const hasToken = tokenManager.isAuthenticated()
          set({ isAuthenticated: hasToken, isLoading: false })
          return hasToken
        },
      }),
      {
        name: 'auth-storage',
        partialize: (state) => ({
          user: state.user,
          isAuthenticated: state.isAuthenticated,
        }),
      }
    ),
    {
      name: 'auth-store',
    }
  )
)
