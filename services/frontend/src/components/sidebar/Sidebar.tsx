import { LogIn, Plus, RotateCw, Trash2 } from "lucide-react";
import type { Session, User } from "@/types";
import { cn } from "@/lib/cn";
import { relativeDay } from "@/lib/format";
import { useI18n } from "@/lib/i18n";
import { LoginPrompt } from "@/components/auth/LoginPrompt";
import { Spinner } from "@/components/ui/Spinner";
import { ProfileMenu } from "@/components/sidebar/ProfileMenu";

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
  onDelete?: (id: string) => void;
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
  onDelete,
}: SidebarProps) {
  const { t } = useI18n();
  return (
    <div className="flex h-full flex-col">
      <div className="flex h-14 items-center px-3">
        <button
          type="button"
          onClick={onNew}
          className="grid h-9 w-9 place-items-center rounded-xl text-ink-soft glass-btn hover:text-ink"
          aria-label={t("sidebar.newChat")}
        >
          <Plus className="h-[18px] w-[18px]" strokeWidth={2.2} />
        </button>
      </div>

      <nav className="min-h-0 flex-1 overflow-y-auto scroll-slim px-2 py-2">
        <p className="px-2 pb-1.5 pt-1 text-xs font-medium text-ink-faint">
          {t("sidebar.prevChats")}
        </p>

        {!user ? (
          <LoginPrompt
            compact
            className="mx-0.5 mt-1"
            title={t("sidebar.historyUnavailable")}
            description={t("sidebar.historyUnavailableDesc")}
            onLogin={onLogin}
          />
        ) : historyLoading && sessions.length === 0 ? (
          <div className="flex animate-fade-in items-center gap-2.5 px-2.5 py-3 text-[13px] text-ink-faint">
            <Spinner className="h-4 w-4" />
            <span>{t("sidebar.loadingHistory")}</span>
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
              {t("sidebar.retry")}
            </button>
          </div>
        ) : sessions.length === 0 ? (
          <p className="animate-fade-in px-2.5 py-3 text-[12.5px] leading-relaxed text-ink-faint">
            {t("sidebar.empty")}
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
                      "group flex w-full items-center gap-1.5 rounded-lg px-2.5 py-2 text-left transition-colors",
                      isActive ? "bg-accent-50" : "hover:bg-line/60",
                    )}
                  >
                    <span className="flex min-w-0 flex-1 flex-col items-start gap-0.5">
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
                    </span>
                    {onDelete && (
                      <span
                        role="button"
                        tabIndex={0}
                        onClick={(e) => {
                          e.stopPropagation();
                          onDelete(s.id);
                        }}
                        onKeyDown={(e) => {
                          if (e.key === "Enter" || e.key === " ") {
                            e.stopPropagation();
                            onDelete(s.id);
                          }
                        }}
                        className="rounded-md p-1 text-ink-faint opacity-0 transition-opacity hover:bg-red-100 hover:text-red-600 group-hover:opacity-100"
                        aria-label={t("sidebar.deleteChat")}
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </span>
                    )}
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </nav>

      <div className="p-3">
        {user ? (
          <div className="animate-fade-in">
            <ProfileMenu user={user} onLogout={onLogout} />
          </div>
        ) : (
          <button
            type="button"
            onClick={onLogin}
            className="flex w-full animate-fade-in items-center justify-start gap-2.5 rounded-xl px-2.5 py-2.5 text-[13.5px] font-medium text-ink-soft transition-all duration-200 ease-out hover:bg-line/60 hover:text-ink active:scale-[0.98]"
          >
            <LogIn className="h-4 w-4" strokeWidth={2.2} />
            {t("sidebar.auth")}
          </button>
        )}
      </div>
    </div>
  );
}
