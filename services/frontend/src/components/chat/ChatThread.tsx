import { useEffect, useRef } from 'react'
import type { Message } from '@/types'
import { EmptyState } from './EmptyState'
import { UserMessage } from './UserMessage'
import { AssistantMessage } from './AssistantMessage'

interface Props {
  messages: Message[]
  onExampleSelect: (text: string) => void
}

export function ChatThread({ messages, onExampleSelect }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null)
  const last = messages[messages.length - 1]

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ block: 'end', behavior: 'smooth' })
  }, [messages.length, last])

  if (messages.length === 0) {
    return <EmptyState onSelect={onExampleSelect} />
  }

  return (
    <div className="mx-auto w-full max-w-3xl px-4 pb-8 pt-6 sm:px-6">
      <div className="flex flex-col gap-8">
        {messages.map((m) =>
          m.role === 'user' ? (
            <UserMessage key={m.id} content={m.content} files={m.files} />
          ) : (
            <AssistantMessage key={m.id} status={m.status} result={m.result} />
          ),
        )}
      </div>
      <div ref={bottomRef} className="h-1" />
    </div>
  )
}
