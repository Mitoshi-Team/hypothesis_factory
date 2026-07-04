import { LogIn } from 'lucide-react'
import { cn } from '@/lib/cn'

interface Props {
  title: string
  description: string
  actionLabel?: string
  compact?: boolean
  className?: string
  onLogin: () => void
}

/** Reusable "sign in to continue" card for locked areas of the UI. */
export function LoginPrompt({
  title,
  description,
  actionLabel = 'Войти',
  compact = false,
  className,
  onLogin,
}: Props) {
  return (
    <div
      className={cn(
        'flex animate-fade-up flex-col items-start rounded-2xl border border-line bg-card',
        compact ? 'gap-2 px-3.5 py-4' : 'gap-2.5 px-5 py-5',
        className,
      )}
    >
      <span
        className={cn(
          'grid place-items-center rounded-xl bg-accent-50 text-accent-600',
          compact ? 'h-8 w-8' : 'h-10 w-10',
        )}
      >
        <LogIn className={compact ? 'h-4 w-4' : 'h-5 w-5'} strokeWidth={2} />
      </span>
      <p className={cn('font-medium text-ink', compact ? 'text-[13px]' : 'text-[15px]')}>
        {title}
      </p>
      <p
        className={cn(
          'leading-relaxed text-ink-soft',
          compact ? 'text-[12px]' : 'text-[13.5px]',
        )}
      >
        {description}
      </p>
      <button
        type="button"
        onClick={onLogin}
        className={cn(
          'mt-1 rounded-xl bg-accent-500 font-medium text-white shadow-soft transition-all duration-200 ease-out hover:bg-accent-600 active:scale-[0.97]',
          compact ? 'px-3.5 py-2 text-[12.5px]' : 'px-4 py-2.5 text-[13.5px]',
        )}
      >
        {actionLabel}
      </button>
    </div>
  )
}
