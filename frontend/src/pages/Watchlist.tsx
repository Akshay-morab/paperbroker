import { MouseEvent, useCallback, useEffect, useState } from 'react'
import { Group, SimpleGrid, Text, Title } from '@mantine/core'
import Shell from '../components/Shell'
import StockCard from '../components/StockCard'
import { api, Quote } from '../api'

export default function Watchlist() {
  const [items, setItems] = useState<Quote[]>([])

  useEffect(() => {
    let alive = true
    const load = () =>
      api<Quote[]>('/api/watchlist')
        .then((w) => {
          if (alive) setItems(w)
        })
        .catch(() => {})
    load()
    const id = setInterval(load, 5000)
    return () => {
      alive = false
      clearInterval(id)
    }
  }, [])

  const removeStar = useCallback(async (symbol: string, e: MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    await api(`/api/watchlist/${symbol}`, { method: 'DELETE' }).catch(() => {})
    setItems((prev) => prev.filter((q) => q.symbol !== symbol))
  }, [])

  return (
    <Shell>
      <Group justify="space-between" mb="md">
        <Title order={2}>Watchlist</Title>
        <Text c="dimmed" size="xs">
          your starred shares
        </Text>
      </Group>

      {items.length === 0 && (
        <Text c="dimmed" mb="md">
          No shares in your watchlist yet. Tap the star on any share to add it.
        </Text>
      )}

      <SimpleGrid cols={{ base: 2, xs: 3, md: 4, xl: 5 }} spacing="md">
        {items.map((q) => (
          <StockCard key={q.symbol} quote={q} starred onToggleStar={removeStar} />
        ))}
      </SimpleGrid>
    </Shell>
  )
}
