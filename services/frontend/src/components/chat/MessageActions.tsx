import { useState, type ReactNode } from 'react'
import { Check, Copy, Download } from 'lucide-react'
import type { HypothesisResult } from '@/types'
import { cn } from '@/lib/cn'
import { CRITERIA_LABELS, verdictLabel } from '@/lib/format'
import { SaveModal } from './SaveModal'

function resultToText(r: HypothesisResult): string {
  const scores = (Object.keys(CRITERIA_LABELS) as Array<keyof typeof r.scores>)
    .map((k) => `${CRITERIA_LABELS[k]} ${r.scores[k].toFixed(1)}`)
    .join(' · ')
  const lines = [
    r.title,
    `${scores} · ${verdictLabel(r.verdict)}`,
    '',
    `Гипотеза: ${r.hypothesis}`,
    `Ожидаемый эффект: ${r.expectedEffect}`,
    '',
    'Риски:',
    ...r.risks.map((x) => `— ${x}`),
  ]
  if (r.suggestions.length) {
    lines.push('', 'Что проверить дальше:', ...r.suggestions.map((x) => `— ${x}`))
  }
  return lines.join('\n')
}

export function MessageActions({ result }: { result: HypothesisResult }) {
  const [copied, setCopied] = useState(false)
  const [saveOpen, setSaveOpen] = useState(false)

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(resultToText(result))
      setCopied(true)
      setTimeout(() => setCopied(false), 1600)
    } catch {
      /* clipboard unavailable */
    }
  }

  return (
    <>
      <div className="mt-2 flex items-center gap-0.5">
        <ActionButton onClick={copy}>
          {copied ? (
            <Check className="h-3.5 w-3.5 text-accent-600" />
          ) : (
            <Copy className="h-3.5 w-3.5" />
          )}
          {copied ? 'Скопировано' : 'Копировать'}
        </ActionButton>
        <ActionButton onClick={() => setSaveOpen(true)}>
          <Download className="h-3.5 w-3.5" />
          Скачать
        </ActionButton>
      </div>

      {saveOpen && <SaveModal result={result} onClose={() => setSaveOpen(false)} />}
    </>
  )
}

function ActionButton({ children, onClick }: { children: ReactNode; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'inline-flex items-center gap-1.5 rounded-lg px-2 py-1.5 text-[13px] font-medium',
        'text-ink-soft transition-colors hover:bg-panel hover:text-ink',
      )}
    >
      {children}
    </button>
  )
}
