import { useEffect, useMemo, useRef } from 'react'
import { createChart, type IChartApi, type ISeriesApi, type CandlestickData } from 'lightweight-charts'
import { type Candle } from '@/shared/api/api-client-types'

interface TickerChartProps {
  candles: Candle[]
  onSelectTimeframe: (timeframe: string) => void
  selectedTimeframe: string
}

const timeframeOptions = ['1D', '1W', '1M', '3M'] as const

export function TickerChart({ candles, onSelectTimeframe, selectedTimeframe }: TickerChartProps) {
  const chartRef = useRef<HTMLDivElement | null>(null)
  const chartInstance = useRef<IChartApi | null>(null)
  const candleSeries = useRef<ISeriesApi<'Candlestick'> | null>(null)

  const seriesData = useMemo<CandlestickData[]>(() => {
    return candles.map((candle) => ({
      time: Math.floor(candle.timestamp / 1000),
      open: candle.open,
      high: candle.high,
      low: candle.low,
      close: candle.close,
    }))
  }, [candles])

  useEffect(() => {
    if (!chartRef.current) return

    chartInstance.current = createChart(chartRef.current, {
      layout: {
        background: { color: 'transparent' },
        textColor: 'var(--foreground)',
      },
      grid: {
        vertLines: { color: 'rgba(148, 163, 184, 0.08)' },
        horzLines: { color: 'rgba(148, 163, 184, 0.08)' },
      },
      rightPriceScale: {
        borderColor: 'rgba(148, 163, 184, 0.2)',
      },
      timeScale: {
        borderColor: 'rgba(148, 163, 184, 0.2)',
      },
      crosshair: {
        mode: 1,
      },
      localization: {
        dateFormat: 'MMM dd',
      },
    })

    candleSeries.current = chartInstance.current.addCandlestickSeries({
      upColor: 'hsl(142, 76%, 36%)',
      downColor: 'hsl(0, 84%, 60%)',
      borderDownColor: 'hsl(0, 84%, 60%)',
      borderUpColor: 'hsl(142, 76%, 36%)',
      wickDownColor: 'hsl(0, 84%, 60%)',
      wickUpColor: 'hsl(142, 76%, 36%)',
    })

    return () => {
      chartInstance.current?.remove()
      chartInstance.current = null
      candleSeries.current = null
    }
  }, [])

  useEffect(() => {
    if (!candleSeries.current) return
    candleSeries.current.setData(seriesData)
    chartInstance.current?.timeScale().fitContent()
  }, [seriesData])

  return (
    <div className="space-y-4 rounded-3xl border border-border bg-card p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold">Свечный график</h2>
          <p className="text-sm text-muted-foreground">Live инструмент с селектором временных рамок.</p>
        </div>
        <div className="flex gap-2">
          {timeframeOptions.map((option) => (
            <button
              key={option}
              type="button"
              onClick={() => onSelectTimeframe(option)}
              className={`rounded-full px-3 py-1.5 text-sm transition ${
                selectedTimeframe === option
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-muted-foreground hover:bg-muted/80'
              }`}
            >
              {option}
            </button>
          ))}
        </div>
      </div>
      <div className="h-[420px]" ref={chartRef} />
    </div>
  )
}
