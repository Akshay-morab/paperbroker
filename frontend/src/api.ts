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
      if (body && typeof body.detail === 'string') detail = body.detail
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
