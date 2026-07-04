import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { Check, ChevronRight, Globe, LogOut } from 'lucide-react'
import type { User } from '@/types'
import { cn } from '@/lib/cn'
import { useI18n } from '@/lib/i18n'
import { LANGS, LANG_META, type Lang } from '@/lib/lang'
import { DEMO_USERNAME } from '@/lib/demo'
import { Flag } from '@/components/ui/Flag'

interface Props {
  user: User
  onLogout: () => void
}

interface Coords {
  left: number
  bottom: number
  width: number
}

/**
 * Account control in the sidebar footer. Clicking the profile row opens a small
 * popover *upward* (like the ChatGPT account menu) with a language switcher —
 * whose flyout of flags appears to the right on hover — and a logout action that
 * asks for confirmation before signing out.
 *
 * The popover is rendered in a portal with fixed positioning so it floats above
 * everything and is never clipped by the sidebar's `overflow-hidden` panel.
 */
export function ProfileMenu({ user, onLogout }: Props) {
  const { t, lang, setLang } = useI18n()
  const [open, setOpen] = useState(false)
  const [confirming, setConfirming] = useState(false)
  const [langOpen, setLangOpen] = useState(false)
  const [coords, setCoords] = useState<Coords | null>(null)
  const triggerRef = useRef<HTMLButtonElement>(null)
  const popoverRef = useRef<HTMLDivElement>(null)

  const isDemo = user.username === DEMO_USERNAME

  const reposition = () => {
    const el = triggerRef.current
    if (!el) return
    const r = el.getBoundingClientRect()
    setCoords({ left: r.left, bottom: window.innerHeight - r.top + 8, width: r.width })
  }

  // Measure before paint so the popover appears in the right spot immediately.
  useLayoutEffect(() => {
    if (open) reposition()
  }, [open])

  // Close on outside click / Escape; keep position on scroll & resize.
  useEffect(() => {
    if (!open) return
    const onDown = (e: MouseEvent) => {
      const target = e.target as Node
      if (
        triggerRef.current?.contains(target) ||
        popoverRef.current?.contains(target)
      )
        return
      setOpen(false)
    }
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false)
    }
    const onScroll = () => reposition()
    window.addEventListener('mousedown', onDown)
    window.addEventListener('keydown', onKey)
    window.addEventListener('resize', onScroll)
    window.addEventListener('scroll', onScroll, true)
    return () => {
      window.removeEventListener('mousedown', onDown)
      window.removeEventListener('keydown', onKey)
      window.removeEventListener('resize', onScroll)
      window.removeEventListener('scroll', onScroll, true)
    }
  }, [open])

  // Reset transient sub-states whenever the menu closes.
  useEffect(() => {
    if (!open) {
      setConfirming(false)
      setLangOpen(false)
    }
  }, [open])

  const pick = (next: Lang) => {
    setLang(next)
    setLangOpen(false)
  }

  const avatar = (
    <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-ink text-[11px] font-semibold uppercase text-white">
      {user.username.slice(0, 2)}
    </span>
  )

  return (
    <>
      {/* ---- Popover (portaled so it floats above the sidebar) ---- */}
      {open &&
        coords &&
        createPortal(
          <div
            ref={popoverRef}
            role="menu"
            style={{ left: coords.left, bottom: coords.bottom, width: coords.width }}
            className="fixed z-[60] origin-bottom animate-fade-up rounded-2xl border border-line bg-card p-1.5 shadow-pop"
          >
            {confirming ? (
              /* Logout confirmation */
              <div className="p-2.5">
                <p className="text-[13.5px] font-semibold text-ink">{t('profile.logoutTitle')}</p>
                <p className="mt-1 text-[12.5px] leading-relaxed text-ink-soft">
                  {t('profile.logoutDesc')}
                </p>
                <div className="mt-3.5 flex gap-2">
                  <button
                    type="button"
                    onClick={() => setConfirming(false)}
                    className="flex-1 rounded-lg border border-line bg-panel px-3 py-2 text-[13px] font-medium text-ink-soft transition-colors hover:bg-line/60 hover:text-ink"
                  >
                    {t('profile.cancel')}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setOpen(false)
                      onLogout()
                    }}
                    className="flex-1 rounded-lg bg-red-500 px-3 py-2 text-[13px] font-medium text-white transition-colors hover:bg-red-600"
                  >
                    {t('profile.logout')}
                  </button>
                </div>
              </div>
            ) : (
              <>
                {/* Account header */}
                <div className="flex items-center gap-2.5 rounded-xl px-2 py-2">
                  {avatar}
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-[13.5px] font-medium text-ink">{user.username}</p>
                    <p className="truncate text-[11.5px] text-ink-faint">
                      {isDemo ? t('profile.demo') : t('profile.account')}
                    </p>
                  </div>
                </div>

                <div className="my-1 h-px bg-line" />

                {/* Language — flyout on hover, to the right */}
                <div
                  className="relative"
                  onMouseEnter={() => setLangOpen(true)}
                  onMouseLeave={() => setLangOpen(false)}
                >
                  <button
                    type="button"
                    onClick={() => setLangOpen((v) => !v)}
                    aria-haspopup="menu"
                    aria-expanded={langOpen}
                    className={cn(
                      'flex w-full items-center gap-2.5 rounded-xl px-2.5 py-2 text-left text-[13.5px] text-ink transition-colors',
                      langOpen ? 'bg-line/60' : 'hover:bg-line/60',
                    )}
                  >
                    <Globe className="h-[18px] w-[18px] shrink-0 text-ink-soft" strokeWidth={2} />
                    <span className="flex-1">{t('profile.language')}</span>
                    <Flag lang={lang} />
                    <ChevronRight className="h-4 w-4 shrink-0 text-ink-faint" />
                  </button>

                  {langOpen && (
                    // Padding bridge so the pointer can cross the gap without closing.
                    <div className="absolute bottom-0 left-full pl-1.5" role="menu">
                      <div className="w-44 animate-fade-in rounded-2xl border border-line bg-card p-1.5 shadow-pop">
                        {LANGS.map((code) => {
                          const activeLang = code === lang
                          return (
                            <button
                              key={code}
                              type="button"
                              onClick={() => pick(code)}
                              className={cn(
                                'flex w-full items-center gap-2.5 rounded-xl px-2.5 py-2 text-left text-[13.5px] transition-colors',
                                activeLang
                                  ? 'bg-accent-50 text-accent-700'
                                  : 'text-ink hover:bg-line/60',
                              )}
                            >
                              <Flag lang={code} />
                              <span className="flex-1">{LANG_META[code].native}</span>
                              {activeLang && (
                                <Check className="h-4 w-4 shrink-0 text-accent-600" strokeWidth={2.4} />
                              )}
                            </button>
                          )
                        })}
                      </div>
                    </div>
                  )}
                </div>

                {/* Logout */}
                <button
                  type="button"
                  onClick={() => setConfirming(true)}
                  className="flex w-full items-center gap-2.5 rounded-xl px-2.5 py-2 text-left text-[13.5px] text-ink transition-colors hover:bg-red-50 hover:text-red-600"
                >
                  <LogOut className="h-[18px] w-[18px] shrink-0" strokeWidth={2} />
                  <span className="flex-1">{t('profile.logout')}</span>
                </button>
              </>
            )}
          </div>,
          document.body,
        )}

      {/* ---- Trigger row ---- */}
      <button
        ref={triggerRef}
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label={t('profile.open')}
        className={cn(
          'flex w-full items-center gap-2.5 rounded-xl px-2 py-1.5 text-left transition-colors',
          open ? 'bg-line/60' : 'hover:bg-line/60',
        )}
      >
        {avatar}
        <span className="min-w-0 flex-1 truncate text-[13px] font-medium text-ink">
          {user.username}
        </span>
        <ChevronRight
          className={cn(
            'h-4 w-4 shrink-0 text-ink-faint transition-transform',
            open ? '-rotate-90' : 'rotate-0',
          )}
        />
      </button>
    </>
  )
}
