import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, PlacedOrder } from '../api'

const fmtMoney = (n: number) =>
  '$' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

export default function Orders() {
  const [rows, setRows] = useState<PlacedOrder[]>([])

  useEffect(() => {
    api<PlacedOrder[]>('/api/orders')
      .then(setRows)
      .catch(() => {})
  }, [])

  return (
    <main className="dash">
      <nav className="nav">
        <Link to="/">Watchlist</Link>
        <Link to="/portfolio">Portfolio</Link>
      </nav>

      <header className="dash-header">
        <div>
          <h1>Order history</h1>
        </div>
      </header>

      {rows.length === 0 && <p className="muted">No orders yet.</p>}

      <table className="quotes">
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Side</th>
            <th>Qty</th>
            <th>Price</th>
            <th>Status</th>
            <th>Reason</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((o) => (
            <tr key={o.id}>
              <td className="mono">
                <Link to={`/stocks/${o.symbol}`}>{o.symbol}</Link>
              </td>
              <td className={o.side === 'buy' ? 'up' : 'down'}>{o.side}</td>
              <td className="mono">{o.quantity}</td>
              <td className="mono">{o.filled_price != null ? fmtMoney(o.filled_price) : '—'}</td>
              <td>{o.status}</td>
              <td className="muted small">{o.reason ?? ''}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  )
}
