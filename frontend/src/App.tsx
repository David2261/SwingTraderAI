import { useEffect } from 'react'
import { useAuthStore } from '@/features/auth/store/auth-store'

export function AppInit() {
  const checkAuth = useAuthStore((s) => s.checkAuth)

  useEffect(() => {
    checkAuth()
  }, [checkAuth])

  return null
}
