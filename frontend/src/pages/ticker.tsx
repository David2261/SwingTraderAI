import { useParams } from 'react-router-dom'
import { PageHeader } from '@/shared/ui/page-header'

export function TickerPage() {
  const { id } = useParams()

  return (
    <div className="space-y-8">
      <PageHeader
        title={`Ticker: ${id?.toUpperCase()}`}
        description="Detailed analysis and trading information"
      />
      <div className="text-center text-muted-foreground">
        Ticker details and charts coming soon...
      </div>
    </div>
  )
}
