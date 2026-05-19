import * as React from 'react'
import { cn } from '@/shared/lib/cn'

interface MarketStatusBadgeProps {
  status: 'bullish' | 'bearish' | 'neutral' | 'volatility' | 'consolidation'
  className?: string
}

export function MarketStatusBadge({ status, className }: MarketStatusBadgeProps) {
  const statusConfig = {
    bullish: {
      bg: 'bg-emerald-950/80',
      border: 'border-emerald-900/50',
      text: 'text-emerald-400',
      dot: 'bg-emerald-500',
    },
    bearish: {
      bg: 'bg-rose-950/80',
      border: 'border-rose-900/50',
      text: 'text-rose-400',
      dot: 'bg-rose-500',
    },
    neutral: {
      bg: 'bg-slate-800/80',
      border: 'border-slate-700/50',
      text: 'text-slate-400',
      dot: 'bg-slate-500',
    },
    volatility: {
      bg: 'bg-orange-950/80',
      border: 'border-orange-900/50',
      text: 'text-orange-400',
      dot: 'bg-orange-500',
    },
    consolidation: {
      bg: 'bg-blue-950/80',
      border: 'border-blue-900/50',
      text: 'text-blue-400',
      dot: 'bg-blue-500',
    },
  }

  const config = statusConfig[status]
  const labels = {
    bullish: 'Bullish',
    bearish: 'Bearish',
    neutral: 'Neutral',
    volatility: 'Volatility',
    consolidation: 'Consolidation',
  }

  return (
    <div className={cn('inline-flex items-center gap-2 rounded-full border px-3 py-1', config.bg, config.border, className)}>
      <div className={cn('h-1.5 w-1.5 rounded-full', config.dot)} />
      <span className={cn('text-xs font-semibold uppercase tracking-[0.12em]', config.text)}>
        {labels[status]}
      </span>
    </div>
  )
}
