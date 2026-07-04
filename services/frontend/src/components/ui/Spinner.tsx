import { cn } from '@/lib/cn'
import { useI18n } from '@/lib/i18n'

export function Spinner({ className }: { className?: string }) {
  const { t } = useI18n()
  return (
    <span
      className={cn(
        'inline-block h-5 w-5 animate-spin rounded-full border-2 border-current border-t-transparent',
        className,
      )}
      role="status"
      aria-label={t('common.loading')}
    />
  )
}
