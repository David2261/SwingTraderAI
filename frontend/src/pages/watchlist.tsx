import { useMemo, useState } from 'react'
import { Search, TrendingUp, TrendingDown } from 'lucide-react'
import { PageHeader } from '@/shared/ui/page-header'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/shared/ui/table'
import { Input } from '@/shared/ui/input'
import { Button } from '@/shared/ui/button'
import { SignalBadge } from '@/shared/ui/signal-badge'
import { useWatchlist } from '@/features/watchlist/hooks/watchlist-hooks'

const assetTypes = ['All', 'Crypto', 'Stocks', 'Russian'] as const

export function WatchlistPage() {
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState<(typeof assetTypes)[number]>('All')
  const watchlistQuery = useWatchlist()
  const items = watchlistQuery.data ?? []

  const filtered = useMemo(() => {
    return items
      .filter((item) => item.ticker.symbol.toLowerCase().includes(search.toLowerCase()) || item.ticker.name.toLowerCase().includes(search.toLowerCase()))
      .filter((item) => {
        if (filter === 'All') return true
        if (filter === 'Crypto') return ['BTC', 'ETH'].includes(item.ticker.symbol)
        if (filter === 'Stocks') return ['AAPL', 'TSLA'].includes(item.ticker.symbol)
        return ['SBER', 'GAZP', 'IMOEX'].includes(item.ticker.symbol)
      })
  }, [filter, items, search])

  return (
    <div className="space-y-8">
      <PageHeader
        title="Watchlist"
        description="Track live signals, price direction, and AI notes for your top assets."
      />

      <div className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="flex flex-col gap-4 rounded-3xl border border-slate-800/80 bg-slate-950/70 p-5 shadow-lg shadow-slate-950/20">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-3 rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3">
              <Search className="h-4 w-4 text-slate-400" />
              <Input
                placeholder="Search your watchlist"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                className="border-0 bg-transparent px-0 text-slate-100 placeholder:text-slate-500 focus-visible:outline-none"
              />
            </div>
            <div className="flex flex-wrap gap-2">
              {assetTypes.map((type) => (
                <Button
                  key={type}
                  variant={filter === type ? 'secondary' : 'ghost'}
                  size="sm"
                  onClick={() => setFilter(type)}
                >
                  {type}
                </Button>
              ))}
            </div>
          </div>

          <Table className="min-w-full border-separate border-spacing-y-3">
            <TableHeader>
              <TableRow>
                <TableHead>Ticker</TableHead>
                <TableHead>Price</TableHead>
                <TableHead>Signal</TableHead>
                <TableHead>Target / Stop</TableHead>
                <TableHead>AI Notes</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered.map((item) => (
                <TableRow key={item.id} className="group transition hover:-translate-y-0.5 hover:bg-slate-900/70">
                  <TableCell>
                    <div className="flex flex-col gap-1">
                      <span className="text-sm font-semibold text-white">{item.ticker.symbol}</span>
                      <span className="text-xs text-slate-500">{item.ticker.name}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm text-white">${item.ticker.price.toFixed(2)}</div>
                    <div className={`text-xs ${item.ticker.change_percent >= 0 ? 'text-emerald-300' : 'text-rose-300'}`}>
                      {item.ticker.change_percent >= 0 ? '+' : ''}{item.ticker.change_percent.toFixed(2)}%
                    </div>
                  </TableCell>
                  <TableCell>
                    <SignalBadge signal={item.ticker.symbol === 'TSLA' ? 'SELL' : item.ticker.symbol === 'AAPL' ? 'BUY' : 'NEUTRAL'} />
                  </TableCell>
                  <TableCell>
                    <div className="text-sm text-slate-200">{item.ticker.symbol === 'BTC' ? '70k / 64k' : item.ticker.symbol === 'ETH' ? '4.4k / 3.8k' : '—'}</div>
                  </TableCell>
                  <TableCell>
                    <p className="max-w-xs text-sm text-slate-400">{item.ticker.symbol === 'AAPL' ? 'Healthy momentum but watch overhead resistance.' : 'Strong support near moving average.'}</p>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        <div className="space-y-4 rounded-3xl border border-slate-800/80 bg-slate-950/70 p-5 shadow-lg shadow-slate-950/20">
          <div className="rounded-3xl border border-slate-800/90 bg-slate-900/80 p-5">
            <p className="text-sm uppercase tracking-[0.24em] text-slate-500">Signal summary</p>
            <div className="mt-4 grid gap-4">
              <div className="flex items-center justify-between rounded-2xl border border-slate-800/90 bg-slate-950 p-4">
                <div>
                  <p className="text-sm text-slate-400">Top mover</p>
                  <p className="mt-1 font-semibold text-white">BTC momentum heat</p>
                </div>
                <TrendingUp className="h-5 w-5 text-emerald-300" />
              </div>
              <div className="flex items-center justify-between rounded-2xl border border-slate-800/90 bg-slate-950 p-4">
                <div>
                  <p className="text-sm text-slate-400">Signal intensity</p>
                  <p className="mt-1 font-semibold text-white">High</p>
                </div>
                <TrendingDown className="h-5 w-5 text-rose-300" />
              </div>
            </div>
          </div>
          <div className="rounded-3xl border border-slate-800/90 bg-slate-900/80 p-5">
            <p className="text-sm text-slate-400">Recent activity</p>
            <div className="mt-4 space-y-3">
              {filtered.slice(0, 3).map((item) => (
                <div key={item.id} className="rounded-2xl border border-slate-800/90 bg-slate-950 px-4 py-3">
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-sm text-slate-200">{item.ticker.symbol}</span>
                    <SignalBadge signal={item.ticker.symbol === 'TSLA' ? 'SELL' : 'BUY'} />
                  </div>
                  <p className="mt-2 text-sm text-slate-400">Estimated AI bias for the next 12h.</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
