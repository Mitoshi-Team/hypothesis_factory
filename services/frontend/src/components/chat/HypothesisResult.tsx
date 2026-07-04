import { useState, type ReactNode } from 'react'
import { Check, ChevronDown } from 'lucide-react'
import type { HypothesisResult as Result } from '@/types'
import { cn } from '@/lib/cn'
import { CRITERIA_LABELS, verdictLabel } from '@/lib/format'

const ORDER: Array<keyof Result['scores']> = ['novelty', 'feasibility', 'effect', 'risk']

export function HypothesisResult({ result }: { result: Result }) {
  const [sourcesOpen, setSourcesOpen] = useState(false)

  return (
    <div className="overflow-hidden rounded-xl border border-line bg-card shadow-soft">
      <div className="flex flex-col gap-4 p-4 sm:p-5">
        {/* Title + verdict */}
        <div className="flex items-start justify-between gap-3">
          <h3 className="text-[15px] font-semibold leading-snug text-ink">{result.title}</h3>
          <span
            className={cn(
              'shrink-0 rounded-full px-2 py-0.5 text-[11px] font-medium',
              result.verdict === 'accept'
                ? 'bg-emerald-50 text-emerald-700'
                : 'bg-red-50 text-red-700',
            )}
          >
            {verdictLabel(result.verdict)}
          </span>
        </div>

        <p className="text-[14px] leading-relaxed text-ink-soft">{result.hypothesis}</p>

        {/* Scores */}
        <div className="grid grid-cols-4 gap-px overflow-hidden rounded-lg border border-line bg-line">
          {ORDER.map((key) => (
            <div key={key} className="flex flex-col gap-0.5 bg-card px-2 py-2.5 text-center">
              <span className="font-mono text-lg font-semibold tabular-nums text-ink">
                {result.scores[key].toFixed(1)}
              </span>
              <span className="text-[11px] text-ink-faint">{CRITERIA_LABELS[key]}</span>
            </div>
          ))}
        </div>

        {/* Expected effect */}
        <Field label="Ожидаемый эффект">
          <p className="text-[14px] leading-relaxed text-ink-soft">{result.expectedEffect}</p>
        </Field>

        {/* Risks */}
        {result.risks.length > 0 && (
          <Field label="Риски">
            <ul className="flex flex-col gap-1.5">
              {result.risks.map((r, i) => (
                <li key={i} className="flex gap-2 text-[14px] text-ink-soft">
                  <span className="mt-2 h-1 w-1 shrink-0 rounded-full bg-ink-faint" />
                  {r}
                </li>
              ))}
            </ul>
          </Field>
        )}

        {/* Suggestions */}
        {result.suggestions.length > 0 && (
          <Field label="Что проверить дальше">
            <ul className="flex flex-col gap-1.5">
              {result.suggestions.map((s, i) => (
                <li key={i} className="flex gap-2 text-[14px] text-ink-soft">
                  <Check className="mt-0.5 h-4 w-4 shrink-0 text-accent-500" strokeWidth={2} />
                  {s}
                </li>
              ))}
            </ul>
          </Field>
        )}
      </div>

      {/* Sources */}
      {result.evidenceSources.length > 0 && (
        <div className="border-t border-line">
          <button
            type="button"
            onClick={() => setSourcesOpen((o) => !o)}
            aria-expanded={sourcesOpen}
            className="flex w-full items-center justify-between px-4 py-2.5 text-[13px] text-ink-soft transition-colors hover:bg-panel sm:px-5"
          >
            <span>Источники · {result.evidenceSources.length}</span>
            <ChevronDown
              className={cn('h-4 w-4 text-ink-faint transition-transform', sourcesOpen && 'rotate-180')}
            />
          </button>
          {sourcesOpen && (
            <ul className="flex flex-col gap-1.5 px-4 pb-3.5 sm:px-5">
              {result.evidenceSources.map((s, i) => (
                <li key={i} className="text-[13px] text-ink-soft">
                  {s}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="flex flex-col gap-1.5">
      <span className="text-xs font-medium text-ink-faint">{label}</span>
      {children}
    </div>
  )
}
