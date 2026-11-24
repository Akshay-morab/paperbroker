import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Alert, Anchor, Button, Card, Group, NumberInput, SegmentedControl, Stack, Text, Title } from '@mantine/core'
import Shell from '../components/Shell'
import { api, ApiError, Candle, StockDetailData } from '../api'

const fmtMoney = (n: number) =>
  '$' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

function Sparkline({ candles }: { candles: Candle[] }) {
  const closes = candles.slice(-60).map((c) => c.c)
  if (closes.length < 2) return null
  const min = Math.min(...closes)
  const max = Math.max(...closes)
  const span = max - min || 1
  const points = closes
    .map((c, i) => `${(i / (closes.length - 1)) * 100},${28 - ((c - min) / span) * 26}`)
    .join(' ')
  return (
    <svg viewBox="0 0 100 30" className="spark" preserveAspectRatio="none">
      <polyline points={points} fill="none" stroke="#4c6ef5" strokeWidth="1" />
    </svg>
  )
}

export default function StockDetail() {
  const { symbol = '' } = useParams()
  const [detail, setDetail] = useState<StockDetailData | null>(null)
  const [notFound, setNotFound] = useState(false)
  const [side, setSide] = useState<'buy' | 'sell'>('buy')
  const [qty, setQty] = useState('10')
  const [toast, setToast] = useState('')
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

  async function placeOrder() {
    setBusy(true)
    setToast('')
    setBanner('')
    try {
      await api('/api/orders', {
        method: 'POST',
        body: JSON.stringify({ symbol, side, quantity: Number(qty) }),
      })
      setToast('Order filled') // AC-3.1: the exact string Kane asserts
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
      <Group justify="space-between" align="flex-start" mb="md" wrap="nowrap">
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
        {detail && <Sparkline candles={detail.candles} />}
      </Group>

      <Card shadow="sm" padding="lg" radius="md" withBorder maw={430}>
        <Title order={4} mb="sm">Place a market order</Title>
        <Stack>
          <SegmentedControl
            value={side}
            onChange={(v) => setSide(v as 'buy' | 'sell')}
            data={[
              { value: 'buy', label: 'Buy' },
              { value: 'sell', label: 'Sell' },
            ]}
          />
          <NumberInput
            label="Quantity"
            min={1}
            step={1}
            value={qty}
            onChange={(v) => setQty(String(v ?? ''))}
          />
          <Button
            color={side === 'buy' ? 'indigo' : 'red'}
            onClick={placeOrder}
            loading={busy}
          >
            {side === 'buy' ? 'Place buy order' : 'Place sell order'}
          </Button>
          {toast && (
            <Alert role="status" color="teal">
              {toast}
            </Alert>
          )}
          {banner && (
            <Alert role="alert" color="red">
              {banner}
            </Alert>
          )}
        </Stack>
      </Card>
    </Shell>
  )
}
