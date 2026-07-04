import { Plus } from "lucide-react";
import type { Session } from "@/types";
import { cn } from "@/lib/cn";
import { relativeDay } from "@/lib/format";

interface SidebarProps {
  sessions: Session[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
}

export function Sidebar({ sessions, activeId, onSelect, onNew }: SidebarProps) {
  return (
    <div className="flex h-full flex-col">
      <div className="flex h-14 items-center px-3">
        <button
          type="button"
          onClick={onNew}
          className="grid h-9 w-9 place-items-center rounded-xl text-ink-soft glass-btn hover:text-ink"
          aria-label="Новый чат"
        >
          <Plus className="h-[18px] w-[18px]" strokeWidth={2.2} />
        </button>
      </div>

      <nav className="min-h-0 flex-1 overflow-y-auto scroll-slim px-2 py-2">
        <p className="px-2 pb-1.5 pt-1 text-xs font-medium text-ink-faint">
          Предыдущие чаты
        </p>
        <ul className="flex flex-col gap-0.5">
          {sessions.map((s) => {
            const isActive = s.id === activeId;
            return (
              <li key={s.id}>
                <button
                  type="button"
                  onClick={() => onSelect(s.id)}
                  className={cn(
                    "flex w-full flex-col items-start gap-0.5 rounded-lg px-2.5 py-2 text-left transition-colors",
                    isActive ? "bg-accent-50" : "hover:bg-line/60",
                  )}
                >
                  <span
                    className={cn(
                      "w-full truncate text-[13px] leading-snug",
                      isActive ? "font-medium text-accent-700" : "text-ink",
                    )}
                  >
                    {s.title}
                  </span>
                  <span className="text-[11px] text-ink-faint">
                    {relativeDay(s.createdAt)}
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="border-t border-line p-3">
        <div className="flex items-center gap-2.5 px-1">
          <span className="grid h-7 w-7 place-items-center rounded-full bg-ink text-[11px] font-semibold text-white">
            67
          </span>
          <span className="truncate text-[13px] text-ink-soft">
            потом тут будет профиль
          </span>
        </div>
      </div>
    </div>
  );
}
