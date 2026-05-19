import * as React from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from './card'
import { cn } from '@/shared/lib/cn'

interface SectionCardProps {
  title: string
  description?: string
  actions?: React.ReactNode
  children?: React.ReactNode
  className?: string
}

export function SectionCard({
  title,
  description,
  actions,
  children,
  className,
}: SectionCardProps) {
  return (
    <Card className={cn('overflow-hidden border-2 border-slate-800/80 shadow-[0_20px_80px_-40px_rgba(0,0,0,0.45)]', className)}>
      <CardHeader className="flex flex-col gap-2 bg-slate-950/80 px-6 py-5 backdrop-blur-sm">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <CardTitle className="text-base tracking-tight text-white">{title}</CardTitle>
          {actions && <div className="flex items-center gap-2">{actions}</div>}
        </div>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent className="px-6 py-5">{children}</CardContent>
    </Card>
  )
}
