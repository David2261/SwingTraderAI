import { cn } from '@/shared/lib/cn'

interface MetricRowProps {
  label: string
  value: string | number
  unit?: string
  trend?: 'up' | 'down' | 'neutral'
  secondary?: string
  className?: string
}

export function MetricRow({ label, value, unit, trend, secondary, className }: MetricRowProps) {
  return (
    <div className={cn('flex items-center justify-between py-3 px-1', className)}>
      <span className="text-sm text-slate-400">{label}</span>
      <div className="flex items-baseline gap-2">
        <span className={cn('text-sm font-semibold', trend === 'up' && 'text-emerald-400', trend === 'down' && 'text-rose-400', trend !== 'up' && trend !== 'down' && 'text-white')}>
          {value}
        </span>
        {unit && <span className="text-xs text-slate-500">{unit}</span>}
        {secondary && <span className="text-xs text-slate-500">{secondary}</span>}
      </div>
    </div>
  )
}
