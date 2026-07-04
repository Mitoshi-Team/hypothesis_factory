import { Plus } from 'lucide-react'
import type { Session } from '@/types'
import { cn } from '@/lib/cn'
import { relativeDay } from '@/lib/format'
import { BrandMark } from './BrandMark'

interface SidebarProps {
  sessions: Session[]
  activeId: string | null
  onSelect: (id: string) => void
  onNew: () => void
}

export function Sidebar({ sessions, activeId, onSelect, onNew }: SidebarProps) {
  return (
    <div className="flex h-full flex-col">
      <div className="flex h-14 items-center px-4">
        <BrandMark />
      </div>

      <div className="px-3 pb-2">
        <button
          type="button"
          onClick={onNew}
          className="flex w-full items-center gap-2 rounded-lg border border-line bg-card px-3 py-2 text-sm font-medium text-ink shadow-soft transition-colors hover:bg-accent-50 hover:border-accent-200"
        >
          <Plus className="h-4 w-4 text-accent-600" strokeWidth={2.2} />
          Новый разбор
        </button>
      </div>

      <nav className="min-h-0 flex-1 overflow-y-auto scroll-slim px-2 py-2">
        <p className="px-2 pb-1.5 pt-1 text-xs font-medium text-ink-faint">Недавние</p>
        <ul className="flex flex-col gap-0.5">
          {sessions.map((s) => {
            const isActive = s.id === activeId
            return (
              <li key={s.id}>
                <button
                  type="button"
                  onClick={() => onSelect(s.id)}
                  className={cn(
                    'flex w-full flex-col items-start gap-0.5 rounded-lg px-2.5 py-2 text-left transition-colors',
                    isActive ? 'bg-accent-50' : 'hover:bg-line/60',
                  )}
                >
                  <span
                    className={cn(
                      'w-full truncate text-[13px] leading-snug',
                      isActive ? 'font-medium text-accent-700' : 'text-ink',
                    )}
                  >
                    {s.title}
                  </span>
                  <span className="text-[11px] text-ink-faint">{relativeDay(s.createdAt)}</span>
                </button>
              </li>
            )
          })}
        </ul>
      </nav>

      <div className="border-t border-line p-3">
        <div className="flex items-center gap-2.5 px-1">
          <span className="grid h-7 w-7 place-items-center rounded-full bg-ink text-[11px] font-semibold text-white">
            ЛС
          </span>
          <span className="truncate text-[13px] text-ink-soft">Лаборатория сплавов</span>
        </div>
      </div>
    </div>
  )
}
