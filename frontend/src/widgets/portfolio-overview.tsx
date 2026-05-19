import { AreaChart, DollarSign, TrendingUp } from 'lucide-react'
import { usePortfolioSummary } from '@/features/portfolio/hooks/portfolio-hooks'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Skeleton } from '@/shared/ui/skeleton'

export function PortfolioOverview() {
  const { data, isLoading } = usePortfolioSummary()

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Сводка портфеля</CardTitle>
          <DollarSign className="h-5 w-5 text-muted-foreground" />
        </div>
      </CardHeader>
      <CardContent className="grid gap-4 sm:grid-cols-2">
        {isLoading ? (
          <div className="space-y-3">
            <Skeleton className="h-14" />
            <Skeleton className="h-14" />
          </div>
        ) : (
          <>
            <div className="rounded-2xl border border-border p-4">
              <p className="text-sm text-muted-foreground">Общая стоимость</p>
              <p className="mt-2 text-2xl font-semibold">${data?.total_value.toLocaleString()}</p>
            </div>
            <div className="rounded-2xl border border-border p-4">
              <p className="text-sm text-muted-foreground">Изменение за день</p>
              <p className="mt-2 text-2xl font-semibold">
                {data?.day_change_percent >= 0 ? '+' : ''}
                {data?.day_change_percent.toFixed(2)}%
              </p>
            </div>
            <div className="rounded-2xl border border-border p-4">
              <p className="text-sm text-muted-foreground">Позиции</p>
              <p className="mt-2 text-2xl font-semibold">{data?.positions}</p>
            </div>
            <div className="rounded-2xl border border-border p-4">
              <p className="text-sm text-muted-foreground">Процент побед</p>
              <p className="mt-2 text-2xl font-semibold">{data?.win_rate.toFixed(0)}%</p>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}
