import { ReactNode, useEffect, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Alert, Anchor, AppShell, Button, Group, Text, Tooltip } from '@mantine/core'
import {
  IconBriefcase,
  IconChartCandle,
  IconReceipt2,
  IconShield,
} from '@tabler/icons-react'
import { api, Profile } from '../api'

const fmtMoney = (n: number) =>
  '$' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const NAV = [
  { to: '/', label: 'Watchlist', icon: IconChartCandle, tip: 'Your watchlist of shares' },
  { to: '/portfolio', label: 'Portfolio', icon: IconBriefcase, tip: 'Your holdings and net worth' },
  { to: '/orders', label: 'Orders', icon: IconReceipt2, tip: 'Your full order history' },
  { to: '/discipline', label: 'Discipline', icon: IconShield, tip: 'Your trading guardrails' },
]

/**
 * The app shell: header with nav, signed-in identity, cash, and logout.
 * Kane-asserted text lives here and must stay byte-exact:
 *   "Signed in as <email>", "Cash: $100,000.00", "Log out".
 */
export default function Shell({ children }: { children: ReactNode }) {
  const nav = useNavigate()
  const loc = useLocation()
  const [profile, setProfile] = useState<Profile | null>(null)
  const [authFailed, setAuthFailed] = useState(false)

  useEffect(() => {
    let alive = true
    api<Profile>('/api/me')
      .then((p) => {
        if (alive) setProfile(p)
      })
      .catch(() => {
        if (alive) setAuthFailed(true)
      })
    return () => {
      alive = false
    }
  }, [])

  useEffect(() => {
    if (authFailed) nav('/login')
  }, [authFailed, nav])

  const logout = async () => {
    try {
      await api('/api/auth/logout', { method: 'POST' })
    } catch {
      /* session already gone */
    }
    nav('/login')
  }

  return (
    <AppShell header={{ height: 60 }} padding="md">
      <AppShell.Header>
        <Group h="100%" px="md" justify="space-between" wrap="nowrap">
          <Group gap="lg">
            <Text fw={700} fz="lg">PaperBroker</Text>
            {NAV.map((item) => (
              <Tooltip key={item.to} label={item.tip} position="bottom" withArrow openDelay={200}>
                <Anchor
                  component={Link}
                  to={item.to}
                  className={`nav-pill ${loc.pathname === item.to ? 'nav-pill-active' : ''}`}
                >
                  <item.icon size={15} stroke={1.75} />
                  <span>{item.label}</span>
                </Anchor>
              </Tooltip>
            ))}
          </Group>
          <Group gap="md" wrap="nowrap">
            {profile && (
              <>
                <Text size="sm" c="dimmed" visibleFrom="xs">
                  Signed in as {profile.email}
                </Text>
                <Text size="sm">
                  Cash: <strong>{fmtMoney(profile.cash)}</strong>
                </Text>
              </>
            )}
            <Button variant="subtle" size="xs" onClick={logout}>
              Log out
            </Button>
          </Group>
        </Group>
      </AppShell.Header>

      <AppShell.Main>{children}</AppShell.Main>
    </AppShell>
  )
}
