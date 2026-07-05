import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'
import { CircleAlert, X } from 'lucide-react'
import type { Message, Session } from '@/types'
import { DEFAULT_WEIGHTS } from '@/types'
import { cn } from '@/lib/cn'
import { ChatShell } from '@/components/layout/ChatShell'
import { Sidebar } from '@/components/sidebar/Sidebar'
import { ChatThread } from '@/components/chat/ChatThread'
import { Composer, type ComposerPayload } from '@/components/composer/Composer'
import { AuthPage } from '@/components/auth/AuthPage'
import { useAuth } from '@/lib/auth'
import { useI18n } from '@/lib/i18n'
import { saveDraft, takeDraft } from '@/lib/draft'
import {
  createSession,
  deleteSession,
  fetchResult,
  fetchSessionDetail,
  fetchSessions,
  humanizeError,
  pollResult,
  sendMessage,
} from '@/lib/api'

let seq = 0
const uid = (p: string) => `${p}_${Date.now().toString(36)}${seq++}`

export function App() {
  const navigate = useNavigate()
  const location = useLocation()
  const { sessionId } = useParams()
  const { user, logout } = useAuth()
  const { t } = useI18n()
  const authed = user !== null

  const isAuthRoute = location.pathname === '/auth'

  // Where to return after closing/completing auth. While the overlay is open
  // the chat behind keeps showing the last visited session.
  const returnPathRef = useRef('/')
  useEffect(() => {
    if (!isAuthRoute) returnPathRef.current = location.pathname
  }, [isAuthRoute, location.pathname])

  const activeId = isAuthRoute
    ? returnPathRef.current.replace(/^\//, '') || null
    : sessionId ?? null

  const [sessions, setSessions] = useState<Session[]>([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyError, setHistoryError] = useState<string | null>(null)
  const [historyNonce, setHistoryNonce] = useState(0)
  const [threadLoading, setThreadLoading] = useState(false)
  const [notice, setNotice] = useState<string | null>(null)
  const [prefill, setPrefill] = useState({ text: '', nonce: 0 })

  const active = useMemo(
    () => sessions.find((s) => s.id === activeId) ?? null,
    [sessions, activeId],
  )

  const busy =
    active?.messages.some((m) => m.role === 'assistant' && m.status === 'thinking') ?? false

  const patch = useCallback((id: string, update: (s: Session) => Session) => {
    setSessions((prev) => prev.map((s) => (s.id === id ? update(s) : s)))
  }, [])

  const patchMessage = useCallback(
    (sessId: string, msgId: string, update: (m: Message) => Message) => {
      patch(sessId, (s) => ({
        ...s,
        messages: s.messages.map((m) => (m.id === msgId ? update(m) : m)),
      }))
    },
    [patch],
  )

  const openAuth = useCallback(() => {
    if (location.pathname !== '/auth') navigate('/auth')
  }, [location.pathname, navigate])

  const closeAuth = useCallback(() => {
    navigate(returnPathRef.current || '/', { replace: true })
  }, [navigate])

  // -------------------------------------------------------------------------
  // History: load the session list when logged in, clear it on logout.

  useEffect(() => {
    if (!authed) {
      setSessions([])
      setHistoryError(null)
      setHistoryLoading(false)
      return
    }
    let cancelled = false
    setHistoryLoading(true)
    setHistoryError(null)
    fetchSessions()
      .then((list) => {
        if (cancelled) return
        // Keep already-hydrated sessions (optimistic ones from this tab).
        setSessions((prev) => {
          const known = new Map(prev.map((s) => [s.id, s]))
          const merged = list.map((s) => known.get(s.id) ?? s)
          const extra = prev.filter((s) => !merged.some((m) => m.id === s.id))
          return [...extra, ...merged]
        })
      })
      .catch((e) => {
        if (!cancelled) setHistoryError(humanizeError(e))
      })
      .finally(() => {
        if (!cancelled) setHistoryLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [authed, historyNonce])

  // -------------------------------------------------------------------------
  // Thread: hydrate the active session (messages + results) on demand.

  const hydratingRef = useRef(new Set<string>())

  useEffect(() => {
    if (!authed || !activeId || !activeId.startsWith('sess_')) return
    const current = sessions.find((s) => s.id === activeId)
    if (current?.loaded || hydratingRef.current.has(activeId)) return

    hydratingRef.current.add(activeId)
    setThreadLoading(true)

    fetchSessionDetail(activeId)
      .then(async (detail) => {
        setSessions((prev) => {
          const exists = prev.some((s) => s.id === detail.id)
          if (!exists) return [detail, ...prev]
          return prev.map((s) => {
            if (s.id !== detail.id) return s
            // Keep optimistic messages sent while the history was loading.
            const local = s.messages.filter((m) => m.id.startsWith('local_msg'))
            return { ...detail, messages: [...detail.messages, ...local] }
          })
        })
        // Backfill results for finished messages that came without one and
        // resume polling for anything still in the pipeline.
        const pending = detail.messages.filter(
          (m): m is Extract<Message, { role: 'assistant' }> =>
            m.role === 'assistant' && ((m.status === 'done' && !m.result) || m.status === 'thinking'),
        )
        await Promise.all(
          pending.map(async (m) => {
            try {
              if (m.status === 'thinking') {
                const result = await pollResult(detail.id, m.id)
                patchMessage(detail.id, m.id, () => ({ ...m, status: 'done', result }))
              } else {
                const r = await fetchResult(detail.id, m.id)
                if (r.state === 'done') {
                  patchMessage(detail.id, m.id, () => ({ ...m, result: r.result }))
                }
              }
            } catch (e) {
              patchMessage(detail.id, m.id, () => ({
                ...m,
                status: 'failed',
                error: humanizeError(e),
              }))
            }
          }),
        )
      })
      .catch((e) => setNotice(humanizeError(e)))
      .finally(() => {
        hydratingRef.current.delete(activeId)
        setThreadLoading(false)
      })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authed, activeId, sessions])

  // -------------------------------------------------------------------------
  // Sending

  const handleSend = useCallback(
    async (payload: ComposerPayload) => {
      const problem = payload.problem.trim()
      if (!problem) return

      // Guests: stash the message (with settings and files) and glide to the
      // auth screen. It will be sent automatically right after login.
      if (!authed) {
        saveDraft({
          problem,
          constraints: payload.constraints,
          weights: payload.weights,
          files: payload.files,
        })
        openAuth()
        return
      }

      if (busy) return
      setNotice(null)

      let sessId = active?.id ?? null
      const iteration = active
        ? active.messages.filter((m) => m.role === 'assistant').length
        : 0

      const userMsg: Message = {
        id: uid('local_msg'),
        role: 'user',
        content: problem,
        files: payload.files.map((f) => f.name),
      }
      const thinkingId = uid('local_msg')
      const thinking: Message = {
        id: thinkingId,
        role: 'assistant',
        status: 'thinking',
        iteration,
      }

      if (!sessId) {
        // A session carries constraints/weights, so it must exist first.
        try {
          const created = await createSession({
            title: problem.slice(0, 120),
            constraints: payload.constraints,
            weights: payload.weights,
          })
          sessId = created.id
          setSessions((prev) => [
            { ...created, messages: [userMsg, thinking] },
            ...prev,
          ])
          navigate(`/${sessId}`)
        } catch (e) {
          setNotice(humanizeError(e))
          setPrefill((p) => ({ text: problem, nonce: p.nonce + 1 }))
          return
        }
      } else {
        patch(sessId, (s) => ({ ...s, messages: [...s.messages, userMsg, thinking] }))
      }

      try {
        const { messageId } = await sendMessage(sessId, problem, payload.files)
        const result = await pollResult(sessId, messageId)
        patchMessage(sessId, thinkingId, () => ({
          id: messageId,
          role: 'assistant',
          status: 'done',
          iteration,
          result,
        }))
      } catch (e) {
        patchMessage(sessId, thinkingId, (m) => ({
          ...m,
          role: 'assistant',
          status: 'failed',
          iteration,
          error: humanizeError(e),
        }))
      }
    },
    [authed, busy, active, navigate, openAuth, patch, patchMessage],
  )

  // After a successful login, replay the saved draft: the user lands back in
  // the chat and sees their own message (with settings and files) already sent.
  useEffect(() => {
    if (!authed || isAuthRoute) return
    const draft = takeDraft()
    if (draft) {
      void handleSend({
        problem: draft.problem,
        constraints: draft.constraints,
        weights: draft.weights,
        files: draft.files,
      })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authed, isAuthRoute])

  const handleLogout = useCallback(() => {
    logout()
    navigate('/', { replace: true })
  }, [logout, navigate])

  const handleDeleteSession = useCallback(
    async (id: string) => {
      try {
        await deleteSession(id)
        setSessions((prev) => prev.filter((s) => s.id !== id))
        if (activeId === id) {
          navigate('/', { replace: true })
        }
      } catch (e) {
        setNotice(humanizeError(e))
      }
    },
    [activeId, navigate],
  )

  return (
    <div className="relative h-[100dvh] overflow-hidden">
      {/* Chat shell eases back as the two auth panels slide in from the edges
          and close over it. Only transform is animated — opacity/filter on this
          subtree breaks the backdrop-blur glass buttons inside. */}
      <div
        className={cn(
          'h-full transition-transform duration-[650ms] ease-[cubic-bezier(0.22,1,0.36,1)]',
          isAuthRoute && 'pointer-events-none scale-[0.97]',
        )}
        aria-hidden={isAuthRoute}
      >
        <ChatShell
          sidebar={
            <Sidebar
              sessions={sessions}
              activeId={activeId}
              user={user}
              historyLoading={historyLoading}
              historyError={historyError}
              onSelect={(id) => navigate(`/${id}`)}
              onNew={() => navigate('/')}
              onLogin={openAuth}
              onLogout={handleLogout}
              onRetryHistory={() => setHistoryNonce((n) => n + 1)}
              onDelete={handleDeleteSession}
            />
          }
          composer={
            <div className="flex flex-col gap-2">
              {/* Inline error banner — animated height reveal */}
              <div
                className={cn(
                  'grid transition-[grid-template-rows] duration-300 ease-out',
                  notice ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]',
                )}
              >
                <div className="min-h-0 overflow-hidden">
                  <div className="flex items-start gap-2.5 rounded-2xl border border-red-100 bg-red-50/80 px-4 py-3">
                    <CircleAlert className="mt-0.5 h-4 w-4 shrink-0 text-red-500" />
                    <p className="min-w-0 flex-1 text-[13px] leading-relaxed text-red-600">
                      {notice}
                    </p>
                    <button
                      type="button"
                      onClick={() => setNotice(null)}
                      className="grid h-6 w-6 shrink-0 place-items-center rounded-md text-red-400 transition-colors hover:bg-red-100 hover:text-red-600"
                      aria-label={t('app.hideError')}
                    >
                      <X className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>
              </div>

              <Composer
                busy={busy}
                threadKey={activeId ?? 'new'}
                prefill={prefill}
                initialWeights={active?.weights ?? DEFAULT_WEIGHTS}
                onSend={handleSend}
              />
            </div>
          }
        >
          <ChatThread
            messages={active?.messages ?? []}
            loading={threadLoading}
            authenticated={authed}
            sessionId={activeId ?? undefined}
            onExampleSelect={(text) => setPrefill((p) => ({ text, nonce: p.nonce + 1 }))}
            onLogin={openAuth}
          />
        </ChatShell>
      </div>

      <AuthPage active={isAuthRoute} onClose={closeAuth} onSuccess={closeAuth} />
    </div>
  )
}
