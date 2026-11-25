import { ReactNode, useEffect, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import {
  Anchor,
  AppShell,
  Button,
  Group,
  Loader,
  Menu,
  Modal,
  Stack,
  Text,
  Tooltip,
} from '@mantine/core'
import {
  IconBriefcase,
  IconChartCandle,
  IconId,
  IconInfoCircle,
  IconLogout,
  IconReceipt2,
  IconRefresh,
  IconShield,
  IconStar,
  IconUser,
} from '@tabler/icons-react'
import { api, PortfolioData, Profile } from '../api'

const fmtMoney = (n: number) =>
  '$' + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const NAV = [
  { to: '/', label: 'All Shares', icon: IconChartCandle, tip: 'All shares on the market' },
  { to: '/watchlist', label: 'Watchlist', icon: IconStar, tip: 'Your starred shares' },
  { to: '/portfolio', label: 'Portfolio', icon: IconBriefcase, tip: 'Your holdings and net worth' },
  { to: '/orders', label: 'Orders', icon: IconReceipt2, tip: 'Your full order history' },
  { to: '/discipline', label: 'Discipline', icon: IconShield, tip: 'Your trading guardrails' },
]

/**
 * The app shell: boxed nav pills with tooltips, a clickable brand (About popup),
 * and the corner Profile menu (User Profile Details / Log out).
 */
export default function Shell({ children }: { children: ReactNode }) {
  const nav = useNavigate()
  const loc = useLocation()
  const [profile, setProfile] = useState<Profile | null>(null)
  const [authFailed, setAuthFailed] = useState(false)
  const [profileOpen, setProfileOpen] = useState(false)
  const [aboutOpen, setAboutOpen] = useState(false)
  const [folio, setFolio] = useState<PortfolioData | null>(null)
  const [resetOpen, setResetOpen] = useState(false)
  const [resetState, setResetState] = useState<'confirm' | 'busy' | 'done' | 'error'>('confirm')
  const [resetError, setResetError] = useState('')

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

  useEffect(() => {
    if (!profileOpen) return
    api<PortfolioData>('/api/portfolio')
      .then(setFolio)
      .catch(() => {})
  }, [profileOpen])

  const logout = async () => {
    try {
      await api('/api/auth/logout', { method: 'POST' })
    } catch {
      /* session already gone */
    }
    nav('/login')
  }

  /** Admin-only: re-arm the three demo personas via the existing tested endpoint. */
  const resetPersonas = async () => {
    setResetState('busy')
    try {
      await api('/api/admin/reset-personas', { method: 'POST' })
      setResetState('done')
    } catch (e) {
      setResetError(e instanceof Error ? e.message : 'reset failed')
      setResetState('error')
    }
  }

  return (
    <AppShell header={{ height: 60 }} padding="md">
      <AppShell.Header>
        <Group h="100%" px="md" justify="space-between">
          <Group gap="lg">
            <Text
              fw={700}
              fz="lg"
              className="brand"
              onClick={() => setAboutOpen(true)}
              title="What is PaperBroker?"
            >
              PaperBroker
            </Text>
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

          {/* Corner profile tab: two options only (user feedback, Nov 25). */}
          <Menu shadow="md" width={230} position="bottom-end">
            <Menu.Target>
              <Button variant="subtle" size="xs" leftSection={<IconUser size={15} />}>
                Profile
              </Button>
            </Menu.Target>
            <Menu.Dropdown>
              <Menu.Item
                leftSection={<IconId size={14} />}
                onClick={() => setProfileOpen(true)}
              >
                User Profile Details
              </Menu.Item>
              {profile?.role === 'admin' && (
                <Menu.Item
                  leftSection={<IconRefresh size={14} />}
                  onClick={() => {
                    setResetState('confirm')
                    setResetOpen(true)
                  }}
                >
                  Reset demo personas
                </Menu.Item>
              )}
              <Menu.Divider />
              <Menu.Item color="red" leftSection={<IconLogout size={14} />} onClick={logout}>
                Log out
              </Menu.Item>
            </Menu.Dropdown>
          </Menu>
        </Group>
      </AppShell.Header>

      <AppShell.Main>{children}</AppShell.Main>

      <Modal
        opened={aboutOpen}
        onClose={() => setAboutOpen(false)}
        centered
        radius="lg"
        title={
          <Group gap="xs">
            <IconInfoCircle size={18} />
            <span>About PaperBroker</span>
          </Group>
        }
      >
        <Text size="sm" mb="xs">
          PaperBroker is an app used for trading — a simulated stock broker where you buy and
          sell shares with $100,000 of practice money.
        </Text>
        <Text size="sm" c="dimmed">
          A discipline engine enforces your trading rules, and every flow is verified
          end-to-end by Kane CLI in a real browser.
        </Text>
      </Modal>

      <Modal
        opened={profileOpen}
        onClose={() => setProfileOpen(false)}
        centered
        radius="lg"
        title="User Profile Details"
      >
        {profile && (
          <Stack gap="xs">
            <Text size="sm">
              Email: <strong>{profile.email}</strong>
            </Text>
            <Text size="sm">
              Cash: <strong>{fmtMoney(profile.cash)}</strong>
            </Text>
            {folio && (
              <>
                <Text size="sm">
                  Net worth: <strong>{fmtMoney(folio.equity)}</strong>
                </Text>
                <Text size="sm">
                  Open positions: <strong>{folio.positions.length}</strong>
                </Text>
              </>
            )}
          </Stack>
        )}
      </Modal>

      {/* Admin-only: confirm + result for the persona re-arm (existing endpoint). */}
      <Modal
        opened={resetOpen}
        onClose={() => setResetOpen(false)}
        centered
        radius="lg"
        title="Reset demo personas"
      >
        {resetState === 'confirm' && (
          <Stack gap="sm">
            <Text size="sm">
              Rebuild the three demo accounts — <strong>fresh@demo</strong>,{' '}
              <strong>tilted@demo</strong> and <strong>cooldown@demo</strong>. Their trades,
              holdings and stars are wiped, and the personas are re-armed: tilted returns to
              one sell away from the kill switch.
            </Text>
            <Group justify="flex-end" gap="xs">
              <Button variant="default" size="xs" onClick={() => setResetOpen(false)}>
                Cancel
              </Button>
              <Button color="red" size="xs" onClick={resetPersonas}>
                Reset personas
              </Button>
            </Group>
          </Stack>
        )}
        {resetState === 'busy' && (
          <Group gap="xs">
            <Loader size="xs" />
            <Text size="sm">Re-arming personas…</Text>
          </Group>
        )}
        {resetState === 'done' && (
          <Stack gap="sm">
            <Text size="sm" c="teal">
              Personas re-armed. tilted@demo is one sell away from the kill switch.
            </Text>
            <Group justify="flex-end">
              <Button size="xs" onClick={() => setResetOpen(false)}>
                Done
              </Button>
            </Group>
          </Stack>
        )}
        {resetState === 'error' && (
          <Stack gap="sm">
            <Text size="sm" c="red">
              {resetError}
            </Text>
            <Group justify="flex-end">
              <Button variant="default" size="xs" onClick={() => setResetOpen(false)}>
                Close
              </Button>
            </Group>
          </Stack>
        )}
      </Modal>
    </AppShell>
  )
}
