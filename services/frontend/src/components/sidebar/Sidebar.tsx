import { LogIn, LogOut, Plus, RotateCw } from "lucide-react";
import type { Session, User } from "@/types";
import { cn } from "@/lib/cn";
import { relativeDay } from "@/lib/format";
import { LoginPrompt } from "@/components/auth/LoginPrompt";
import { Spinner } from "@/components/ui/Spinner";

interface SidebarProps {
  sessions: Session[];
  activeId: string | null;
  user: User | null;
  historyLoading: boolean;
  historyError: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onLogin: () => void;
  onLogout: () => void;
  onRetryHistory: () => void;
}

export function Sidebar({
  sessions,
  activeId,
  user,
  historyLoading,
  historyError,
  onSelect,
  onNew,
  onLogin,
  onLogout,
  onRetryHistory,
}: SidebarProps) {
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

        {!user ? (
          <LoginPrompt
            compact
            className="mx-0.5 mt-1"
            title="История недоступна"
            description="Для того чтобы иметь доступ к истории, необходимо войти или зарегистрироваться."
            onLogin={onLogin}
          />
        ) : historyLoading && sessions.length === 0 ? (
          <div className="flex animate-fade-in items-center gap-2.5 px-2.5 py-3 text-[13px] text-ink-faint">
            <Spinner className="h-4 w-4" />
            <span>Загружаем историю…</span>
          </div>
        ) : historyError ? (
          <div className="mx-0.5 mt-1 flex animate-fade-up flex-col gap-2 rounded-xl border border-red-100 bg-red-50/60 px-3 py-3">
            <p className="text-[12.5px] leading-relaxed text-red-600">{historyError}</p>
            <button
              type="button"
              onClick={onRetryHistory}
              className="inline-flex w-fit items-center gap-1.5 rounded-lg bg-card px-2.5 py-1.5 text-[12px] font-medium text-ink-soft shadow-soft transition-colors hover:text-ink"
            >
              <RotateCw className="h-3.5 w-3.5" />
              Повторить
            </button>
          </div>
        ) : sessions.length === 0 ? (
          <p className="animate-fade-in px-2.5 py-3 text-[12.5px] leading-relaxed text-ink-faint">
            Пока пусто — начните первый чат, и он появится здесь.
          </p>
        ) : (
          <ul className="flex flex-col gap-0.5">
            {sessions.map((s, i) => {
              const isActive = s.id === activeId;
              return (
                <li
                  key={s.id}
                  className="animate-fade-up"
                  style={{ animationDelay: `${Math.min(i, 8) * 30}ms` }}
                >
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
        )}
      </nav>

      <div className="p-3">
        {user ? (
          <div className="flex animate-fade-in items-center gap-2.5 px-1">
            <span className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-ink text-[11px] font-semibold uppercase text-white">
              {user.username.slice(0, 2)}
            </span>
            <span className="min-w-0 flex-1 truncate text-[13px] font-medium text-ink">
              {user.username}
            </span>
            <button
              type="button"
              onClick={onLogout}
              className="grid h-8 w-8 shrink-0 place-items-center rounded-lg text-ink-faint transition-colors duration-150 hover:bg-red-50 hover:text-red-500"
              aria-label="Выйти из аккаунта"
              title="Выйти"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        ) : (
          <button
            type="button"
            onClick={onLogin}
            className="flex w-full animate-fade-in items-center justify-start gap-2.5 rounded-xl px-2.5 py-2.5 text-[13.5px] font-medium text-ink-soft transition-all duration-200 ease-out hover:bg-line/60 hover:text-ink active:scale-[0.98]"
          >
            <LogIn className="h-4 w-4" strokeWidth={2.2} />
            Авторизация
          </button>
        )}
      </div>
    </div>
  );
}
