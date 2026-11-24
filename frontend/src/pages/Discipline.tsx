import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, GuardrailStatus } from '../api'

const fmtMoney = (n: number) => {
  const sign = n < 0 ? '−' : ''
  return sign + '$' + Math.abs(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

export default function Discipline() {
  const [status, setStatus] = useState<GuardrailStatus | null>(null)
  const [countdown, setCountdown] = useState('')

  useEffect(() => {
    let alive = true
    const load = () =>
      api<GuardrailStatus>('/api/guardrails/status')
        .then((s) => {
          if (alive) setStatus(s)
        })
        .catch(() => {})
    load()
    const id = setInterval(load, 5000)
    return () => {
      alive = false
      clearInterval(id)
    }
  }, [])

  // Ticking cooldown countdown (cosmetic; the banner text is server-computed).
  useEffect(() => {
    const tick = () => {
      if (!status?.cooldown.active || !status.cooldown.until) {
        setCountdown('')
        return
      }
      const left = Math.max(
        0,
        Math.floor((new Date(status.cooldown.until).getTime() - Date.now()) / 1000)
      )
      const mm = Math.floor(left / 60)
      const ss = left % 60
      setCountdown(`${mm}:${String(ss).padStart(2, '0')}`)
    }
    tick()
    const id = setInterval(tick, 1000)
    return () => clearInterval(id)
  }, [status])

  return (
    <main className="dash">
      <nav className="nav">
        <Link to="/">Watchlist</Link>
        <Link to="/portfolio">Portfolio</Link>
        <Link to="/orders">Orders</Link>
      </nav>

      <header className="dash-header">
        <div>
          <h1>Discipline</h1>
          <p className="muted small">Every rule, enforced before the fill.</p>
        </div>
      </header>

      {status?.locked && status.lock_reason && (
        <p className="banner error" role="alert">
          {status.lock_reason}
        </p>
      )}

      {status && (
        <div className="cards">
          <div className="card">
            <h2>Daily loss limit</h2>
            <p className="big-price">{fmtMoney(status.daily_loss.used)}</p>
            <p className="muted small">
              of {fmtMoney(status.daily_loss.limit)} — {fmtMoney(status.daily_loss.remaining)} remaining
            </p>
          </div>

          <div className="card">
            <h2>Trades today</h2>
            <p className="big-price">
              {status.trade_cap.used}
              <span className="muted">/{status.trade_cap.limit}</span>
            </p>
            <p className="muted small">blocked attempts never count</p>
          </div>

          <div className="card">
            <h2>Tilt cooldown</h2>
            {status.cooldown.active ? (
              <>
                <p className="big-price down">{countdown}</p>
                <p className="muted small">after 3 consecutive losses</p>
              </>
            ) : (
              <p className="muted small">no cooldown active</p>
            )}
          </div>

          <div className="card">
            <h2>Position size cap</h2>
            <p className="big-price">{status.position_size_pct}%</p>
            <p className="muted small">of equity per position</p>
          </div>

          <div className="card">
            <h2>Open positions</h2>
            <p className="big-price">
              {status.state.open_positions}
              <span className="muted">/{status.open_positions_limit}</span>
            </p>
            <p className="muted small">new symbols blocked at the limit</p>
          </div>
        </div>
      )}
    </main>
  )
}
