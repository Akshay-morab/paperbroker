import { useEffect, useState } from 'react'
import { Alert, Card, SimpleGrid, Stack, Text, Title } from '@mantine/core'
import Shell from '../components/Shell'
import { api, GuardrailStatus } from '../api'

const fmtMoney = (n: number) => {
  const sign = n < 0 ? '−' : ''
  return sign + '$' + Math.abs(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

export default function Discipline() {
  const [status, setStatus] = useState<GuardrailStatus | null>(null)
  const [countdown, setCountdown] = useState('')

  useEffect(() => {
    let alive = true
    const load = () =>
      api<GuardrailStatus>('/api/guardrails/status')
        .then((s) => {
          if (alive) setStatus(s)
        })
        .catch(() => {})
    load()
    const id = setInterval(load, 5000)
    return () => {
      alive = false
      clearInterval(id)
    }
  }, [])

  // Ticking cooldown countdown (cosmetic; the banner text is server-computed).
  useEffect(() => {
    const tick = () => {
      if (!status?.cooldown.active || !status.cooldown.until) {
        setCountdown('')
        return
      }
      const left = Math.max(
        0,
        Math.floor((new Date(status.cooldown.until).getTime() - Date.now()) / 1000)
      )
      const mm = Math.floor(left / 60)
      const ss = left % 60
      setCountdown(`${mm}:${String(ss).padStart(2, '0')}`)
    }
    tick()
    const id = setInterval(tick, 1000)
    return () => clearInterval(id)
  }, [status])

  return (
    <Shell>
      <Stack gap={0} mb="md">
        <Title order={2}>Discipline</Title>
        <Text c="dimmed" size="sm">
          Every rule, enforced before the fill.
        </Text>
      </Stack>

      {status?.locked && status.lock_reason && (
        <Alert role="alert" color="red" mb="md" maw={560}>
          {status.lock_reason}
        </Alert>
      )}

      {status && (
        <SimpleGrid cols={{ base: 1, xs: 2, md: 3 }} spacing="md">
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Text c="dimmed" size="xs" tt="uppercase" mb="xs">Daily loss limit</Text>
            <Text fz="xl" fw={700} className="mono">{fmtMoney(status.daily_loss.used)}</Text>
            <Text c="dimmed" size="xs">
              of {fmtMoney(status.daily_loss.limit)} — {fmtMoney(status.daily_loss.remaining)} remaining
            </Text>
          </Card>

          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Text c="dimmed" size="xs" tt="uppercase" mb="xs">Trades today</Text>
            <Text fz="xl" fw={700} className="mono">
              {status.trade_cap.used}
              <Text span c="dimmed" fz="xl">/{status.trade_cap.limit}</Text>
            </Text>
            <Text c="dimmed" size="xs">blocked attempts never count</Text>
          </Card>

          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Text c="dimmed" size="xs" tt="uppercase" mb="xs">Tilt cooldown</Text>
            {status.cooldown.active ? (
              <>
                <Text fz="xl" fw={700} className="mono" c="red">{countdown}</Text>
                <Text c="dimmed" size="xs">after 3 consecutive losses</Text>
              </>
            ) : (
              <Text fz="xl" fw={700} c="dimmed">—</Text>
            )}
          </Card>

          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Text c="dimmed" size="xs" tt="uppercase" mb="xs">Position size cap</Text>
            <Text fz="xl" fw={700} className="mono">{status.position_size_pct}%</Text>
            <Text c="dimmed" size="xs">of equity per position</Text>
          </Card>

          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Text c="dimmed" size="xs" tt="uppercase" mb="xs">Open positions</Text>
            <Text fz="xl" fw={700} className="mono">
              {status.state.open_positions}
              <Text span c="dimmed" fz="xl">/{status.open_positions_limit}</Text>
            </Text>
            <Text c="dimmed" size="xs">new symbols blocked at the limit</Text>
          </Card>
        </SimpleGrid>
      )}
    </Shell>
  )
}
