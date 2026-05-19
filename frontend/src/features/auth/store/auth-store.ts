import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'
import { tokenManager } from '@/shared/api/tokens'
import type { User } from '../schemas/api-schemas'

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
      (set, _) => ({
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

            if (!hasToken) {
                set({
                user: null,
                isAuthenticated: false,
                isLoading: false,
                })

                return false
            }

            set({
                isAuthenticated: true,
                isLoading: false,
            })

            return true
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
