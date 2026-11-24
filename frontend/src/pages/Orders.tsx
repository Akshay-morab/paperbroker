import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Anchor, Badge, Group, Table, Text, Title } from '@mantine/core'
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

      <Table highlightOnHover>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Symbol</Table.Th>
            <Table.Th>Side</Table.Th>
            <Table.Th>Qty</Table.Th>
            <Table.Th>Price</Table.Th>
            <Table.Th>Status</Table.Th>
            <Table.Th>Reason</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {rows.map((o) => (
            <Table.Tr key={o.id}>
              <Table.Td className="mono">
                <Anchor component={Link} to={`/stocks/${o.symbol}`}>
                  {o.symbol}
                </Anchor>
              </Table.Td>
              <Table.Td c={o.side === 'buy' ? 'teal' : 'red'}>{o.side}</Table.Td>
              <Table.Td className="mono">{o.quantity}</Table.Td>
              <Table.Td className="mono">{o.filled_price != null ? fmtMoney(o.filled_price) : '—'}</Table.Td>
              <Table.Td>
                <Badge color={STATUS_COLORS[o.status] ?? 'gray'} variant="light">
                  {o.status}
                </Badge>
              </Table.Td>
              <Table.Td>
                <Text c="dimmed" size="xs">
                  {o.reason ?? ''}
                </Text>
              </Table.Td>
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>
    </Shell>
  )
}
