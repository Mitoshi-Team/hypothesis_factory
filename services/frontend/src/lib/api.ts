// HTTP client for the API Gateway, per docs/API_CONTRACT.md.
// Handles bearer auth, transparent access-token refresh (single-flight),
// the unified `{ error: { code, message, details } }` envelope and
// long-polling of pipeline results.

import type { HypothesisResult, Message, Session, User, Weights } from '@/types'
import { DEFAULT_WEIGHTS } from '@/types'

const API_BASE =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://localhost:8000/api/v1'

// ---------------------------------------------------------------------------
// Errors

export type ApiErrorCode =
  | 'VALIDATION_ERROR'
  | 'UNAUTHORIZED'
  | 'FORBIDDEN'
  | 'NOT_FOUND'
  | 'INTERNAL_SERVER_ERROR'
  | 'NETWORK_ERROR'
  | 'TIMEOUT'
  | 'PIPELINE_FAILED'
  | 'UNKNOWN'

export class ApiError extends Error {
  code: ApiErrorCode
  status?: number
  details?: Record<string, unknown>

  constructor(
    code: ApiErrorCode,
    message: string,
    opts: { status?: number; details?: Record<string, unknown> } = {},
  ) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = opts.status
    this.details = opts.details
  }
}

const ERROR_MESSAGES: Record<ApiErrorCode, string> = {
  VALIDATION_ERROR: 'Проверьте правильность заполненных данных.',
  UNAUTHORIZED: 'Сессия истекла. Войдите заново.',
  FORBIDDEN: 'Недостаточно прав для этого действия.',
  NOT_FOUND: 'Запрошенные данные не найдены.',
  INTERNAL_SERVER_ERROR: 'На сервере произошла ошибка. Попробуйте ещё раз.',
  NETWORK_ERROR: 'Не удалось связаться с сервером. Проверьте подключение.',
  TIMEOUT: 'Сервер отвечает слишком долго. Попробуйте позже.',
  PIPELINE_FAILED: 'Обработка запроса завершилась с ошибкой. Попробуйте переформулировать.',
  UNKNOWN: 'Что-то пошло не так. Попробуйте ещё раз.',
}

/** A short, user-facing Russian description for any thrown error. */
export function humanizeError(e: unknown): string {
  if (e instanceof ApiError) return e.message || ERROR_MESSAGES[e.code]
  if (e instanceof Error && e.message) return ERROR_MESSAGES.UNKNOWN
  return ERROR_MESSAGES.UNKNOWN
}

async function toApiError(res: Response): Promise<ApiError> {
  let code: ApiErrorCode = 'UNKNOWN'
  let details: Record<string, unknown> | undefined
  try {
    const body = await res.json()
    const raw = body?.error?.code
    if (raw && raw in ERROR_MESSAGES) code = raw as ApiErrorCode
    details = body?.error?.details
  } catch {
    // Non-JSON error body — classify by HTTP status below.
  }
  if (code === 'UNKNOWN') {
    if (res.status === 401) code = 'UNAUTHORIZED'
    else if (res.status === 403) code = 'FORBIDDEN'
    else if (res.status === 404) code = 'NOT_FOUND'
    else if (res.status === 422) code = 'VALIDATION_ERROR'
    else if (res.status >= 500) code = 'INTERNAL_SERVER_ERROR'
  }
  return new ApiError(code, ERROR_MESSAGES[code], { status: res.status, details })
}

// ---------------------------------------------------------------------------
// Token storage

const ACCESS_KEY = 'hf.access_token'
const REFRESH_KEY = 'hf.refresh_token'
const USER_KEY = 'hf.username'

function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_KEY)
}

export function getStoredUser(): User | null {
  const username = localStorage.getItem(USER_KEY)
  return username && localStorage.getItem(REFRESH_KEY) ? { username } : null
}

export function clearAuthTokens(): void {
  localStorage.removeItem(ACCESS_KEY)
  localStorage.removeItem(REFRESH_KEY)
  localStorage.removeItem(USER_KEY)
}

// Broadcast for "refresh token is dead" — the auth provider subscribes and
// flips the app into the logged-out state without a reload.
type Listener = () => void
const expiredListeners = new Set<Listener>()

export function onAuthExpired(listener: Listener): () => void {
  expiredListeners.add(listener)
  return () => expiredListeners.delete(listener)
}

function emitAuthExpired(): void {
  clearAuthTokens()
  expiredListeners.forEach((l) => l())
}

// ---------------------------------------------------------------------------
// Core request machinery

let refreshInFlight: Promise<string> | null = null

/** POST /auth/refresh, deduplicated so parallel 401s trigger a single call. */
function refreshAccessToken(): Promise<string> {
  if (!refreshInFlight) {
    refreshInFlight = (async () => {
      const refreshToken = localStorage.getItem(REFRESH_KEY)
      if (!refreshToken) throw new ApiError('UNAUTHORIZED', ERROR_MESSAGES.UNAUTHORIZED)
      let res: Response
      try {
        res = await fetch(`${API_BASE}/auth/refresh`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refreshToken }),
        })
      } catch {
        throw new ApiError('NETWORK_ERROR', ERROR_MESSAGES.NETWORK_ERROR)
      }
      if (!res.ok) throw await toApiError(res)
      const data = await res.json()
      localStorage.setItem(ACCESS_KEY, data.access_token)
      return data.access_token as string
    })().finally(() => {
      refreshInFlight = null
    })
  }
  return refreshInFlight
}

interface RequestOptions {
  method?: string
  json?: unknown
  form?: FormData
  auth?: boolean
}

async function request(path: string, opts: RequestOptions = {}): Promise<Response> {
  const { method = 'GET', json, form, auth = true } = opts

  const doFetch = (token: string | null) => {
    const headers: Record<string, string> = {}
    if (auth && token) headers.Authorization = `Bearer ${token}`
    if (json !== undefined) headers['Content-Type'] = 'application/json'
    return fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: json !== undefined ? JSON.stringify(json) : form,
    })
  }

  let res: Response
  try {
    res = await doFetch(getAccessToken())
  } catch {
    throw new ApiError('NETWORK_ERROR', ERROR_MESSAGES.NETWORK_ERROR)
  }

  if (res.status === 401 && auth) {
    // Access token likely expired — refresh once and retry.
    let fresh: string
    try {
      fresh = await refreshAccessToken()
    } catch (e) {
      emitAuthExpired()
      throw e instanceof ApiError ? e : new ApiError('UNAUTHORIZED', ERROR_MESSAGES.UNAUTHORIZED)
    }
    try {
      res = await doFetch(fresh)
    } catch {
      throw new ApiError('NETWORK_ERROR', ERROR_MESSAGES.NETWORK_ERROR)
    }
    if (res.status === 401) {
      emitAuthExpired()
      throw await toApiError(res)
    }
  }

  if (!res.ok && res.status !== 202) throw await toApiError(res)
  return res
}

// ---------------------------------------------------------------------------
// Auth

export async function login(username: string, password: string): Promise<User> {
  const res = await request('/auth/login', {
    method: 'POST',
    json: { username, password },
    auth: false,
  })
  const data = await res.json()
  localStorage.setItem(ACCESS_KEY, data.access_token)
  localStorage.setItem(REFRESH_KEY, data.refresh_token)
  localStorage.setItem(USER_KEY, username)
  return { username }
}

export function logout(): void {
  clearAuthTokens()
}

// ---------------------------------------------------------------------------
// Wire formats

interface ApiSessionSummary {
  id: string
  title: string
  status: string
  created_at: string
  updated_at: string
}

interface ApiMessage {
  id: string
  role: 'user' | 'system'
  content: string
  iteration: number
  status: 'queued' | 'processing' | 'done' | 'failed'
  task_id: string
  created_at: string
}

interface ApiSessionDetail extends ApiSessionSummary {
  constraints: string
  weights: Weights
  messages: ApiMessage[]
  latest_result?: {
    message_id: string
    hypothesis?: ApiHypothesis
    review?: ApiReview
  } | null
}

interface ApiHypothesis {
  title?: string
  hypothesis?: string
  expected_effect?: string
  risks?: string[]
  feasibility_score?: number
  novelty_score?: number
  effect_score?: number
  risk_score?: number
  evidence_sources?: string[]
}

interface ApiReview {
  scores?: Partial<Record<'novelty' | 'feasibility' | 'effect' | 'risk', number>>
  verdict?: string
  suggestions?: string[]
}

function mapResult(hypothesis?: ApiHypothesis, review?: ApiReview): HypothesisResult {
  const h = hypothesis ?? {}
  const r = review ?? {}
  return {
    title: h.title ?? 'Гипотеза',
    hypothesis: h.hypothesis ?? '',
    expectedEffect: h.expected_effect ?? '',
    scores: {
      novelty: r.scores?.novelty ?? h.novelty_score ?? 0,
      feasibility: r.scores?.feasibility ?? h.feasibility_score ?? 0,
      effect: r.scores?.effect ?? h.effect_score ?? 0,
      risk: r.scores?.risk ?? h.risk_score ?? 0,
    },
    verdict: r.verdict === 'reject' ? 'reject' : 'accept',
    risks: h.risks ?? [],
    suggestions: r.suggestions ?? [],
    evidenceSources: h.evidence_sources ?? [],
  }
}

function mapMessage(m: ApiMessage): Message {
  if (m.role === 'user') {
    return { id: m.id, role: 'user', content: m.content, files: [] }
  }
  return {
    id: m.id,
    role: 'assistant',
    status: m.status === 'done' ? 'done' : m.status === 'failed' ? 'failed' : 'thinking',
    iteration: m.iteration,
    error: m.status === 'failed' ? ERROR_MESSAGES.PIPELINE_FAILED : undefined,
  }
}

// ---------------------------------------------------------------------------
// Sessions

export async function fetchSessions(): Promise<Session[]> {
  const res = await request('/sessions')
  const data = await res.json()
  const items: ApiSessionSummary[] = data.items ?? []
  return items.map((s) => ({
    id: s.id,
    title: s.title,
    createdAt: s.created_at,
    constraints: '',
    weights: DEFAULT_WEIGHTS,
    messages: [],
    loaded: false,
  }))
}

export async function fetchSessionDetail(sessionId: string): Promise<Session> {
  const res = await request(`/sessions/${sessionId}`)
  const d: ApiSessionDetail = await res.json()
  const messages = (d.messages ?? []).map(mapMessage)

  if (d.latest_result?.message_id) {
    const result = mapResult(d.latest_result.hypothesis, d.latest_result.review)
    for (const m of messages) {
      if (m.id === d.latest_result.message_id && m.role === 'assistant') {
        m.result = result
      }
    }
  }

  return {
    id: d.id,
    title: d.title,
    createdAt: d.created_at,
    constraints: d.constraints ?? '',
    weights: d.weights ?? DEFAULT_WEIGHTS,
    messages,
    loaded: true,
  }
}

export async function createSession(input: {
  title: string
  constraints: string
  weights: Weights
}): Promise<Session> {
  const res = await request('/sessions', { method: 'POST', json: input })
  const d: ApiSessionDetail = await res.json()
  return {
    id: d.id,
    title: d.title,
    createdAt: d.created_at,
    constraints: d.constraints ?? '',
    weights: d.weights ?? DEFAULT_WEIGHTS,
    messages: [],
    loaded: true,
  }
}

export async function deleteSession(sessionId: string): Promise<void> {
  await request(`/sessions/${sessionId}`, { method: 'DELETE' })
}

// ---------------------------------------------------------------------------
// Messages & results

export async function sendMessage(
  sessionId: string,
  content: string,
  files: File[],
): Promise<{ messageId: string; taskId: string }> {
  const form = new FormData()
  form.append('content', content)
  for (const file of files) form.append('files', file, file.name)
  const res = await request(`/sessions/${sessionId}/messages`, { method: 'POST', form })
  const data = await res.json()
  return { messageId: data.message_id, taskId: data.task_id }
}

export type ResultState =
  | { state: 'processing' }
  | { state: 'done'; result: HypothesisResult }
  | { state: 'failed' }

export async function fetchResult(sessionId: string, messageId: string): Promise<ResultState> {
  const res = await request(`/sessions/${sessionId}/results/${messageId}`)
  const data = await res.json()
  if (res.status === 202 || data.status === 'processing' || data.status === 'queued') {
    return { state: 'processing' }
  }
  if (data.status === 'failed') return { state: 'failed' }
  return { state: 'done', result: mapResult(data.hypothesis, data.review) }
}

const POLL_INTERVAL_MS = 2500
const POLL_TIMEOUT_MS = 10 * 60 * 1000

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

/** Poll the result endpoint until the pipeline finishes, fails or times out. */
export async function pollResult(
  sessionId: string,
  messageId: string,
): Promise<HypothesisResult> {
  const deadline = Date.now() + POLL_TIMEOUT_MS
  for (;;) {
    const r = await fetchResult(sessionId, messageId)
    if (r.state === 'done') return r.result
    if (r.state === 'failed') {
      throw new ApiError('PIPELINE_FAILED', ERROR_MESSAGES.PIPELINE_FAILED)
    }
    if (Date.now() > deadline) {
      throw new ApiError('TIMEOUT', ERROR_MESSAGES.TIMEOUT)
    }
    await delay(POLL_INTERVAL_MS)
  }
}
