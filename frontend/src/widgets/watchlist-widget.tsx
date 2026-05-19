import { useMemo } from 'react'
import { Eye, Star } from 'lucide-react'
import { useWatchlist } from '@/features/watchlist/hooks/watchlist-hooks'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Skeleton } from '@/shared/ui/skeleton'

export function WatchlistWidget() {
  const { data, isLoading } = useWatchlist()

  const topFive = useMemo(() => data?.slice(0, 5) ?? [], [data])

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Предварительный просмотр списка отслеживаемых товаров</CardTitle>
          <Star className="h-5 w-5 text-primary" />
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {isLoading ? (
          <div className="space-y-3">
            <Skeleton className="h-12" />
            <Skeleton className="h-12" />
          </div>
        ) : topFive.length === 0 ? (
          <p className="text-sm text-muted-foreground">Ваш список отслеживаемых товаров пуст. Добавьте активы, чтобы начать отслеживание производительности.</p>
        ) : (
          topFive.map((item) => (
            <div key={item.id} className="flex items-center justify-between rounded-2xl border border-border p-4">
              <div>
                <p className="font-medium">{item.ticker.symbol}</p>
                <p className="text-xs text-muted-foreground">{item.ticker.name}</p>
              </div>
              <div className="text-right">
                <p className="font-semibold">${item.ticker.price.toFixed(2)}</p>
                <p className="text-xs text-muted-foreground">{item.ticker.change_percent.toFixed(2)}%</p>
              </div>
              <Eye className="h-4 w-4 text-muted-foreground" />
            </div>
          ))
        )}
      </CardContent>
    </Card>
  )
}
