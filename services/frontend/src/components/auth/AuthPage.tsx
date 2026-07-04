import { useEffect, useRef, useState } from 'react'
import { ArrowLeft, Eye, EyeOff, History, Layers, Sparkles } from 'lucide-react'
import { cn } from '@/lib/cn'
import { useAuth } from '@/lib/auth'
import { humanizeError, ApiError } from '@/lib/api'
import { DEMO_PASSWORD, DEMO_USERNAME } from '@/lib/demo'
import { Spinner } from '@/components/ui/Spinner'

interface Props {
  /** True while `/auth` is the active route — drives the enter/exit transition. */
  active: boolean
  onClose: () => void
  onSuccess: () => void
}

type Mode = 'login' | 'register'

const PERKS = [
  { icon: History, text: 'История сессий всегда под рукой' },
  { icon: Layers, text: 'Итеративная работа над гипотезой' },
  { icon: Sparkles, text: 'Оценка по критериям и рискам' },
]

/**
 * Full-page auth screen shown on the `/auth` route. Always mounted so the swap
 * with the chat is a pure transition — no modal, no backdrop blur, no remounts.
 *
 * Layout is a split: a branded accent panel on the left and the form on the
 * right. The two halves slide in from opposite screen edges and meet in the
 * middle ("shutters closing" over the chat), then part again on exit.
 */
export function AuthPage({ active, onClose, onSuccess }: Props) {
  const { login, register } = useAuth()
  const [mode, setMode] = useState<Mode>('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [shaking, setShaking] = useState(false)
  const usernameRef = useRef<HTMLInputElement>(null)

  const isRegister = mode === 'register'

  useEffect(() => {
    if (!active) return
    setError(null)
    setPassword('')
    setConfirm('')
    setSubmitting(false)
    // Focus after the enter transition starts, so the ring doesn't flash.
    const t = setTimeout(() => usernameRef.current?.focus(), 400)
    return () => clearTimeout(t)
  }, [active])

  useEffect(() => {
    if (!active) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [active, onClose])

  const fail = (msg: string) => {
    setError(msg)
    setShaking(true)
    setSubmitting(false)
  }

  const enterDemo = async () => {
    if (submitting) return
    setSubmitting(true)
    setError(null)
    try {
      await login(DEMO_USERNAME, DEMO_PASSWORD)
      onSuccess()
    } catch (err) {
      fail(humanizeError(err))
    }
  }

  const switchMode = (next: Mode) => {
    setMode(next)
    setError(null)
    setConfirm('')
    usernameRef.current?.focus()
  }

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (submitting) return
    if (!username.trim() || !password) {
      fail('Введите логин и пароль.')
      return
    }
    if (isRegister && password !== confirm) {
      fail('Пароли не совпадают.')
      return
    }
    setSubmitting(true)
    setError(null)
    try {
      if (isRegister) await register(username, password)
      else await login(username, password)
      onSuccess()
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        fail('Неверный логин или пароль.')
      } else if (isRegister && err instanceof ApiError && err.status === 409) {
        fail('Такой логин уже занят.')
      } else {
        fail(humanizeError(err))
      }
    }
  }

  // Minimal fields — a quiet underline-style focus in ink, no accent ring.
  const inputClass =
    'w-full rounded-xl border border-line bg-panel px-3.5 py-2.5 text-[14px] text-ink placeholder:text-ink-faint transition-colors duration-200 focus:border-ink focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0'

  return (
    <div
      className={cn(
        // `visibility` transitions with a delay so it only flips to hidden
        // AFTER the panels finish sliding back out on close.
        'absolute inset-0 z-40 flex overflow-hidden transition-[visibility] duration-[650ms]',
        active ? 'visible' : 'invisible pointer-events-none',
      )}
      aria-hidden={!active}
      role="region"
      aria-label={isRegister ? 'Регистрация' : 'Авторизация'}
    >
      {/* ---- Left brand panel (desktop only) — slides in from the left ---- */}
      <aside
        className={cn(
          'relative hidden w-[44%] shrink-0 overflow-hidden text-white transition-transform duration-[650ms] ease-[cubic-bezier(0.22,1,0.36,1)] md:flex md:flex-col',
          active ? 'translate-x-0' : '-translate-x-full',
        )}
      >
        {/* Living gradient: an oversized multi-stop wash drifting diagonally,
            layered with a few slowly floating blurred glows. */}
        <div className="pointer-events-none absolute inset-0 animate-gradient bg-[length:220%_220%] bg-[linear-gradient(125deg,#3B78F5_0%,#1F57D6_34%,#1A47B4_58%,#2E6BF0_82%,#4C86F7_100%)]" />
        <div className="pointer-events-none absolute -left-28 -top-24 h-80 w-80 rounded-full bg-white/20 blur-3xl animate-float" />
        <div
          className="pointer-events-none absolute -bottom-32 right-[-12%] h-96 w-96 rounded-full bg-sky-300/25 blur-3xl animate-float"
          style={{ animationDelay: '2s' }}
        />
        <div
          className="pointer-events-none absolute left-1/4 top-1/2 h-72 w-72 rounded-full bg-white/10 blur-3xl animate-float"
          style={{ animationDelay: '4s' }}
        />

        <div className="relative z-10 flex h-full flex-col justify-center p-10 xl:p-14">
          <div
            className={cn('max-w-sm', active && 'animate-rise-in')}
            style={{ animationDelay: '250ms' }}
          >
            <h1 className="text-[32px] font-semibold leading-[1.12] tracking-tight xl:text-[38px]">
              Гипотезы,
              <br />
              подкреплённые данными
            </h1>
            <p className="mt-4 text-[14.5px] leading-relaxed text-white/75">
              Опишите технологическую задачу — получите гипотезу с обоснованием, ожидаемым
              эффектом и оценкой рисков.
            </p>

            <ul className="mt-9 flex flex-col gap-4">
              {PERKS.map((p) => (
                <li key={p.text} className="flex items-center gap-3 text-[14px] text-white/85">
                  <p.icon className="h-[18px] w-[18px] shrink-0 text-white/55" strokeWidth={2} />
                  {p.text}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </aside>

      {/* ---- Right form panel — slides in from the right ---- */}
      <div
        className={cn(
          'relative flex flex-1 items-center justify-center bg-panel px-5 py-10 transition-transform duration-[650ms] ease-[cubic-bezier(0.22,1,0.36,1)]',
          active ? 'translate-x-0' : 'translate-x-full',
        )}
      >
        <button
          type="button"
          onClick={onClose}
          className="absolute left-4 top-4 flex items-center gap-1.5 rounded-xl px-2.5 py-2 text-[13px] font-medium text-ink-soft transition-colors hover:bg-line/60 hover:text-ink"
        >
          <ArrowLeft className="h-4 w-4" />
          К чату
        </button>

        <div
          onAnimationEnd={(e) => {
            if (e.target === e.currentTarget) setShaking(false)
          }}
          className={cn(
            'w-full max-w-[360px]',
            active && 'animate-rise-in',
            shaking && active && 'animate-shake',
          )}
          style={{ animationDelay: shaking ? '0ms' : '180ms' }}
        >
          <h2 className="text-2xl font-semibold tracking-tight text-ink">
            {isRegister ? 'Создать аккаунт' : 'С возвращением'}
          </h2>
          <p className="mt-1.5 text-[13.5px] leading-relaxed text-ink-soft">
            {isRegister
              ? 'Придумайте логин и пароль, чтобы начать работу.'
              : 'Войдите, чтобы работать с чатом и историей сессий.'}
          </p>

          <form onSubmit={submit} className="mt-6 flex flex-col gap-3.5">
            <label className="flex flex-col gap-1.5">
              <span className="text-xs font-medium text-ink-soft">Логин</span>
              <input
                ref={usernameRef}
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
                placeholder="researcher_1"
                className={inputClass}
                disabled={submitting}
              />
            </label>

            <label className="flex flex-col gap-1.5">
              <span className="text-xs font-medium text-ink-soft">Пароль</span>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete={isRegister ? 'new-password' : 'current-password'}
                  placeholder="••••••••"
                  className={cn(inputClass, 'pr-11')}
                  disabled={submitting}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  tabIndex={-1}
                  className="absolute right-2 top-1/2 grid h-8 w-8 -translate-y-1/2 place-items-center rounded-lg text-ink-faint transition-colors hover:text-ink"
                  aria-label={showPassword ? 'Скрыть пароль' : 'Показать пароль'}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </label>

            {/* Confirm password — only for registration, revealed smoothly */}
            <div
              className={cn(
                'grid transition-[grid-template-rows] duration-300 ease-out',
                isRegister ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]',
              )}
            >
              <div className="min-h-0 overflow-hidden">
                <label className="flex flex-col gap-1.5 pt-px">
                  <span className="text-xs font-medium text-ink-soft">Повторите пароль</span>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={confirm}
                    onChange={(e) => setConfirm(e.target.value)}
                    autoComplete="new-password"
                    placeholder="••••••••"
                    className={inputClass}
                    disabled={submitting || !isRegister}
                    tabIndex={isRegister ? 0 : -1}
                  />
                </label>
              </div>
            </div>

            {/* Error — smooth height reveal */}
            <div
              className={cn(
                'grid transition-[grid-template-rows] duration-300 ease-out',
                error ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]',
              )}
            >
              <div className="min-h-0 overflow-hidden">
                <p className="rounded-xl border border-red-100 bg-red-50 px-3.5 py-2.5 text-[12.5px] leading-relaxed text-red-600">
                  {error}
                </p>
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className={cn(
                'mt-1 flex h-11 items-center justify-center gap-2 rounded-xl bg-ink text-[14px] font-medium text-white shadow-soft transition-all duration-200 ease-out',
                submitting ? 'cursor-default opacity-80' : 'hover:bg-ink/90 active:scale-[0.98]',
              )}
            >
              {submitting ? (
                <>
                  <Spinner className="h-4 w-4" />
                  <span>{isRegister ? 'Регистрируем…' : 'Входим…'}</span>
                </>
              ) : isRegister ? (
                'Зарегистрироваться'
              ) : (
                'Войти'
              )}
            </button>
          </form>

          {/* Switch between sign in / sign up */}
          <div className="mt-5 text-[13px] text-ink-soft">
            {isRegister ? 'Уже есть аккаунт? ' : 'Нет аккаунта? '}
            <button
              type="button"
              onClick={() => switchMode(isRegister ? 'login' : 'register')}
              className="font-medium text-ink underline-offset-2 transition-colors hover:underline"
            >
              {isRegister ? 'Войти' : 'Зарегистрироваться'}
            </button>
          </div>

          {/* Demo access — one click into a fully seeded, offline chat history */}
          <div className="mt-6 border-t border-line pt-5">
            <button
              type="button"
              onClick={enterDemo}
              disabled={submitting}
              className="flex w-full items-center justify-center gap-2 rounded-xl border border-line bg-card px-4 py-2.5 text-[13px] font-medium text-ink-soft transition-colors hover:border-line-strong hover:text-ink disabled:opacity-60"
            >
              <Sparkles className="h-4 w-4 text-ink-faint" strokeWidth={2} />
              Посмотреть демо без регистрации
            </button>
            <p className="mt-3 text-[12px] leading-relaxed text-ink-faint">
              Забыли логин или пароль? Обратитесь к администратору.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
