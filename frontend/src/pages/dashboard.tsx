import { TrendingUp, TrendingDown, DollarSign, BarChart3 } from 'lucide-react'
import { PageHeader } from '@/shared/ui/page-header'
import { StatCard } from '@/shared/ui/stat-card'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'

// Mock data - replace with real data from API
const mockStats = {
  totalValue: 125000,
  totalChange: 5.2,
  dayChange: 2.1,
  positions: 12,
}

const mockRecentTrades = [
  { symbol: 'AAPL', action: 'BUY', quantity: 100, price: 150.25, time: '10:30 AM' },
  { symbol: 'GOOGL', action: 'SELL', quantity: 50, price: 2800.50, time: '11:15 AM' },
  { symbol: 'TSLA', action: 'BUY', quantity: 25, price: 220.75, time: '2:45 PM' },
]

export function DashboardPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="Dashboard"
        description="Overview of your trading portfolio and recent activity"
      />

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Portfolio Value"
          value={`$${mockStats.totalValue.toLocaleString()}`}
          change={{ value: mockStats.totalChange, label: 'from yesterday' }}
          icon={<DollarSign className="h-4 w-4" />}
        />
        <StatCard
          title="Day Change"
          value={`${mockStats.dayChange > 0 ? '+' : ''}${mockStats.dayChange}%`}
          change={{ value: mockStats.dayChange, label: 'today' }}
          icon={
            mockStats.dayChange >= 0 ? (
              <TrendingUp className="h-4 w-4" />
            ) : (
              <TrendingDown className="h-4 w-4" />
            )
          }
        />
        <StatCard
          title="Active Positions"
          value={mockStats.positions}
          icon={<BarChart3 className="h-4 w-4" />}
        />
        <StatCard
          title="Win Rate"
          value="68%"
          change={{ value: 5.2, label: 'this month' }}
          icon={<TrendingUp className="h-4 w-4" />}
        />
      </div>

      {/* Recent Activity */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent Trades</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {mockRecentTrades.map((trade, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`w-2 h-2 rounded-full ${
                      trade.action === 'BUY' ? 'bg-positive' : 'bg-negative'
                    }`} />
                    <div>
                      <p className="font-medium">{trade.symbol}</p>
                      <p className="text-sm text-muted-foreground">{trade.time}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">
                      {trade.action} {trade.quantity}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      @ ${trade.price}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Market Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">S&P 500</span>
                <span className="text-sm text-positive">+0.8%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">NASDAQ</span>
                <span className="text-sm text-positive">+1.2%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">DOW</span>
                <span className="text-sm text-negative">-0.3%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">VIX</span>
                <span className="text-sm text-positive">-2.1%</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
