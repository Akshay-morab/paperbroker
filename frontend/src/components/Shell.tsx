import { ReactNode, useEffect, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Alert, Anchor, AppShell, Button, Group, Text } from '@mantine/core'
import { api, Profile } from '../api'

const fmtMoney = (n: number) =>
  '$' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const NAV = [
  { to: '/', label: 'Watchlist' },
  { to: '/portfolio', label: 'Portfolio' },
  { to: '/orders', label: 'Orders' },
  { to: '/discipline', label: 'Discipline' },
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
              <Anchor
                key={item.to}
                component={Link}
                to={item.to}
                c={loc.pathname === item.to ? 'indigo' : 'dimmed'}
                fz="sm"
              >
                {item.label}
              </Anchor>
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
