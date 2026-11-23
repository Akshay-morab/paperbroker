import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, PortfolioData } from '../api'

const fmtMoney = (n: number) =>
  '$' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

export default function Portfolio() {
  const [data, setData] = useState<PortfolioData | null>(null)

  useEffect(() => {
    let alive = true
    const load = () =>
      api<PortfolioData>('/api/portfolio')
        .then((p) => {
          if (alive) setData(p)
        })
        .catch(() => {})
    load()
    const id = setInterval(load, 5000)
    return () => {
      alive = false
      clearInterval(id)
    }
  }, [])

  return (
    <main className="dash">
      <nav className="nav">
        <Link to="/">Watchlist</Link>
        <Link to="/orders">Orders</Link>
      </nav>

      <header className="dash-header">
        <div>
          <h1>Portfolio</h1>
        </div>
        <div className="cash-box">
          {data && (
            <>
              <span className="cash-label">
                Cash: <strong>{fmtMoney(data.cash)}</strong>
              </span>
              <span className="cash-label">
                Equity: <strong>{fmtMoney(data.equity)}</strong>
              </span>
            </>
          )}
        </div>
      </header>

      {data && data.positions.length === 0 && <p className="muted">No positions yet.</p>}

      <table className="quotes">
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Qty</th>
            <th>Avg cost</th>
            <th>Price</th>
            <th>Market value</th>
            <th>Unrealized P&L</th>
          </tr>
        </thead>
        <tbody>
          {data?.positions.map((p) => (
            <tr key={p.symbol}>
              <td className="mono">
                <Link to={`/stocks/${p.symbol}`}>{p.symbol}</Link>
              </td>
              <td className="mono">{p.quantity}</td>
              <td className="mono">{fmtMoney(p.avg_cost)}</td>
              <td className="mono">{fmtMoney(p.price)}</td>
              <td className="mono">{fmtMoney(p.market_value)}</td>
              <td className={`mono ${p.unrealized_pnl >= 0 ? 'up' : 'down'}`}>
                {p.unrealized_pnl >= 0 ? '+' : ''}
                {fmtMoney(p.unrealized_pnl)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  )
}
