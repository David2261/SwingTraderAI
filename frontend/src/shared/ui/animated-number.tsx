import * as React from 'react'
import { cn } from '@/shared/lib/cn'

interface AnimatedNumberProps {
  value: number
  prefix?: string
  suffix?: string
  decimals?: number
  className?: string
}

export function AnimatedNumber({ value, prefix = '', suffix = '', decimals = 2, className }: AnimatedNumberProps) {
  const formatted = value.toFixed(decimals)

  return (
    <span className={cn('font-semibold tabular-nums transition-all duration-300', className)}>
      {prefix}
      {formatted}
      {suffix}
    </span>
  )
}
