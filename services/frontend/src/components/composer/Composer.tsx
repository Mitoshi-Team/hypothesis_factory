import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { ArrowUp, SlidersHorizontal } from 'lucide-react'
import type { Weights } from '@/types'
import { cn } from '@/lib/cn'
import { ContextTray, type ContextValue } from './ContextTray'

export interface ComposerPayload {
  problem: string
  constraints: string
  weights: Weights
  files: string[]
}

interface Props {
  busy: boolean
  threadKey: string
  prefill: { text: string; nonce: number }
  initialWeights: Weights
  onSend: (payload: ComposerPayload) => void
}

export function Composer({ busy, threadKey, prefill, initialWeights, onSend }: Props) {
  const emptyContext = (): ContextValue => ({
    constraints: '',
    weights: initialWeights,
    files: [],
  })

  const [problem, setProblem] = useState('')
  const [context, setContext] = useState<ContextValue>(emptyContext)
  const [trayOpen, setTrayOpen] = useState(true)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    setProblem('')
    setContext(emptyContext())
    setTrayOpen(false)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [threadKey])

  useEffect(() => {
    if (prefill.nonce === 0) return
    setProblem(prefill.text)
    textareaRef.current?.focus()
  }, [prefill.nonce, prefill.text])

  useLayoutEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`
  }, [problem])

  const contextCount =
    (context.constraints.trim() ? 1 : 0) + context.files.length

  const canSend = problem.trim().length > 0 && !busy

  const submit = () => {
    if (!canSend) return
    onSend({
      problem,
      constraints: context.constraints,
      weights: context.weights,
      files: context.files,
    })
    setProblem('')
    setContext(emptyContext())
    setTrayOpen(false)
  }

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <div className="overflow-hidden rounded-3xl border border-line bg-card shadow-composer transition-shadow focus-within:border-line-strong">
      {trayOpen && <ContextTray value={context} onChange={setContext} />}

      <div className="flex items-end gap-2 p-2 pl-3">
        <textarea
          ref={textareaRef}
          value={problem}
          onChange={(e) => setProblem(e.target.value)}
          onKeyDown={onKeyDown}
          rows={1}
          placeholder="Опишите технологическую проблему…"
          aria-label="Технологическая проблема"
          className="max-h-[200px] min-h-[40px] flex-1 resize-none self-center bg-transparent py-2.5 text-[15px] leading-relaxed text-ink placeholder:text-ink-faint focus:outline-none scroll-slim"
        />
        <div className="flex items-center gap-1 pb-0.5">
          <button
            type="button"
            onClick={() => setTrayOpen((o) => !o)}
            aria-expanded={trayOpen}
            aria-label="Ограничения, веса и файлы"
            className={cn(
              'relative grid h-9 w-9 place-items-center rounded-full transition-colors',
              trayOpen || contextCount > 0
                ? 'bg-accent-50 text-accent-600'
                : 'text-ink-soft hover:bg-panel',
            )}
          >
            <SlidersHorizontal className="h-[18px] w-[18px]" />
            {contextCount > 0 && (
              <span className="absolute -right-0.5 -top-0.5 grid h-4 min-w-4 place-items-center rounded-full bg-accent-500 px-1 text-[10px] font-semibold text-white">
                {contextCount}
              </span>
            )}
          </button>
          <button
            type="button"
            onClick={submit}
            disabled={!canSend}
            aria-label="Отправить"
            className={cn(
              'grid h-9 w-9 place-items-center rounded-full transition-colors',
              canSend
                ? 'bg-accent-500 text-white hover:bg-accent-600'
                : 'bg-panel text-ink-faint',
            )}
          >
            <ArrowUp className="h-[18px] w-[18px]" strokeWidth={2.4} />
          </button>
        </div>
      </div>
    </div>
  )
}
