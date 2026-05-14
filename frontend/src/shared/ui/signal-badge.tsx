import { cn } from '@/shared/lib/cn'

interface SignalBadgeProps {
  signal: string
}

const signalStyles: Record<string, string> = {
  'STRONG BUY': 'bg-emerald-500/10 text-emerald-200 ring-emerald-500/25',
  BUY: 'bg-emerald-400/10 text-emerald-200 ring-emerald-400/25',
  NEUTRAL: 'bg-slate-500/10 text-slate-200 ring-slate-500/25',
  SELL: 'bg-rose-500/10 text-rose-200 ring-rose-500/25',
  'STRONG SELL': 'bg-rose-600/10 text-rose-200 ring-rose-600/25',
}

export function SignalBadge({ signal }: SignalBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex rounded-full border px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.2em] ring-1',
        signalStyles[signal] ?? 'bg-slate-600/20 text-slate-100 ring-slate-500/20'
      )}
    >
      {signal}
    </span>
  )
}
