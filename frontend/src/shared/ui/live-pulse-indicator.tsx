import { cn } from '@/shared/lib/cn'

interface LivePulseIndicatorProps {
  active?: boolean
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

export function LivePulseIndicator({ active = true, size = 'md', className }: LivePulseIndicatorProps) {
  const sizeClasses = {
    sm: 'h-2 w-2',
    md: 'h-3 w-3',
    lg: 'h-4 w-4',
  }

  const pulseSize = {
    sm: 'h-2 w-2',
    md: 'h-3 w-3',
    lg: 'h-4 w-4',
  }

  return (
    <div className={cn('relative inline-block', className)}>
      {active && (
        <>
          <div
            className={cn(
              pulseSize[size],
              'absolute inset-0 animate-pulse rounded-full bg-emerald-400/50'
            )}
          />
          <div
            className={cn(
              'animate-ping absolute inset-0 rounded-full bg-emerald-400',
              size === 'sm' && 'h-2 w-2',
              size === 'md' && 'h-3 w-3',
              size === 'lg' && 'h-4 w-4'
            )}
          />
        </>
      )}
      <div
        className={cn(
          sizeClasses[size],
          'relative rounded-full transition-colors',
          active ? 'bg-emerald-500' : 'bg-slate-600'
        )}
      />
    </div>
  )
}
