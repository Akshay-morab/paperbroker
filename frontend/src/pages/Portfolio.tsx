import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Anchor, Group, Table, Text, Title } from '@mantine/core'
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
      <Group justify="space-between" mb="md">
        <Title order={2}>Portfolio</Title>
        {data && (
          <Text size="sm">
            Equity: <strong>{fmtMoney(data.equity)}</strong>
          </Text>
        )}
      </Group>

      {data && data.positions.length === 0 && (
        <Text c="dimmed" mb="md">
          No positions yet.
        </Text>
      )}

      <Table highlightOnHover>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Symbol</Table.Th>
            <Table.Th>Qty</Table.Th>
            <Table.Th>Avg cost</Table.Th>
            <Table.Th>Price</Table.Th>
            <Table.Th>Market value</Table.Th>
            <Table.Th>Unrealized P&L</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {data?.positions.map((p) => (
            <Table.Tr key={p.symbol}>
              <Table.Td className="mono">
                <Anchor component={Link} to={`/stocks/${p.symbol}`}>
                  {p.symbol}
                </Anchor>
              </Table.Td>
              <Table.Td className="mono">{p.quantity}</Table.Td>
              <Table.Td className="mono">{fmtMoney(p.avg_cost)}</Table.Td>
              <Table.Td className="mono">{fmtMoney(p.price)}</Table.Td>
              <Table.Td className="mono">{fmtMoney(p.market_value)}</Table.Td>
              <Table.Td className="mono" c={p.unrealized_pnl >= 0 ? 'teal' : 'red'}>
                {p.unrealized_pnl >= 0 ? '+' : ''}
                {fmtMoney(p.unrealized_pnl)}
              </Table.Td>
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>
    </Shell>
  )
}
