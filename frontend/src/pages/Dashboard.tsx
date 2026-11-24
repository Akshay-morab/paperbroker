import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Badge, Card, Group, SimpleGrid, Stack, Text, Title } from '@mantine/core'
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
      <Group justify="space-between" mb="md">
        <Title order={2}>Watchlist</Title>
        <Text c="dimmed" size="xs">
          {quotes.length} simulated instruments · prices tick every 3 seconds
        </Text>
      </Group>

      <SimpleGrid cols={{ base: 2, xs: 3, md: 4, xl: 5 }} spacing="md">
        {quotes.map((q) => (
          // The whole card is the link — click anywhere on it to open the stock.
          <Card
            key={q.symbol}
            component={Link}
            to={`/stocks/${q.symbol}`}
            radius="md"
            withBorder
            shadow="sm"
            padding="lg"
            className="stock-card"
          >
            <Stack gap={2}>
              <Group justify="space-between" gap="xs">
                <Text fw={700} fz="lg" className="mono">
                  {q.symbol}
                </Text>
                <Badge color={q.change_pct >= 0 ? 'teal' : 'red'} variant="light" size="sm">
                  {q.change_pct >= 0 ? '+' : ''}
                  {q.change_pct.toFixed(2)}%
                </Badge>
              </Group>
              <Text c="dimmed" size="xs" lineClamp={1}>
                {q.name}
              </Text>
              <Text fz="xl" fw={700} className="mono" mt="xs">
                {fmtMoney(q.price)}
              </Text>
            </Stack>
          </Card>
        ))}
      </SimpleGrid>
    </Shell>
  )
}
