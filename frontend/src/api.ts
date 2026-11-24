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

export type StockProfile = {
  symbol: string
  description: string
  sector: string
  eps: number
  shares_outstanding: number
  fifty_two_week_high: number
  fifty_two_week_low: number
  founded_year: number | null
}

export type Financial = { year: number; revenue: number; net_profit: number }

export type StockDetailData = Quote & {
  candles: Candle[]
  history: Candle[]
  profile: StockProfile | null
  pe: number | null
  market_cap: number | null
  financials: Financial[]
  similar: Quote[]
}

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

export type GuardrailStatus = {
  locked: boolean
  lock_reason: string | null
  state: { realized_today: number; trades_used: number; open_positions: number; equity: number }
  daily_loss: { used: number; limit: number; remaining: number }
  trade_cap: { used: number; limit: number }
  cooldown: { active: boolean; until: string | null }
  position_size_pct: number
  open_positions_limit: number
}
