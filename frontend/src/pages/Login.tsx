import { FormEvent, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Alert, Button, Card, Center, PasswordInput, Stack, Text, TextInput, Title } from '@mantine/core'
import { api } from '../api'

export default function Login() {
  const nav = useNavigate()
  const [mode, setMode] = useState<'login' | 'signup'>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function submit(e: FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError('')
    try {
      await api(`/api/auth/${mode}`, {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
      nav('/')
    } catch (err) {
      // Backend reason strings render verbatim — Kane asserts on them.
      setError(err instanceof Error ? err.message : 'request failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <Center mih="100vh" p="md">
      <Card shadow="sm" padding="xl" radius="md" withBorder maw={400} w="100%">
        <Title order={3}>PaperBroker</Title>
        <Text c="dimmed" size="sm" mb="md">
          A paper-trading broker with a discipline engine.
        </Text>
        <form onSubmit={submit}>
          <Stack>
            <TextInput
              id="email"
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.currentTarget.value)}
              required
              autoFocus
            />
            <PasswordInput
              id="password"
              label="Password"
              value={password}
              onChange={(e) => setPassword(e.currentTarget.value)}
              required
              minLength={8}
            />
            {error && (
              <Alert role="alert" color="red">
                {error}
              </Alert>
            )}
            <Button type="submit" loading={busy}>
              {mode === 'login' ? 'Log in' : 'Create account'}
            </Button>
          </Stack>
        </form>
        <Button
          variant="subtle"
          mt="xs"
          onClick={() => {
            setMode(mode === 'login' ? 'signup' : 'login')
            setError('')
          }}
        >
          {mode === 'login' ? 'Need an account? Sign up' : 'Have an account? Log in'}
        </Button>
        <Text c="dimmed" size="xs" mt="md">
          Demo personas: fresh@demo · tilted@demo · cooldown@demo — password demo1234
        </Text>
      </Card>
    </Center>
  )
}
