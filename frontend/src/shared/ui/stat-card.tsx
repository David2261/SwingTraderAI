import * as React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from './card'
import { cn } from '@/shared/lib/cn'

interface StatCardProps {
  title: string
  value: string | number
  change?: {
    value: number
    label: string
  }
  icon?: React.ReactNode
  className?: string
}

export function StatCard({
  title,
  value,
  change,
  icon,
  className,
}: StatCardProps) {
  return (
    <Card className={className}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {icon && <div className="text-muted-foreground">{icon}</div>}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {change && (
          <p
            className={cn(
              'text-xs',
              change.value >= 0
                ? 'text-positive'
                : 'text-negative'
            )}
          >
            {change.value >= 0 ? '+' : ''}
            {change.value}% {change.label}
          </p>
        )}
      </CardContent>
    </Card>
  )
}
