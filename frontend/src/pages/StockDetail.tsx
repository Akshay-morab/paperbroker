import { useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  Alert,
  Badge,
  Button,
  Card,
  Group,
  Modal,
  NumberInput,
  SimpleGrid,
  Stack,
  Text,
  Title,
} from '@mantine/core'
import { IconCircleCheck } from '@tabler/icons-react'
import { createChart, IChartApi, UTCTimestamp } from 'lightweight-charts'
import Shell from '../components/Shell'
import { api, ApiError, Candle, Financial, PlacedOrder, Quote, StockDetailData } from '../api'

const fmtMoney = (n: number) =>
  '$' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const fmtMarketCap = (n: number | null) => {
  if (n == null) return '—'
  if (n >= 1e12) return `$${(n / 1e12).toFixed(2)}T`
  if (n >= 1e9) return `$${(n / 1e9).toFixed(1)}B`
  return fmtMoney(n)
}

const RANGES: { label: string; days: number; step?: number }[] = [
  { label: '1D', days: 0 },
  { label: '1M', days: 22 },
  { label: '2M', days: 44 },
  { label: '4M', days: 88 },
  { label: '6M', days: 131 },
  { label: '1Y', days: 261 },
  { label: '5Y', days: 1826, step: 7 },
]

/** Candlestick chart with the range buttons (1D intraday; daily bars for the rest). */
function RangeChart({ detail, range }: { detail: StockDetailData; range: string }) {
  const holder = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!holder.current) return
    const spec = RANGES.find((r) => r.label === range) ?? RANGES[0]
    const step = spec.step ?? 1
    let data: Candle[] =
      spec.days === 0 ? detail.candles : detail.history.slice(-spec.days)
    if (step > 1) data = data.filter((_, i) => i % step === 0)
    if (data.length === 0) return

    const chart: IChartApi = createChart(holder.current, {
      height: 300,
      layout: { background: { color: 'transparent' }, textColor: '#8b94a7' },
      grid: {
        vertLines: { color: 'rgba(140,140,140,0.08)' },
        horzLines: { color: 'rgba(140,140,140,0.08)' },
      },
      timeScale: { timeVisible: spec.days === 0, secondsVisible: false },
      rightPriceScale: { borderVisible: false },
    })
    const series = chart.addCandlestickSeries({
      upColor: '#2fbf71',
      downColor: '#e5484d',
      wickUpColor: '#2fbf71',
      wickDownColor: '#e5484d',
      borderVisible: false,
    })
    const spacing = spec.days === 0 ? 3 : 86400 * step
    const nowSec = Math.floor(Date.now() / 1000)
    series.setData(
      data.map((c, i) => ({
        time: (nowSec - (data.length - 1 - i) * spacing) as UTCTimestamp,
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
  }, [detail, range])

  return <div ref={holder} style={{ width: '100%' }} />
}

/** 52-week range bar with the current price marker. */
function WeekRangeBar({ low, high, price }: { low: number; high: number; price: number }) {
  const span = high - low || 1
  const pct = Math.min(100, Math.max(0, ((price - low) / span) * 100))
  return (
    <div>
      <div className="rangebar">
        <div className="rangebar-dot" style={{ left: `${pct}%` }} />
      </div>
      <Group justify="space-between" mt={4}>
        <Text size="xs" c="dimmed">{fmtMoney(low)}</Text>
        <Text size="xs" c="dimmed">{fmtMoney(high)}</Text>
      </Group>
    </div>
  )
}

/** 5-year financials: revenue vs net profit bars (hand-rolled SVG — no extra deps). */
function FinancialBars({ rows }: { rows: Financial[] }) {
  if (rows.length === 0) return null
  const max = Math.max(...rows.flatMap((r) => [r.revenue, Math.abs(r.net_profit)])) || 1
  const W = rows.length * 46
  return (
    <div>
      <Group gap="xs" mb="xs">
        <span className="legend-dot" style={{ background: '#4c6ef5' }} />
        <Text size="xs" c="dimmed">Revenue</Text>
        <span className="legend-dot" style={{ background: '#2fbf71' }} />
        <Text size="xs" c="dimmed">Net profit</Text>
      </Group>
      <svg viewBox={`0 0 ${W} 112`} className="finchart">
        {rows.map((r, i) => {
          const x = i * 46 + 8
          const rh = Math.max(2, (r.revenue / max) * 80)
          const ph = Math.max(2, (Math.abs(r.net_profit) / max) * 80)
          const profitColor = r.net_profit >= 0 ? '#2fbf71' : '#e5484d'
          return (
            <g key={r.year}>
              <rect x={x} y={92 - rh} width={14} height={rh} rx={3} fill="#4c6ef5" />
              <rect x={x + 17} y={92 - ph} width={14} height={ph} rx={3} fill={profitColor} />
              <text x={x + 15} y={105} textAnchor="middle" fill="#8b94a7" fontSize="9">
                {`'${String(r.year).slice(2)}`}
              </text>
              <text x={x + 15} y={92 - rh - 4} textAnchor="middle" fill="#aab3c5" fontSize="8">
                {`$${(r.revenue / 1e9).toFixed(1)}B`}
              </text>
            </g>
          )
        })}
      </svg>
    </div>
  )
}

export default function StockDetail() {
  const { symbol = '' } = useParams()
  const [detail, setDetail] = useState<StockDetailData | null>(null)
  const [notFound, setNotFound] = useState(false)
  const [range, setRange] = useState('1D')
  const [buyQty, setBuyQty] = useState('10')
  const [sellQty, setSellQty] = useState('10')
  const [toast, setToast] = useState('') // "Order filled" — Kane asserts this text
  const [banner, setBanner] = useState('')
  const [purchase, setPurchase] = useState('') // the popup text
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

  // "Order filled" confirmation stays visible 4s (assertable), the popup ~2s.
  useEffect(() => {
    if (!toast) return
    const id = setTimeout(() => setToast(''), 4000)
    return () => clearTimeout(id)
  }, [toast])

  useEffect(() => {
    if (!purchase) return
    const id = setTimeout(() => setPurchase(''), 2000)
    return () => clearTimeout(id)
  }, [purchase])

  async function placeOrder(side: 'buy' | 'sell', qtyStr: string) {
    setBusy(true)
    setToast('')
    setBanner('')
    try {
      const order = await api<PlacedOrder>('/api/orders', {
        method: 'POST',
        body: JSON.stringify({ symbol, side, quantity: Number(qtyStr) }),
      })
      setToast('Order filled')
      setPurchase(
        `${side === 'buy' ? 'You bought' : 'You sold'} ${order.quantity} ${order.symbol} shares for ${fmtMoney(
          order.filled_price ?? 0
        )}`
      )
      if (side === 'buy') setBuyQty('10')
      else setSellQty('10')
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

  const price = detail?.price ?? 0
  const buyTotal = (Number(buyQty) || 0) * price
  const sellProceeds = (Number(sellQty) || 0) * price
  const profile = detail?.profile ?? null

  return (
    <Shell>
      <Stack gap="md">
        {/* Header */}
        <Stack gap={0}>
          <Title order={2}>
            <span className="mono">{detail?.symbol ?? symbol}</span> — {detail?.name ?? '…'}
          </Title>
          {detail && (
            <Text fz="xl" fw={700} className="mono" c={detail.change_pct >= 0 ? 'teal' : 'red'}>
              {fmtMoney(detail.price)} ({detail.change_pct >= 0 ? '+' : ''}
              {detail.change_pct.toFixed(2)}%)
            </Text>
          )}
        </Stack>

        {/* Price chart with range buttons */}
        <Card radius="md" withBorder padding="sm">
          <Group gap="xs" mb="xs">
            {RANGES.map((r) => (
              <Button
                key={r.label}
                size="xs"
                variant={range === r.label ? 'filled' : 'subtle'}
                onClick={() => setRange(r.label)}
              >
                {r.label}
              </Button>
            ))}
          </Group>
          {detail ? (
            <RangeChart detail={detail} range={range} />
          ) : (
            <div style={{ height: 300 }} />
          )}
        </Card>

        {/* Fundamentals */}
        {profile && (
          <>
            <SimpleGrid cols={{ base: 2, xs: 4 }} spacing="md">
              <Card radius="md" withBorder padding="md">
                <Text c="dimmed" size="xs" tt="uppercase">P/E ratio</Text>
                <Text fz="xl" fw={700} className="mono">{detail?.pe ?? '—'}</Text>
              </Card>
              <Card radius="md" withBorder padding="md">
                <Text c="dimmed" size="xs" tt="uppercase">Market cap</Text>
                <Text fz="xl" fw={700} className="mono">{fmtMarketCap(detail?.market_cap ?? null)}</Text>
              </Card>
              <Card radius="md" withBorder padding="md">
                <Text c="dimmed" size="xs" tt="uppercase">EPS</Text>
                <Text fz="xl" fw={700} className="mono">${profile.eps.toFixed(2)}</Text>
              </Card>
              <Card radius="md" withBorder padding="md">
                <Text c="dimmed" size="xs" tt="uppercase" mb="xs">52-week range</Text>
                <WeekRangeBar
                  low={profile.fifty_two_week_low}
                  high={profile.fifty_two_week_high}
                  price={price}
                />
              </Card>
            </SimpleGrid>

            <Card radius="md" withBorder padding="md">
              <Group gap="sm" mb="xs">
                <Badge variant="light" color="indigo">{profile.sector}</Badge>
                {profile.founded_year && (
                  <Text c="dimmed" size="xs">Founded {profile.founded_year}</Text>
                )}
              </Group>
              <Text size="sm">{profile.description}</Text>
            </Card>

            {/* 5-year financials */}
            <Card radius="md" withBorder padding="md">
              <Title order={5} mb="xs">Financials — 5 years</Title>
              <FinancialBars rows={detail?.financials ?? []} />
            </Card>
          </>
        )}

        {/* Similar stocks (same sector) */}
        {detail && detail.similar.length > 0 && (
          <div>
            <Title order={4} mb="xs">Similar stocks</Title>
            <SimpleGrid cols={{ base: 2, xs: 4 }} spacing="sm">
              {detail.similar.map((s: Quote) => (
                <Card
                  key={s.symbol}
                  component={Link}
                  to={`/stocks/${s.symbol}`}
                  radius="md"
                  withBorder
                  padding="sm"
                  className="stock-card"
                >
                  <Group justify="space-between" mb={2}>
                    <Text fw={700} className="mono">{s.symbol}</Text>
                    <Text size="xs" c={s.change_pct >= 0 ? 'teal' : 'red'}>
                      {s.change_pct >= 0 ? '+' : ''}{s.change_pct.toFixed(2)}%
                    </Text>
                  </Group>
                  <Text className="mono" size="sm">{fmtMoney(s.price)}</Text>
                </Card>
              ))}
            </SimpleGrid>
          </div>
        )}

        {/* Trade — two fully separated cards */}
        <div>
          <Title order={4} mb="xs">Trade</Title>
          <SimpleGrid cols={{ base: 1, xs: 2 }} spacing="md">
            <Card radius="md" withBorder padding="lg" className="trade-card trade-buy">
              <Group justify="space-between" mb="xs">
                <Title order={4} c="teal">Buy</Title>
                <Badge color="teal" variant="light">{detail?.symbol ?? symbol}</Badge>
              </Group>
              <Stack gap="xs">
                <NumberInput
                  label="Quantity"
                  min={1}
                  step={1}
                  value={buyQty}
                  onChange={(v) => setBuyQty(String(v ?? ''))}
                />
                <Group justify="space-between">
                  <Text c="dimmed" size="sm">Price</Text>
                  <Text size="sm" className="mono">{fmtMoney(price)}</Text>
                </Group>
                <Group justify="space-between">
                  <Text c="dimmed" size="sm">Total</Text>
                  <Text fw={700} className="mono">{fmtMoney(buyTotal)}</Text>
                </Group>
                <Button color="teal" onClick={() => placeOrder('buy', buyQty)} loading={busy}>
                  Buy
                </Button>
              </Stack>
            </Card>

            <Card radius="md" withBorder padding="lg" className="trade-card trade-sell">
              <Group justify="space-between" mb="xs">
                <Title order={4} c="red">Sell</Title>
                <Badge color="red" variant="light">{detail?.symbol ?? symbol}</Badge>
              </Group>
              <Stack gap="xs">
                <NumberInput
                  label="Quantity"
                  min={1}
                  step={1}
                  value={sellQty}
                  onChange={(v) => setSellQty(String(v ?? ''))}
                />
                <Group justify="space-between">
                  <Text c="dimmed" size="sm">Price</Text>
                  <Text size="sm" className="mono">{fmtMoney(price)}</Text>
                </Group>
                <Group justify="space-between">
                  <Text c="dimmed" size="sm">Proceeds</Text>
                  <Text fw={700} className="mono">{fmtMoney(sellProceeds)}</Text>
                </Group>
                <Button color="red" onClick={() => placeOrder('sell', sellQty)} loading={busy}>
                  Sell
                </Button>
              </Stack>
            </Card>
          </SimpleGrid>
        </div>

        {/* Confirmations: assertable alert (4s) + popup (2s) */}
        {toast && (
          <Alert role="status" color="teal" maw={520}>
            {toast}
          </Alert>
        )}
        {banner && (
          <Alert role="alert" color="red" maw={520}>
            {banner}
          </Alert>
        )}
      </Stack>

      <Modal
        opened={!!purchase}
        onClose={() => setPurchase('')}
        centered
        withCloseButton={false}
        radius="lg"
        overlayProps={{ blur: 2 }}
        trapFocus={false}
      >
        <Stack align="center" py="xl">
          <IconCircleCheck size={52} color="#2fbf71" stroke={1.5} />
          <Text fz="lg" fw={600} ta="center">{purchase}</Text>
        </Stack>
      </Modal>
    </Shell>
  )
}
