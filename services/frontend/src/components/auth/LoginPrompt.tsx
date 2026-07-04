import type { CSSProperties } from 'react'
import { cn } from '@/lib/cn'
import { useI18n } from '@/lib/i18n'

interface Props {
  title: string
  description: string
  actionLabel?: string
  compact?: boolean
  className?: string
  style?: CSSProperties
  onLogin: () => void
}

/**
 * Reusable "sign in to continue" card for locked areas of the UI. One shared
 * look — title, description, single primary button — scaled down via `compact`
 * for the sidebar. No decorative icon badges.
 */
export function LoginPrompt({
  title,
  description,
  actionLabel,
  compact = false,
  className,
  style,
  onLogin,
}: Props) {
  const { t } = useI18n()
  return (
    <div
      style={style}
      className={cn(
        'flex animate-fade-up flex-col items-start rounded-2xl border border-line bg-card',
        compact ? 'gap-2 px-4 py-4' : 'gap-2.5 px-5 py-5',
        className,
      )}
    >
      <p
        className={cn(
          'font-semibold tracking-tight text-ink',
          compact ? 'text-[14px]' : 'text-[16px]',
        )}
      >
        {title}
      </p>
      <p
        className={cn(
          'leading-relaxed text-ink-soft',
          compact ? 'text-[12.5px]' : 'text-[13.5px]',
        )}
      >
        {description}
      </p>
      <button
        type="button"
        onClick={onLogin}
        className={cn(
          'mt-1.5 rounded-xl bg-accent-500 font-medium text-white shadow-soft transition-all duration-200 ease-out hover:bg-accent-600 active:scale-[0.97]',
          compact ? 'px-4 py-2 text-[12.5px]' : 'px-4 py-2.5 text-[13.5px]',
        )}
      >
        {actionLabel ?? t('common.signIn')}
      </button>
    </div>
  )
}
