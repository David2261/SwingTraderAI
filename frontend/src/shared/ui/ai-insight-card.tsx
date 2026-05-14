import { Sparkles } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from './card'
import { cn } from '@/shared/lib/cn'

interface AIInsightCardProps {
  title: string
  description: string
  strength: string
  score: number
  children?: React.ReactNode
  className?: string
}

export function AIInsightCard({
  title,
  description,
  strength,
  score,
  children,
  className,
}: AIInsightCardProps) {
  return (
    <Card className={cn('border-slate-700/90 bg-slate-950/80 text-white', className)}>
      <CardHeader className="items-start gap-3 px-5 pt-5 pb-4">
        <div>
          <CardTitle className="text-base text-white">{title}</CardTitle>
          <p className="mt-1 text-sm text-slate-300">{description}</p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 px-3 py-2 text-xs text-slate-200">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-amber-300" />
            <span>{strength}</span>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4 px-5 pb-5 pt-0">
        <div className="text-3xl font-semibold text-white">{score}%</div>
        {children}
      </CardContent>
    </Card>
  )
}
