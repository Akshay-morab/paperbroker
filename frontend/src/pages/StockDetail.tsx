import { FormEvent, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api, ApiError, Candle, Quote, StockDetailData } from '../api'

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
      <polyline points={points} fill="none" stroke="#4c7ef3" strokeWidth="1" />
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

  async function submit(e: FormEvent) {
    e.preventDefault()
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
    }
  }

  if (notFound) {
    return (
      <main className="dash">
        <nav className="nav">
          <Link to="/">← Watchlist</Link>
        </nav>
        <p className="banner error">unknown symbol</p>
      </main>
    )
  }

  return (
    <main className="dash">
      <nav className="nav">
        <Link to="/">← Watchlist</Link>
        <Link to="/portfolio">Portfolio</Link>
        <Link to="/orders">Orders</Link>
      </nav>

      {detail && (
        <>
          <header className="dash-header">
            <div>
              <h1>
                <span className="mono">{detail.symbol}</span> — {detail.name}
              </h1>
              <p className={`big-price ${detail.change_pct >= 0 ? 'up' : 'down'}`}>
                {fmtMoney(detail.price)} ({detail.change_pct >= 0 ? '+' : ''}
                {detail.change_pct.toFixed(2)}%)
              </p>
              <p className="muted small">
                Session open {fmtMoney(detail.session_open)} · simulated market
              </p>
            </div>
            <Sparkline candles={detail.candles} />
          </header>

          <form className="ticket" onSubmit={submit}>
            <h2>Place a market order</h2>
            <div className="side-toggle">
              <button
                type="button"
                className={side === 'buy' ? 'side active-buy' : 'side'}
                onClick={() => setSide('buy')}
              >
                Buy
              </button>
              <button
                type="button"
                className={side === 'sell' ? 'side active-sell' : 'side'}
                onClick={() => setSide('sell')}
              >
                Sell
              </button>
            </div>
            <label htmlFor="qty">Quantity</label>
            <input
              id="qty"
              type="number"
              min={1}
              step={1}
              value={qty}
              onChange={(e) => setQty(e.target.value)}
            />
            <button type="submit" className={side === 'buy' ? 'place-buy' : 'place-sell'}>
              {side === 'buy' ? 'Place buy order' : 'Place sell order'}
            </button>
            {toast && (
              <p className="banner ok" role="status">
                {toast}
              </p>
            )}
            {banner && (
              <p className="banner error" role="alert">
                {banner}
              </p>
            )}
          </form>
        </>
      )}
    </main>
  )
}
