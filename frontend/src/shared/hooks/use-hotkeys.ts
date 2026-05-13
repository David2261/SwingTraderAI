import { useEffect } from 'react'

export function useHotkey(keys: string, callback: () => void) {
  useEffect(() => {
    const handleKeydown = (event: KeyboardEvent) => {
      if (event.key.toLowerCase() === keys.toLowerCase()) {
        callback()
      }
    }

    window.addEventListener('keydown', handleKeydown)
    return () => window.removeEventListener('keydown', handleKeydown)
  }, [callback, keys])
}
