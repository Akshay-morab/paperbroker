import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api, Profile, Quote } from '../api'

const fmtMoney = (n: number) =>
  '$' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

export default function Dashboard() {
  const nav = useNavigate()
  const [profile, setProfile] = useState<Profile | null>(null)
  const [quotes, setQuotes] = useState<Quote[]>([])
  const [loaded, setLoaded] = useState(false)

  const logout = useCallback(async () => {
    try {
      await api('/api/auth/logout', { method: 'POST' })
    } catch {
      /* session already gone */
    }
    nav('/login')
  }, [nav])

  useEffect(() => {
    let alive = true
    api<Profile>('/api/me')
      .then((p) => {
        if (alive) {
          setProfile(p)
          setLoaded(true)
        }
      })
      .catch(() => nav('/login'))

    const loadQuotes = () =>
      api<Quote[]>('/api/stocks')
        .then((q) => {
          if (alive) setQuotes(q)
        })
        .catch(() => {})

    loadQuotes()
    const id = setInterval(loadQuotes, 5000)
    return () => {
      alive = false
      clearInterval(id)
    }
  }, [nav])

  return (
    <main className="dash">
      <header className="dash-header">
        <div>
          <h1>PaperBroker</h1>
          {profile && <p className="signed-in">Signed in as {profile.email}</p>}
        </div>
        <div className="cash-box">
          {profile && (
            <span className="cash-label">
              Cash: <strong>{fmtMoney(profile.cash)}</strong>
            </span>
          )}
          <button onClick={logout}>Log out</button>
        </div>
      </header>

      <nav className="nav">
        <Link to="/">Watchlist</Link>
        <Link to="/portfolio">Portfolio</Link>
        <Link to="/orders">Orders</Link>
      </nav>

      {!loaded && <p className="muted">Loading…</p>}

      <table className="quotes">
        <thead>
          <tr>
            <th>Symbol</th>
            <th>Name</th>
            <th>Price</th>
            <th>Change</th>
          </tr>
        </thead>
        <tbody>
          {quotes.map((q) => (
            <tr key={q.symbol}>
              <td className="mono">
                <Link to={`/stocks/${q.symbol}`}>{q.symbol}</Link>
              </td>
              <td>{q.name}</td>
              <td className="mono">{fmtMoney(q.price)}</td>
              <td className={q.change_pct >= 0 ? 'up' : 'down'}>
                {q.change_pct >= 0 ? '+' : ''}
                {q.change_pct.toFixed(2)}%
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <p className="muted small">Simulated market — prices tick every 3 seconds.</p>
    </main>
  )
}
