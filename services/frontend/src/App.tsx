import { useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import type { Message, Session } from '@/types'
import { DEFAULT_WEIGHTS } from '@/types'
import { ChatShell } from '@/components/layout/ChatShell'
import { Sidebar } from '@/components/sidebar/Sidebar'
import { ChatThread } from '@/components/chat/ChatThread'
import { Composer, type ComposerPayload } from '@/components/composer/Composer'
import { generateHypothesis } from '@/lib/api'
import { MOCK_SESSIONS } from '@/data/mock'

let seq = 0
const uid = (p: string) => `${p}_${Date.now().toString(36)}${seq++}`

export function App() {
  const navigate = useNavigate()
  const { sessionId } = useParams()
  const activeId = sessionId ?? null

  const [sessions, setSessions] = useState<Session[]>(MOCK_SESSIONS)
  const [prefill, setPrefill] = useState({ text: '', nonce: 0 })

  const active = useMemo(
    () => sessions.find((s) => s.id === activeId) ?? null,
    [sessions, activeId],
  )

  const busy =
    active?.messages.some((m) => m.role === 'assistant' && m.status === 'thinking') ?? false

  const patch = (id: string, update: (s: Session) => Session) =>
    setSessions((prev) => prev.map((s) => (s.id === id ? update(s) : s)))

  const handleSend = async (payload: ComposerPayload) => {
    if (busy || !payload.problem.trim()) return

    const iteration = active
      ? active.messages.filter((m) => m.role === 'assistant').length
      : 0

    const userMsg: Message = {
      id: uid('msg'),
      role: 'user',
      content: payload.problem.trim(),
      files: payload.files,
    }
    const thinkingId = uid('msg')
    const thinking: Message = { id: thinkingId, role: 'assistant', status: 'thinking', iteration }

    let sessionId = active?.id
    if (!sessionId) {
      sessionId = uid('sess')
      const session: Session = {
        id: sessionId,
        title: payload.problem.trim(),
        createdAt: new Date().toISOString(),
        constraints: payload.constraints,
        weights: payload.weights,
        messages: [userMsg, thinking],
      }
      setSessions((prev) => [session, ...prev])
      navigate(`/${sessionId}`)
    } else {
      patch(sessionId, (s) => ({ ...s, messages: [...s.messages, userMsg, thinking] }))
    }

    const result = await generateHypothesis({
      problem: payload.problem,
      constraints: payload.constraints,
      weights: payload.weights,
      files: payload.files,
      iteration,
    })

    patch(sessionId, (s) => ({
      ...s,
      messages: s.messages.map((m) =>
        m.id === thinkingId
          ? { id: m.id, role: 'assistant', status: 'done', iteration, result }
          : m,
      ),
    }))
  }

  return (
    <ChatShell
      sidebar={
        <Sidebar
          sessions={sessions}
          activeId={activeId}
          onSelect={(id) => navigate(`/${id}`)}
          onNew={() => navigate('/')}
        />
      }
      composer={
        <Composer
          busy={busy}
          threadKey={activeId ?? 'new'}
          prefill={prefill}
          initialWeights={active?.weights ?? DEFAULT_WEIGHTS}
          onSend={handleSend}
        />
      }
    >
      <ChatThread
        messages={active?.messages ?? []}
        onExampleSelect={(text) => setPrefill((p) => ({ text, nonce: p.nonce + 1 }))}
      />
    </ChatShell>
  )
}
