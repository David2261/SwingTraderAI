import { cn } from '@/shared/lib/cn'

interface LoadingSkeletonProps {
  rows?: number
  className?: string
}

export function LoadingSkeleton({ rows = 3, className }: LoadingSkeletonProps) {
  return (
    <div className={cn('space-y-3', className)}>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="space-y-2">
          <div className="h-4 w-full rounded bg-slate-800 animate-pulse" />
          <div className="h-3 w-3/4 rounded bg-slate-800 animate-pulse" />
        </div>
      ))}
    </div>
  )
}
