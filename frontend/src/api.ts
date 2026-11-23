/** Thin fetch wrapper: same-origin cookies, backend detail strings surfaced verbatim. */

export class ApiError extends Error {
  status: number
  detail: string

  constructor(status: number, detail: string) {
    super(detail)
    this.status = status
    this.detail = detail
  }
}

export async function api<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const res = await fetch(path, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...(opts.headers ?? {}) },
    ...opts,
  })
  if (!res.ok) {
    let detail = 'request failed'
    try {
      const body = await res.json()
      if (typeof body?.reason === 'string') detail = body.reason // order rejects/blocks (DESIGN §5)
      else if (typeof body?.detail === 'string') detail = body.detail
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(res.status, detail)
  }
  return res.json() as Promise<T>
}

export type Profile = {
  id: number
  email: string
  role: string
  cash: number
  rules: {
    daily_loss_limit: number
    max_trades_per_day: number
    cooldown_minutes: number
    loss_streak_trigger: number
    max_position_pct: number
    max_open_positions: number
  }
}

export type Quote = {
  symbol: string
  name: string
  price: number
  session_open: number
  change_pct: number
}

export type Candle = { t: number; o: number; h: number; l: number; c: number }

export type StockDetailData = Quote & { candles: Candle[] }

export type PlacedOrder = {
  id: number
  symbol: string
  side: string
  quantity: number
  order_type: string
  status: string
  reason: string | null
  filled_price: number | null
  realized_pnl: number | null
  created_at: string
}

export type Position = {
  symbol: string
  quantity: number
  avg_cost: number
  price: number
  market_value: number
  unrealized_pnl: number
}

export type PortfolioData = { cash: number; equity: number; positions: Position[] }
