import { useEffect, useState } from 'react'
import { Badge, Group, Paper, Stack, Text, Title } from '@mantine/core'
import Shell from '../components/Shell'
import { api, PlacedOrder } from '../api'

const fmtMoney = (n: number) =>
  '$' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const STATUS_COLORS: Record<string, string> = {
  filled: 'green',
  rejected: 'orange',
  blocked: 'red',
}

export default function Orders() {
  const [rows, setRows] = useState<PlacedOrder[]>([])

  useEffect(() => {
    api<PlacedOrder[]>('/api/orders')
      .then(setRows)
      .catch(() => {})
  }, [])

  return (
    <Shell>
      <Group justify="space-between" mb="md">
        <Title order={2}>Order history</Title>
        <Text c="dimmed" size="xs">
          every attempt is recorded — fills, rejects, and blocks
        </Text>
      </Group>

      {rows.length === 0 && (
        <Text c="dimmed" mb="md">
          No orders yet.
        </Text>
      )}

      <Stack gap="sm">
        {rows.map((o) => (
          <Paper key={o.id} radius="md" withBorder p="sm" className="order-row">
            <Group wrap="nowrap" justify="space-between">
              <Group gap="sm" wrap="nowrap">
                <Badge color={o.side === 'buy' ? 'teal' : 'red'} variant="light">
                  {o.side}
                </Badge>
                <div>
                  <Text size="sm">
                    <strong>{o.side === 'buy' ? 'Bought' : 'Sold'} {o.quantity} {o.symbol}</strong>
                    {o.filled_price != null ? ` @ ${fmtMoney(o.filled_price)}` : ''}
                  </Text>
                  {o.reason && (
                    <Text size="xs" c="dimmed">{o.reason}</Text>
                  )}
                </div>
              </Group>
              <Group gap="sm" wrap="nowrap">
                {o.realized_pnl != null && (
                  <Text size="sm" className="mono" c={o.realized_pnl >= 0 ? 'teal' : 'red'}>
                    {o.realized_pnl >= 0 ? '+' : ''}{fmtMoney(o.realized_pnl)}
                  </Text>
                )}
                <Badge color={STATUS_COLORS[o.status] ?? 'gray'} variant="light">
                  {o.status}
                </Badge>
              </Group>
            </Group>
          </Paper>
        ))}
      </Stack>
    </Shell>
  )
}
