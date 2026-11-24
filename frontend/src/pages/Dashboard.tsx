import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Anchor, Table, Text, Title } from '@mantine/core'
import Shell from '../components/Shell'
import { api, Quote } from '../api'

const fmtMoney = (n: number) =>
  '$' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

export default function Dashboard() {
  const [quotes, setQuotes] = useState<Quote[]>([])

  useEffect(() => {
    let alive = true
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
  }, [])

  return (
    <Shell>
      <Title order={2} mb="md">Watchlist</Title>
      <Table highlightOnHover>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Symbol</Table.Th>
            <Table.Th>Name</Table.Th>
            <Table.Th>Price</Table.Th>
            <Table.Th>Change</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {quotes.map((q) => (
            <Table.Tr key={q.symbol}>
              <Table.Td className="mono">
                <Anchor component={Link} to={`/stocks/${q.symbol}`}>
                  {q.symbol}
                </Anchor>
              </Table.Td>
              <Table.Td>{q.name}</Table.Td>
              <Table.Td className="mono">{fmtMoney(q.price)}</Table.Td>
              <Table.Td className="mono" c={q.change_pct >= 0 ? 'teal' : 'red'}>
                {q.change_pct >= 0 ? '+' : ''}
                {q.change_pct.toFixed(2)}%
              </Table.Td>
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>
      <Text c="dimmed" size="xs" mt="sm">
        Simulated market — prices tick every 3 seconds.
      </Text>
    </Shell>
  )
}
