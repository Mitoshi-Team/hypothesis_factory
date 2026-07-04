import { CircleAlert, FlaskConical } from 'lucide-react'
import type { HypothesisResult as Result } from '@/types'
import { HypothesisResult } from './HypothesisResult'
import { ThinkingTrace } from './ThinkingTrace'
import { MessageActions } from './MessageActions'

interface Props {
  status: 'thinking' | 'done' | 'failed'
  result?: Result
  error?: string
}

export function AssistantMessage({ status, result, error }: Props) {
  return (
    <div className="flex gap-3">
      <span className="mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-lg bg-accent-50 text-accent-600">
        <FlaskConical className="h-4 w-4" strokeWidth={2} />
      </span>

      <div className="min-w-0 flex-1">
        {status === 'failed' ? (
          <div className="flex animate-fade-up items-start gap-2.5 rounded-2xl border border-red-100 bg-red-50/70 px-4 py-3.5">
            <CircleAlert className="mt-0.5 h-4 w-4 shrink-0 text-red-500" />
            <div className="min-w-0">
              <p className="text-[13.5px] font-medium text-red-600">Не удалось получить ответ</p>
              <p className="mt-0.5 text-[13px] leading-relaxed text-red-500/90">
                {error ?? 'Попробуйте отправить сообщение ещё раз.'}
              </p>
            </div>
          </div>
        ) : status === 'thinking' || !result ? (
          <ThinkingTrace />
        ) : (
          <div className="animate-fade-in">
            <HypothesisResult result={result} />
            <MessageActions result={result} />
          </div>
        )}
      </div>
    </div>
  )
}
