import { useEffect, useRef } from 'react'
import type { Message } from '@/types'
import { useI18n } from '@/lib/i18n'
import { Spinner } from '@/components/ui/Spinner'
import { EmptyState } from './EmptyState'
import { UserMessage } from './UserMessage'
import { AssistantMessage } from './AssistantMessage'

interface Props {
  messages: Message[]
  loading?: boolean
  authenticated: boolean
  sessionId?: string
  onExampleSelect: (text: string) => void
  onLogin: () => void
}

export function ChatThread({
  messages,
  loading,
  authenticated,
  sessionId,
  onExampleSelect,
  onLogin,
}: Props) {
  const { t } = useI18n()
  const bottomRef = useRef<HTMLDivElement>(null)
  const last = messages[messages.length - 1]

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ block: 'end', behavior: 'smooth' })
  }, [messages.length, last])

  if (loading && messages.length === 0) {
    return (
      <div className="flex min-h-full items-center justify-center">
        <div className="flex animate-fade-in items-center gap-3 text-ink-faint">
          <Spinner className="h-5 w-5" />
          <span className="text-[14px]">{t('thread.loading')}</span>
        </div>
      </div>
    )
  }

  if (messages.length === 0) {
    return (
      <EmptyState
        authenticated={authenticated}
        onSelect={onExampleSelect}
        onLogin={onLogin}
      />
    )
  }

  return (
    <div className="mx-auto w-full max-w-3xl px-4 pb-8 pt-6 sm:px-6">
      <div className="flex flex-col gap-8">
        {messages.map((m) =>
          m.role === 'user' ? (
            <UserMessage key={m.id} content={m.content} files={m.files} />
          ) : (
            <AssistantMessage
              key={m.id}
              status={m.status}
              result={m.result}
              error={m.error}
              sessionId={sessionId}
              isLast={m === last}
            />
          ),
        )}
      </div>
      <div ref={bottomRef} className="h-1" />
    </div>
  )
}
