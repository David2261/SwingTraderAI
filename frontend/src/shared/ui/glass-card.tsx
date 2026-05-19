import * as React from 'react'
import { cn } from '@/shared/lib/cn'

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
  glow?: boolean
}

export function GlassCard({ children, glow = false, className, ...props }: GlassCardProps) {
  return (
    <div
      className={cn(
        'rounded-3xl border border-slate-800/90 bg-slate-950/70 backdrop-blur-sm',
        glow && 'shadow-[0_0_20px_rgba(59,130,246,0.15)] border-slate-800/50',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}
