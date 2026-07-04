import { useState, type ReactNode } from 'react'
import { Check, Copy, Download, Network } from 'lucide-react'
import type { HypothesisResult } from '@/types'
import { cn } from '@/lib/cn'
import { CRITERIA_KEYS, criteriaLabel, verdictLabel } from '@/lib/format'
import { t } from '@/lib/lang'
import { useI18n } from '@/lib/i18n'
import { SaveModal } from './SaveModal'
import { GraphModal } from '@/components/graph/GraphModal'

function resultToText(r: HypothesisResult): string {
  const scores = CRITERIA_KEYS.map((k) => `${criteriaLabel(k)} ${r.scores[k].toFixed(1)}`).join(' · ')
  const lines = [
    r.title,
    `${scores} · ${verdictLabel(r.verdict)}`,
    '',
    `${t('result.hypothesisLabel')}: ${r.hypothesis}`,
    `${t('result.expectedEffect')}: ${r.expectedEffect}`,
    '',
    `${t('result.risks')}:`,
    ...r.risks.map((x) => `— ${x}`),
  ]
  if (r.suggestions.length) {
    lines.push('', `${t('result.nextChecks')}:`, ...r.suggestions.map((x) => `— ${x}`))
  }
  return lines.join('\n')
}

interface MessageActionsProps {
  result: HypothesisResult
  /** Session id — enables the graph button when this is the latest answer. */
  sessionId?: string
  showGraph?: boolean
}

export function MessageActions({ result, sessionId, showGraph }: MessageActionsProps) {
  const { t } = useI18n()
  const [copied, setCopied] = useState(false)
  const [saveOpen, setSaveOpen] = useState(false)
  const [graphOpen, setGraphOpen] = useState(false)

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
          {copied ? t('actions.copied') : t('actions.copy')}
        </ActionButton>
        <ActionButton onClick={() => setSaveOpen(true)}>
          <Download className="h-3.5 w-3.5" />
          {t('actions.download')}
        </ActionButton>
        {showGraph && sessionId && (
          <ActionButton onClick={() => setGraphOpen(true)}>
            <Network className="h-3.5 w-3.5" />
            {t('actions.viewGraph')}
          </ActionButton>
        )}
      </div>

      {saveOpen && <SaveModal result={result} onClose={() => setSaveOpen(false)} />}
      {graphOpen && sessionId && (
        <GraphModal sessionId={sessionId} onClose={() => setGraphOpen(false)} />
      )}
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
