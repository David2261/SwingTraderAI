import { cn } from '@/shared/lib/cn'

interface MarketHeatBadgeProps {
  status: 'Bullish' | 'Bearish' | 'Neutral'
  active?: boolean
}

const heatStyles: Record<string, string> = {
  Bullish: 'bg-emerald-500/10 text-emerald-200 ring-emerald-500/20',
  Bearish: 'bg-rose-500/10 text-rose-200 ring-rose-500/20',
  Neutral: 'bg-slate-600/10 text-slate-200 ring-slate-600/20',
}

export function MarketHeatBadge({ status, active = false }: MarketHeatBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-wide ring-1',
        heatStyles[status],
        active && 'animate-pulse'
      )}
    >
      <span className={cn('h-2.5 w-2.5 rounded-full', status === 'Bullish' ? 'bg-emerald-300' : status === 'Bearish' ? 'bg-rose-300' : 'bg-slate-400')} />
      {status}
    </span>
  )
}
