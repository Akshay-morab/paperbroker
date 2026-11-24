import { MouseEvent } from 'react'
import { Link } from 'react-router-dom'
import { ActionIcon, Badge, Card, Group, Stack, Text } from '@mantine/core'
import { IconStar, IconStarFilled } from '@tabler/icons-react'
import SymbolAvatar from './SymbolAvatar'
import { Quote } from '../api'

const fmtMoney = (n: number) =>
  '$' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

/** One large clickable stock card. The whole card is the link; the star toggles
 * the per-user watchlist without navigating (click is intercepted). */
export default function StockCard({
  quote,
  starred,
  onToggleStar,
}: {
  quote: Quote
  starred: boolean
  onToggleStar: (symbol: string, e: MouseEvent) => void
}) {
  return (
    <Card
      component={Link}
      to={`/stocks/${quote.symbol}`}
      radius="md"
      withBorder
      shadow="sm"
      padding="lg"
      className="stock-card"
    >
      <Stack gap={2}>
        <Group justify="space-between" gap="xs" wrap="nowrap">
          <Group gap="xs" wrap="nowrap">
            <SymbolAvatar symbol={quote.symbol} size={30} />
            <Text fw={700} fz="lg" className="mono">
              {quote.symbol}
            </Text>
          </Group>
          <ActionIcon
            variant={starred ? 'filled' : 'subtle'}
            color="indigo"
            size="sm"
            radius="md"
            title={starred ? 'Remove from watchlist' : 'Add to watchlist'}
            onClick={(e) => onToggleStar(quote.symbol, e)}
          >
            {starred ? <IconStarFilled size={14} /> : <IconStar size={14} />}
          </ActionIcon>
        </Group>
        <Text c="dimmed" size="xs" lineClamp={1}>
          {quote.name}
        </Text>
        <Group justify="space-between" mt="xs" wrap="nowrap">
          <Text fz="xl" fw={700} className="mono">
            {fmtMoney(quote.price)}
          </Text>
          <Badge color={quote.change_pct >= 0 ? 'teal' : 'red'} variant="light" size="sm">
            {quote.change_pct >= 0 ? '+' : ''}
            {quote.change_pct.toFixed(2)}%
          </Badge>
        </Group>
      </Stack>
    </Card>
  )
}
