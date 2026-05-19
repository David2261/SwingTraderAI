import { useParams } from 'react-router-dom'
import { PageHeader } from '@/shared/ui/page-header'

export function TickerPage() {
  const { id } = useParams()

  return (
    <div className="space-y-8">
      <PageHeader
        title={`Ticker: ${id?.toUpperCase()}`}
        description="Подробный анализ и торговая информация"
      />
      <div className="text-center text-muted-foreground">
        Подробная информация о тикерах и графики появятся в ближайшее время....
      </div>
    </div>
  )
}
