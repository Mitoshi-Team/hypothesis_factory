import { LoginPrompt } from '@/components/auth/LoginPrompt'
import { useI18n } from '@/lib/i18n'
import { EXAMPLES } from '@/lib/lang'

interface Props {
  authenticated: boolean
  onSelect: (text: string) => void
  onLogin: () => void
}

export function EmptyState({ authenticated, onSelect, onLogin }: Props) {
  const { t, lang } = useI18n()
  return (
    <div className="mx-auto flex min-h-full w-full max-w-2xl flex-col justify-start px-4 pb-12 pt-[14vh]">
      <div className="animate-fade-up" key={authenticated ? 'hero-auth' : 'hero-guest'}>
        <h1 className="text-2xl font-semibold tracking-tight text-ink">
          {t('empty.title')}
        </h1>
        <p className="mt-2 max-w-lg text-[15px] leading-relaxed text-ink-soft">
          {t('empty.desc')}
        </p>
      </div>

      {authenticated ? (
        <div
          key="examples"
          className="mt-7 flex flex-col gap-2 animate-fade-up"
          style={{ animationDelay: '80ms' }}
        >
          {EXAMPLES[lang].map((ex) => (
            <button
              key={ex}
              type="button"
              onClick={() => onSelect(ex)}
              className="rounded-xl border border-line bg-card px-4 py-3 text-left text-[14px] text-ink-soft transition-colors hover:border-accent-200 hover:bg-accent-50 hover:text-ink"
            >
              {ex}
            </button>
          ))}
        </div>
      ) : (
        <LoginPrompt
          className="mt-7"
          style={{ animationDelay: '80ms' }}
          title={t('empty.loginTitle')}
          description={t('empty.loginDesc')}
          actionLabel={t('empty.loginAction')}
          onLogin={onLogin}
        />
      )}
    </div>
  )
}
