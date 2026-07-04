import { useState, type ReactNode } from 'react'
import { Menu, X } from 'lucide-react'
import { cn } from '@/lib/cn'
import { BrandMark } from '@/components/sidebar/BrandMark'

interface ChatShellProps {
  sidebar: ReactNode
  composer: ReactNode
  children: ReactNode
}

export function ChatShell({ sidebar, composer, children }: ChatShellProps) {
  const [drawerOpen, setDrawerOpen] = useState(false)

  return (
    <div className="flex h-[100dvh] overflow-hidden bg-bg text-ink">
      <aside className="hidden w-[264px] shrink-0 border-r border-line bg-panel md:block">
        {sidebar}
      </aside>

      {/* Mobile drawer */}
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
            'absolute inset-y-0 left-0 w-[84%] max-w-[300px] border-r border-line bg-panel shadow-pop transition-transform duration-200 ease-out',
            drawerOpen ? 'translate-x-0' : '-translate-x-full',
          )}
          onClick={() => setDrawerOpen(false)}
        >
          {sidebar}
        </div>
      </div>

      <div className="relative flex min-w-0 flex-1 flex-col">
        {/* Mobile top bar */}
        <div className="flex h-14 shrink-0 items-center gap-2 border-b border-line bg-bg/90 px-3 backdrop-blur md:hidden">
          <button
            type="button"
            onClick={() => setDrawerOpen(true)}
            className="rounded-lg p-2 text-ink-soft hover:bg-panel"
            aria-label="Меню"
          >
            {drawerOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
          <BrandMark />
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto scroll-slim">{children}</div>

        <div className="shrink-0 px-3 pb-4 pt-1 md:px-6 md:pb-6">
          <div className="mx-auto w-full max-w-3xl">
            {composer}
          </div>
        </div>
      </div>
    </div>
  )
}
