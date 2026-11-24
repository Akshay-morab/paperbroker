import { useEffect, useState } from 'react'
import { Alert, Badge, Group, Menu, Modal, Paper, Stack, Text, Title } from '@mantine/core'
import Shell from '../components/Shell'
import SymbolAvatar from '../components/SymbolAvatar'
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
  const [selected, setSelected] = useState<PlacedOrder | null>(null)

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
          every attempt is recorded — click any entry for details
        </Text>
      </Group>

      {rows.length === 0 && (
        <Text c="dimmed" mb="md">
          No orders yet.
        </Text>
      )}

      <Stack gap="sm">
        {rows.map((o) => (
          <Paper
            key={o.id}
            radius="md"
            withBorder
            p="sm"
            className="order-row"
            onClick={() => setSelected(o)}
          >
            <Group wrap="nowrap" justify="space-between">
              <Group gap="sm" wrap="nowrap">
                <SymbolAvatar symbol={o.symbol} size={30} />
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

      {/* Order details modal (user feedback, Nov 25): shares, price, total cost, status. */}
      <Modal
        opened={!!selected}
        onClose={() => setSelected(null)}
        centered
        radius="lg"
        title="Order details"
      >
        {selected && (
          <Stack gap="xs">
            <Group gap="sm">
              <SymbolAvatar symbol={selected.symbol} size={38} />
              <div>
                <Text fw={600}>
                  {selected.side === 'buy' ? 'Bought' : 'Sold'} {selected.quantity} {selected.symbol}
                </Text>
                <Badge color={selected.side === 'buy' ? 'teal' : 'red'} variant="light">
                  {selected.side}
                </Badge>
              </div>
            </Group>
            <Text size="sm">
              Shares: <strong>{selected.quantity}</strong>
            </Text>
            <Text size="sm">
              Price:{' '}
              <strong>{selected.filled_price != null ? fmtMoney(selected.filled_price) : '—'}</strong>
            </Text>
            <Text size="sm">
              Total:{' '}
              <strong>{fmtMoney((selected.filled_price ?? 0) * selected.quantity)}</strong>
            </Text>
            <Text size="sm">
              Status:{' '}
              <Badge color={STATUS_COLORS[selected.status] ?? 'gray'} variant="light">
                {selected.status}
              </Badge>
            </Text>
            {selected.status === 'filled' ? (
              <Alert role="status" color="teal" mt="xs">
                Order filled successfully.
              </Alert>
            ) : (
              selected.reason && (
                <Alert role="alert" color="red" mt="xs">
                  {selected.reason}
                </Alert>
              )
            )}
          </Stack>
        )}
      </Modal>
    </Shell>
  )
}
