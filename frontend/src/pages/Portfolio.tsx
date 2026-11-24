import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Badge, Card, Group, SimpleGrid, Text } from '@mantine/core'
import Shell from '../components/Shell'
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
    <Shell>
      {/* Net worth hero */}
      <Card radius="md" withBorder p="xl" mb="lg" className="hero">
        <Text c="dimmed" size="sm" tt="uppercase">Net worth</Text>
        <Text fz={44} fw={800} className="mono" lh={1.2}>
          {data ? fmtMoney(data.equity) : '—'}
        </Text>
        <Group gap="xl" mt="xs">
          <div>
            <Text c="dimmed" size="xs">Cash</Text>
            <Text fz="lg" fw={600} className="mono">{fmtMoney(data?.cash ?? 0)}</Text>
          </div>
          <div>
            <Text c="dimmed" size="xs">Invested</Text>
            <Text fz="lg" fw={600} className="mono">
              {fmtMoney((data?.equity ?? 0) - (data?.cash ?? 0))}
            </Text>
          </div>
        </Group>
      </Card>

      <Text fz="lg" fw={600} mb="xs">Positions</Text>

      {data && data.positions.length === 0 && (
        <Text c="dimmed" mb="md">
          No positions yet.
        </Text>
      )}

      <SimpleGrid cols={{ base: 1, xs: 2, md: 3 }} spacing="md">
        {data?.positions.map((p) => (
          <Card
            key={p.symbol}
            component={Link}
            to={`/stocks/${p.symbol}`}
            radius="md"
            withBorder
            padding="lg"
            className="stock-card"
          >
            <Group justify="space-between" mb={4}>
              <Text fw={700} fz="lg" className="mono">{p.symbol}</Text>
              <Badge variant="light" color={p.unrealized_pnl >= 0 ? 'teal' : 'red'}>
                {p.quantity} shares
              </Badge>
            </Group>
            <Text c="dimmed" size="xs" mb="xs">
              Avg cost {fmtMoney(p.avg_cost)}
            </Text>
            <Group justify="space-between" align="baseline">
              <Text fw={600} className="mono">{fmtMoney(p.price)}</Text>
              <Text fw={700} className="mono" c={p.unrealized_pnl >= 0 ? 'teal' : 'red'}>
                {p.unrealized_pnl >= 0 ? '+' : ''}{fmtMoney(p.unrealized_pnl)}
              </Text>
            </Group>
          </Card>
        ))}
      </SimpleGrid>
    </Shell>
  )
}
