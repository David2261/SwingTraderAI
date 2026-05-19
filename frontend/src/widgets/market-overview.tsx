import { ArrowUpRight, ArrowDownRight, TrendingUp } from 'lucide-react'
import { useTopMovers } from '@/features/tickers/hooks/ticker-hooks'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Skeleton } from '@/shared/ui/skeleton'

export function MarketOverview() {
  const { data, isLoading } = useTopMovers()

  return (
    <Card>
      <CardHeader>
        <CardTitle>Обзор рынка</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {isLoading ? (
          <div className="grid gap-3">
            <Skeleton className="h-16" />
            <Skeleton className="h-16" />
            <Skeleton className="h-16" />
          </div>
        ) : (
          <div className="space-y-3">
            {data?.slice(0, 3).map((mover) => (
              <div key={mover.symbol} className="flex items-center justify-between gap-3 rounded-2xl border border-border p-4">
                <div>
                  <p className="text-sm font-medium">{mover.symbol}</p>
                  <p className="text-xs text-muted-foreground">{mover.name}</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold">${mover.price.toFixed(2)}</p>
                  <span className={`text-xs ${mover.change_percent >= 0 ? 'text-positive' : 'text-negative'}`}>
                    {mover.change_percent.toFixed(2)}%
                  </span>
                </div>
                <div className="rounded-full bg-muted/80 p-2 text-muted-foreground">
                  {mover.direction === 'up' ? <ArrowUpRight className="h-4 w-4" /> : <ArrowDownRight className="h-4 w-4" />}
                </div>
              </div>
            ))}
            <div className="flex items-center gap-2 rounded-2xl bg-primary/5 p-3 text-xs text-muted-foreground">
              <TrendingUp className="h-4 w-4 text-primary" />
              Рынки обновляются каждые 10 секунд с живыми тикерами и сигналами.
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
