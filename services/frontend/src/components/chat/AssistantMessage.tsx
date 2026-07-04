import { FlaskConical } from 'lucide-react'
import type { HypothesisResult as Result } from '@/types'
import { HypothesisResult } from './HypothesisResult'
import { ThinkingTrace } from './ThinkingTrace'
import { MessageActions } from './MessageActions'

interface Props {
  status: 'thinking' | 'done'
  result?: Result
}

export function AssistantMessage({ status, result }: Props) {
  return (
    <div className="flex gap-3">
      <span className="mt-0.5 grid h-7 w-7 shrink-0 place-items-center rounded-lg bg-accent-50 text-accent-600">
        <FlaskConical className="h-4 w-4" strokeWidth={2} />
      </span>

      <div className="min-w-0 flex-1">
        {status === 'thinking' || !result ? (
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
