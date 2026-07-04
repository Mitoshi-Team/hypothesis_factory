import { useEffect, useRef, useState } from 'react'
import { ArrowLeft, Eye, EyeOff, LockKeyhole, UserPlus } from 'lucide-react'
import { cn } from '@/lib/cn'
import { useAuth } from '@/lib/auth'
import { humanizeError, ApiError } from '@/lib/api'
import { Spinner } from '@/components/ui/Spinner'

interface Props {
  /** True while `/auth` is the active route — drives the enter/exit transition. */
  active: boolean
  onClose: () => void
  onSuccess: () => void
}

type Mode = 'login' | 'register'

/**
 * Full-page auth screen shown on the `/auth` route. Always mounted so the
 * swap with the chat is a pure cross-fade — the chat recedes, this glides in,
 * no modal, no backdrop blur, no remounts.
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
    const t = setTimeout(() => usernameRef.current?.focus(), 250)
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

  const inputClass =
    'w-full rounded-xl border border-line bg-panel px-3.5 py-2.5 text-[14px] text-ink placeholder:text-ink-faint transition-[border-color,box-shadow] duration-200 focus:border-accent-200 focus:outline-none focus:ring-2 focus:ring-accent-500/20'

  return (
    <div
      className={cn(
        'absolute inset-0 z-40 flex items-center justify-center overflow-y-auto bg-bg p-4 transition-all duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]',
        active
          ? 'visible translate-y-0 scale-100 opacity-100'
          : 'invisible pointer-events-none translate-y-3 scale-[0.98] opacity-0',
      )}
      aria-hidden={!active}
      role="region"
      aria-label={isRegister ? 'Регистрация' : 'Авторизация'}
    >
      <button
        type="button"
        onClick={onClose}
        className="absolute left-4 top-4 flex items-center gap-1.5 rounded-xl px-2.5 py-2 text-[13px] font-medium text-ink-soft transition-colors hover:bg-panel hover:text-ink"
      >
        <ArrowLeft className="h-4 w-4" />
        К чату
      </button>

      <div
        onAnimationEnd={(e) => {
          if (e.target === e.currentTarget) setShaking(false)
        }}
        className={cn(
          'w-full max-w-[400px] rounded-3xl border border-line bg-card p-7 shadow-pop',
          shaking && active && 'animate-shake',
        )}
      >
        <span className="grid h-11 w-11 place-items-center rounded-xl bg-accent-50 text-accent-600">
          {isRegister ? (
            <UserPlus className="h-5 w-5" strokeWidth={2} />
          ) : (
            <LockKeyhole className="h-5 w-5" strokeWidth={2} />
          )}
        </span>

        <h2 className="mt-4 text-xl font-semibold tracking-tight text-ink">
          {isRegister ? 'Создать аккаунт' : 'Вход в аккаунт'}
        </h2>
        <p className="mt-1.5 text-[13.5px] leading-relaxed text-ink-soft">
          {isRegister
            ? 'Придумайте логин и пароль, чтобы работать с чатом и историей сессий.'
            : 'Войдите, чтобы работать с чатом и историей сессий.'}
        </p>

        <form onSubmit={submit} className="mt-5 flex flex-col gap-3">
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
              'mt-1 flex h-11 items-center justify-center gap-2 rounded-xl bg-accent-500 text-[14px] font-medium text-white shadow-soft transition-all duration-200 ease-out',
              submitting
                ? 'cursor-default opacity-80'
                : 'hover:bg-accent-600 active:scale-[0.98]',
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
        <div className="mt-4 text-center text-[13px] text-ink-soft">
          {isRegister ? 'Уже есть аккаунт? ' : 'Нет аккаунта? '}
          <button
            type="button"
            onClick={() => switchMode(isRegister ? 'login' : 'register')}
            className="font-medium text-accent-600 transition-colors hover:text-accent-700"
          >
            {isRegister ? 'Войти' : 'Зарегистрироваться'}
          </button>
        </div>

        <p className="mt-4 border-t border-line pt-4 text-center text-[12px] leading-relaxed text-ink-faint">
          Забыли логин или пароль? Обратитесь к администратору.
        </p>
      </div>
    </div>
  )
}
