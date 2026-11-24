import { MouseEvent, useCallback, useEffect, useState } from 'react'
import { Group, SimpleGrid, Text, Title } from '@mantine/core'
import Shell from '../components/Shell'
import StockCard from '../components/StockCard'
import { api, Quote } from '../api'

export default function AllShares() {
  const [quotes, setQuotes] = useState<Quote[]>([])
  const [stars, setStars] = useState<Set<string>>(new Set())

  useEffect(() => {
    let alive = true
    const loadQuotes = () =>
      api<Quote[]>('/api/stocks')
        .then((q) => {
          if (alive) setQuotes(q)
        })
        .catch(() => {})
    const loadStars = () =>
      api<Quote[]>('/api/watchlist')
        .then((w) => {
          if (alive) setStars(new Set(w.map((q) => q.symbol)))
        })
        .catch(() => {})
    loadQuotes()
    loadStars()
    const id = setInterval(loadQuotes, 5000)
    return () => {
      alive = false
      clearInterval(id)
    }
  }, [])

  const toggleStar = useCallback(
    async (symbol: string, e: MouseEvent) => {
      e.preventDefault()
      e.stopPropagation()
      if (stars.has(symbol)) {
        await api(`/api/watchlist/${symbol}`, { method: 'DELETE' }).catch(() => {})
        setStars((prev) => {
          const next = new Set(prev)
          next.delete(symbol)
          return next
        })
      } else {
        await api(`/api/watchlist/${symbol}`, { method: 'POST' }).catch(() => {})
        setStars((prev) => new Set([...prev, symbol]))
      }
    },
    [stars]
  )

  return (
    <Shell>
      <Group justify="space-between" mb="md">
        <Title order={2}>All Shares</Title>
        <Text c="dimmed" size="xs">
          {quotes.length} simulated instruments · prices tick every 3 seconds
        </Text>
      </Group>

      <SimpleGrid cols={{ base: 2, xs: 3, md: 4, xl: 5 }} spacing="md">
        {quotes.map((q) => (
          <StockCard key={q.symbol} quote={q} starred={stars.has(q.symbol)} onToggleStar={toggleStar} />
        ))}
      </SimpleGrid>
    </Shell>
  )
}
