import { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { ArrowUp, SlidersHorizontal } from 'lucide-react'
import type { Weights } from '@/types'
import { cn } from '@/lib/cn'
import { ContextTray, type ContextValue } from './ContextTray'

export interface ComposerPayload {
  problem: string
  constraints: string
  weights: Weights
  files: File[]
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
  const [trayOpen, setTrayOpen] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const lastHeightRef = useRef<number | null>(null)

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
    const prev = lastHeightRef.current
    // Measure the natural content height.
    el.style.height = 'auto'
    const cs = getComputedStyle(el)
    const lineHeight = parseFloat(cs.lineHeight) || 24
    const maxHeight = lineHeight * 5 + parseFloat(cs.paddingTop) + parseFloat(cs.paddingBottom)
    const scrollH = el.scrollHeight
    const target = Math.min(scrollH, maxHeight)
    // Keep the caret line visible during the grow: only clip while it fits,
    // scroll once we hit the 5-line cap.
    el.style.overflowY = scrollH > maxHeight + 0.5 ? 'auto' : 'hidden'
    // Anchor the transition to the previously painted height, then let CSS
    // ease to the new one, so the box glides in a single smooth motion.
    if (prev != null && prev !== target) {
      el.style.height = `${prev}px`
      void el.offsetHeight
    }
    el.style.height = `${target}px`
    lastHeightRef.current = target
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
    <div className="overflow-hidden rounded-[26px] border border-line bg-card shadow-composer transition-[border-color,box-shadow] duration-300 ease-out focus-within:border-line-strong focus-within:shadow-pop">
      {/* Context tray — smooth height reveal */}
      <div
        className={cn(
          'grid transition-[grid-template-rows] duration-300 ease-out',
          trayOpen ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]',
        )}
      >
        <div className="min-h-0 overflow-hidden">
          <div
            className={cn(
              'transition-opacity duration-300 ease-out',
              trayOpen ? 'opacity-100' : 'opacity-0',
            )}
          >
            <ContextTray value={context} onChange={setContext} />
          </div>
        </div>
      </div>

      {/* Text input */}
      <textarea
        ref={textareaRef}
        value={problem}
        onChange={(e) => setProblem(e.target.value)}
        onKeyDown={onKeyDown}
        rows={1}
        placeholder="Опишите технологическую проблему…"
        aria-label="Технологическая проблема"
        className="scroll-slim block w-full resize-none bg-transparent px-4 pb-1 pt-3.5 text-[15px] leading-relaxed text-ink transition-[height] duration-[420ms] ease-[cubic-bezier(0.25,0.1,0.25,1)] placeholder:text-ink-faint focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0 will-change-[height]"
      />

      {/* Action bar */}
      <div className="flex items-center justify-between px-2.5 pb-2.5 pt-1">
        <button
          type="button"
          onClick={() => setTrayOpen((o) => !o)}
          aria-expanded={trayOpen}
          aria-label="Контекст: ограничения, веса и файлы"
          className={cn(
            'flex h-9 items-center gap-1.5 rounded-full pl-2.5 pr-3 text-[13px] font-medium transition-all duration-200 ease-out active:scale-[0.97]',
            trayOpen || contextCount > 0
              ? 'bg-accent-50 text-accent-600'
              : 'text-ink-soft hover:bg-panel',
          )}
        >
          <SlidersHorizontal
            className={cn(
              'h-[17px] w-[17px] transition-transform duration-300 ease-out',
              trayOpen && 'rotate-180',
            )}
          />
          <span>Контекст</span>
          <span
            className={cn(
              'grid place-items-center overflow-hidden rounded-full bg-accent-500 text-[11px] font-semibold tabular-nums text-white transition-all duration-200 ease-out',
              contextCount > 0 ? 'ml-0.5 h-5 min-w-5 px-1 opacity-100' : 'h-5 w-0 opacity-0',
            )}
          >
            {contextCount > 0 ? contextCount : ''}
          </span>
        </button>

        <button
          type="button"
          onClick={submit}
          disabled={!canSend}
          aria-label="Отправить"
          className={cn(
            'grid h-9 w-9 place-items-center rounded-full transition-all duration-200 ease-out active:scale-90',
            canSend
              ? 'bg-accent-500 text-white shadow-soft hover:scale-105 hover:bg-accent-600'
              : 'scale-95 bg-panel text-ink-faint',
          )}
        >
          <ArrowUp className="h-[18px] w-[18px]" strokeWidth={2.4} />
        </button>
      </div>
    </div>
  )
}
