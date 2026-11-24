import { useEffect, useRef, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Alert, Button, Card, Group, NumberInput, Stack, Text, Title } from '@mantine/core'
import { createChart, IChartApi, UTCTimestamp } from 'lightweight-charts'
import Shell from '../components/Shell'
import { api, ApiError, Candle, PlacedOrder, StockDetailData } from '../api'

const fmtMoney = (n: number) =>
  '$' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

/** Real candlestick chart (TradingView's lightweight-charts). */
function CandleChart({ candles }: { candles: Candle[] }) {
  const holder = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!holder.current || candles.length === 0) return
    const chart: IChartApi = createChart(holder.current, {
      height: 300,
      layout: { background: { color: 'transparent' }, textColor: '#8b94a7' },
      grid: {
        vertLines: { color: 'rgba(140,140,140,0.08)' },
        horzLines: { color: 'rgba(140,140,140,0.08)' },
      },
      timeScale: { timeVisible: true, secondsVisible: false },
      rightPriceScale: { borderVisible: false },
    })
    const series = chart.addCandlestickSeries({
      upColor: '#2fbf71',
      downColor: '#e5484d',
      wickUpColor: '#2fbf71',
      wickDownColor: '#e5484d',
      borderVisible: false,
    })
    // Map the deterministic back-candles onto a plausible "minutes ago" axis.
    const nowSec = Math.floor(Date.now() / 1000)
    series.setData(
      candles.map((c, i) => ({
        time: (nowSec - (candles.length - 1 - i) * 3) as UTCTimestamp,
        open: c.o,
        high: c.h,
        low: c.l,
        close: c.c,
      }))
    )
    chart.timeScale().fitContent()

    const ro = new ResizeObserver(() => {
      if (holder.current) chart.applyOptions({ width: holder.current.clientWidth })
    })
    ro.observe(holder.current)

    return () => {
      ro.disconnect()
      chart.remove()
    }
  }, [candles])

  return <div ref={holder} style={{ width: '100%' }} />
}

export default function StockDetail() {
  const { symbol = '' } = useParams()
  const [detail, setDetail] = useState<StockDetailData | null>(null)
  const [notFound, setNotFound] = useState(false)
  const [qty, setQty] = useState('10')
  const [toast, setToast] = useState('') // "Order filled" — Kane asserts this text
  const [fillDetail, setFillDetail] = useState('')
  const [banner, setBanner] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    let alive = true
    setNotFound(false)
    setDetail(null)
    const load = () =>
      api<StockDetailData>(`/api/stocks/${symbol}`)
        .then((d) => {
          if (alive) setDetail(d)
        })
        .catch((e) => {
          if (alive && e instanceof ApiError && e.status === 404) setNotFound(true)
        })
    load()
    const id = setInterval(load, 5000)
    return () => {
      alive = false
      clearInterval(id)
    }
  }, [symbol])

  // The success toast auto-dismisses after 4 seconds (user feedback, Nov 24).
  // Kane asserts immediately after clicking, well inside the window.
  useEffect(() => {
    if (!toast) return
    const id = setTimeout(() => {
      setToast('')
      setFillDetail('')
    }, 4000)
    return () => clearTimeout(id)
  }, [toast])

  async function placeOrder(side: 'buy' | 'sell') {
    setBusy(true)
    setToast('')
    setFillDetail('')
    setBanner('')
    try {
      const order = await api<PlacedOrder>('/api/orders', {
        method: 'POST',
        body: JSON.stringify({ symbol, side, quantity: Number(qty) }),
      })
      setToast('Order filled')
      setFillDetail(
        `${side === 'buy' ? 'Bought' : 'Sold'} ${order.quantity} ${order.symbol} @ ${fmtMoney(
          order.filled_price ?? 0
        )}`
      )
      setQty('10')
    } catch (err) {
      // Rejected/blocked reasons render verbatim (DESIGN.md §3.4).
      if (err instanceof ApiError) setBanner(err.detail)
    } finally {
      setBusy(false)
    }
  }

  if (notFound) {
    return (
      <Shell>
        <Alert role="alert" color="red" maw={430}>
          unknown symbol
        </Alert>
      </Shell>
    )
  }

  return (
    <Shell>
      <Stack gap="md" mb="md">
        <Group justify="space-between" align="flex-end" wrap="nowrap">
          <Stack gap={0}>
            <Title order={2}>
              <span className="mono">{detail?.symbol ?? symbol}</span> — {detail?.name ?? '…'}
            </Title>
            {detail && (
              <>
                <Text fz="xl" fw={700} className="mono" c={detail.change_pct >= 0 ? 'teal' : 'red'}>
                  {fmtMoney(detail.price)} ({detail.change_pct >= 0 ? '+' : ''}
                  {detail.change_pct.toFixed(2)}%)
                </Text>
                <Text c="dimmed" size="xs">
                  Session open {fmtMoney(detail.session_open)} · simulated market
                </Text>
              </>
            )}
          </Stack>
        </Group>

        <Card radius="md" withBorder padding="sm">
          {detail ? <CandleChart candles={detail.candles} /> : <div style={{ height: 300 }} />}
        </Card>
      </Stack>

      <Card shadow="sm" padding="lg" radius="md" withBorder maw={520}>
        <Title order={4} mb="sm">Place a market order</Title>
        <Group grow align="flex-end" gap="sm" wrap="nowrap">
          <NumberInput
            label="Quantity"
            min={1}
            step={1}
            value={qty}
            onChange={(v) => setQty(String(v ?? ''))}
          />
          <Button size="md" color="teal" onClick={() => placeOrder('buy')} loading={busy}>
            Buy
          </Button>
          <Button size="md" color="red" onClick={() => placeOrder('sell')} loading={busy}>
            Sell
          </Button>
        </Group>

        {toast && (
          <Alert role="status" color="teal" mt="sm">
            {toast}
          </Alert>
        )}
        {fillDetail && (
          <Text c="teal" size="sm" mt="xs">
            {fillDetail}
          </Text>
        )}
        {banner && (
          <Alert role="alert" color="red" mt="sm">
            {banner}
          </Alert>
        )}
      </Card>
    </Shell>
  )
}
