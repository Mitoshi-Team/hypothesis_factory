import { useState, type ReactNode } from 'react'
import { PanelLeftClose, PanelLeftOpen } from 'lucide-react'
import { cn } from '@/lib/cn'
import { useI18n } from '@/lib/i18n'

interface ChatShellProps {
  sidebar: ReactNode
  composer: ReactNode
  children: ReactNode
}

export function ChatShell({ sidebar, composer, children }: ChatShellProps) {
  const { t } = useI18n()
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <div className="flex h-[100dvh] overflow-hidden bg-bg text-ink">
      {/* Desktop floating sidebar */}
      <div
        className={cn(
          'relative hidden shrink-0 overflow-hidden transition-[width] duration-300 ease-out md:block',
          sidebarOpen ? 'w-[288px]' : 'w-0',
        )}
      >
        <aside
          className={cn(
            'absolute inset-y-0 left-0 w-[288px] p-3 pr-0 transition-transform duration-300 ease-out',
            sidebarOpen ? 'translate-x-0' : '-translate-x-full',
          )}
        >
          <div className="relative flex h-full flex-col overflow-hidden rounded-2xl border border-line bg-panel shadow-pop">
            <button
              type="button"
              onClick={() => setSidebarOpen(false)}
              className="absolute right-3 top-2.5 z-10 grid h-9 w-9 place-items-center rounded-xl text-ink-soft glass-btn hover:text-ink"
              aria-label={t("sidebar.hideMenu")}
            >
              <PanelLeftClose className="h-[18px] w-[18px]" />
            </button>
            {sidebar}
          </div>
        </aside>
      </div>

      {/* Mobile drawer — fullscreen floating panel */}
      <div
        className={cn('fixed inset-0 z-40 md:hidden', !drawerOpen && 'pointer-events-none')}
        aria-hidden={!drawerOpen}
      >
        <div
          className={cn(
            'absolute inset-0 bg-ink/20 transition-opacity duration-200',
            drawerOpen ? 'opacity-100' : 'opacity-0',
          )}
          onClick={() => setDrawerOpen(false)}
        />
        <div
          className={cn(
            'absolute inset-0 transform-gpu p-3 transition-transform duration-300 ease-out will-change-transform',
            drawerOpen ? 'translate-x-0' : '-translate-x-full',
          )}
        >
          <div
            className="relative flex h-full flex-col overflow-hidden rounded-2xl border border-line bg-panel shadow-pop"
            onClick={() => setDrawerOpen(false)}
          >
            <button
              type="button"
              onClick={() => setDrawerOpen(false)}
              className="absolute right-3 top-2.5 z-10 grid h-9 w-9 place-items-center rounded-xl text-ink-soft glass-btn hover:text-ink"
              aria-label={t("sidebar.hideMenu")}
            >
              <PanelLeftClose className="h-[18px] w-[18px]" />
            </button>
            {sidebar}
          </div>
        </div>
      </div>

      <div className="min-w-0 flex-1 p-3">
        {/* Floating chat panel — a detached island, matching the sidebar */}
        <div className="relative flex h-full min-h-0 flex-col overflow-hidden rounded-2xl border border-line bg-panel shadow-pop">
          {/* Desktop reopen button */}
          <button
            type="button"
            onClick={() => setSidebarOpen(true)}
            className={cn(
              'absolute left-3 top-3 z-20 hidden h-9 w-9 place-items-center rounded-xl text-ink-soft glass-btn transition-all duration-300 hover:text-ink md:grid',
              sidebarOpen
                ? 'pointer-events-none -translate-x-3 opacity-0'
                : 'translate-x-0 opacity-100',
            )}
            aria-label={t("sidebar.showMenu")}
          >
            <PanelLeftOpen className="h-[18px] w-[18px]" />
          </button>

          {/* Mobile open button */}
          <button
            type="button"
            onClick={() => setDrawerOpen(true)}
            className="absolute left-3 top-3 z-20 grid h-9 w-9 place-items-center rounded-xl text-ink-soft glass-btn hover:text-ink md:hidden"
            aria-label={t("sidebar.showMenu")}
          >
            <PanelLeftOpen className="h-[18px] w-[18px]" />
          </button>

          <div className="min-h-0 flex-1 overflow-y-auto scroll-slim">{children}</div>

          <div className="shrink-0 px-3 pb-4 pt-1 md:px-6 md:pb-6">
            <div className="mx-auto w-full max-w-3xl">
              {composer}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
