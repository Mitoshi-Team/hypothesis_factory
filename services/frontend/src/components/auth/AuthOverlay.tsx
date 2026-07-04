import { useEffect, useRef, useState } from 'react'
import { Eye, EyeOff, LockKeyhole, X } from 'lucide-react'
import { cn } from '@/lib/cn'
import { useAuth } from '@/lib/auth'
import { humanizeError, ApiError } from '@/lib/api'
import { Spinner } from '@/components/ui/Spinner'

interface Props {
  open: boolean
  onClose: () => void
  onSuccess: () => void
}

/**
 * Full-screen login layer rendered on the `/auth` route. Always mounted so
 * open/close is a pure CSS transition — no remounts, no page reloads.
 */
export function AuthOverlay({ open, onClose, onSuccess }: Props) {
  const { login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [shaking, setShaking] = useState(false)
  const usernameRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (!open) return
    setError(null)
    setPassword('')
    setSubmitting(false)
    // Focus after the enter transition starts, so the ring doesn't flash.
    const t = setTimeout(() => usernameRef.current?.focus(), 250)
    return () => clearTimeout(t)
  }, [open])

  useEffect(() => {
    if (!open) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open, onClose])

  const submit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (submitting) return
    if (!username.trim() || !password) {
      setError('Введите логин и пароль.')
      setShaking(true)
      return
    }
    setSubmitting(true)
    setError(null)
    try {
      await login(username, password)
      onSuccess()
    } catch (err) {
      const msg =
        err instanceof ApiError && err.status === 401
          ? 'Неверный логин или пароль.'
          : humanizeError(err)
      setError(msg)
      setShaking(true)
      setSubmitting(false)
    }
  }

  const inputClass =
    'w-full rounded-xl border border-line bg-panel px-3.5 py-2.5 text-[14px] text-ink placeholder:text-ink-faint transition-[border-color,box-shadow] duration-200 focus:border-accent-200 focus:outline-none focus:ring-2 focus:ring-accent-500/20'

  return (
    <div
      className={cn(
        'fixed inset-0 z-50 flex items-center justify-center p-4 transition-[visibility] duration-500',
        open ? 'visible' : 'invisible pointer-events-none',
      )}
      aria-hidden={!open}
      role="dialog"
      aria-modal="true"
      aria-label="Авторизация"
    >
      {/* Dim + blur the chat behind. The backdrop-filter itself is animated
          (blur 0 → 6px) so the glass effect glides in with the dim instead of
          popping when the layer becomes visible. */}
      <div
        className={cn(
          'absolute inset-0 transition-all duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]',
          open ? 'bg-ink/25 backdrop-blur-[6px]' : 'bg-transparent backdrop-blur-0',
        )}
        onClick={onClose}
      />

      <div
        onAnimationEnd={(e) => {
          if (e.target === e.currentTarget) setShaking(false)
        }}
        className={cn(
          'relative w-full max-w-[380px] rounded-3xl border border-line bg-card p-7 shadow-pop transition-all duration-500 ease-[cubic-bezier(0.22,1,0.36,1)]',
          open ? 'translate-y-0 scale-100 opacity-100' : 'translate-y-5 scale-[0.96] opacity-0',
          shaking && open && 'animate-shake',
        )}
      >
        <button
          type="button"
          onClick={onClose}
          className="absolute right-4 top-4 grid h-8 w-8 place-items-center rounded-lg text-ink-faint transition-colors hover:bg-panel hover:text-ink"
          aria-label="Закрыть"
        >
          <X className="h-4 w-4" />
        </button>

        <span className="grid h-11 w-11 place-items-center rounded-xl bg-accent-50 text-accent-600">
          <LockKeyhole className="h-5 w-5" strokeWidth={2} />
        </span>

        <h2 className="mt-4 text-xl font-semibold tracking-tight text-ink">Вход в аккаунт</h2>
        <p className="mt-1.5 text-[13.5px] leading-relaxed text-ink-soft">
          Войдите, чтобы работать с чатом и историей сессий. Аккаунты выдаёт администратор.
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
                autoComplete="current-password"
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
                <span>Входим…</span>
              </>
            ) : (
              'Войти'
            )}
          </button>
        </form>
      </div>
    </div>
  )
}
