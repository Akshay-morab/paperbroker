/** Deterministic letter avatar per symbol — the effort-light "logo tile":
 * no assets, no trademarks, a stable gradient per ticker. */

const PALETTES: [string, string][] = [
  ['#4c6ef5', '#7048e8'],
  ['#2fbf71', '#1d7a4a'],
  ['#e5484d', '#a63a3f'],
  ['#f59f00', '#d9480f'],
  ['#15aabf', '#0b7285'],
  ['#e64980', '#be4bdb'],
]

function hashCode(s: string): number {
  let h = 0
  for (let i = 0; i < s.length; i++) h = (h * 31 + s.charCodeAt(i)) % 9973
  return h
}

export default function SymbolAvatar({ symbol, size = 34 }: { symbol: string; size?: number }) {
  const [a, b] = PALETTES[hashCode(symbol) % PALETTES.length]
  return (
    <div
      className="sym-avatar"
      style={{
        width: size,
        height: size,
        fontSize: Math.round(size * 0.45),
        background: `linear-gradient(135deg, ${a}, ${b})`,
      }}
      title={symbol}
    >
      {symbol[0]}
    </div>
  )
}
