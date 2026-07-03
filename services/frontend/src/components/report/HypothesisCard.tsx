import { useState, type ReactNode } from 'react'
import {
  ChevronDown,
  Cog,
  ExternalLink,
  Lightbulb,
  ShieldAlert,
  TrendingUp,
} from 'lucide-react'
import type { Hypothesis, Risk } from '@/types'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { cn } from '@/lib/cn'
import { riskCategoryLabel, riskLevelLabel, sourceKindLabel } from '@/lib/format'

const RISK_TONE: Record<Risk['level'], 'green' | 'amber' | 'red'> = {
  low: 'green',
  medium: 'amber',
  high: 'red',
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex-1">
      <div className="mb-1 flex items-center justify-between text-xs">
        <span className="text-slate-500">{label}</span>
        <span className="font-mono font-semibold text-slate-700">{value}/100</span>
      </div>
      <div className="h-1.5 w-full rounded-full bg-slate-100">
        <div
          className={cn(
            'h-full rounded-full',
            value >= 70 ? 'bg-emerald-500' : value >= 50 ? 'bg-amber-500' : 'bg-slate-400',
          )}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  )
}

export function HypothesisCard({ hypothesis, index }: { hypothesis: Hypothesis; index: number }) {
  const [open, setOpen] = useState(index === 0)
  const h = hypothesis

  return (
    <Card className="overflow-hidden">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-start gap-3 p-5 text-left hover:bg-slate-50"
      >
        <span className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-brand-600 text-sm font-bold text-white">
          {index + 1}
        </span>
        <div className="flex-1">
          <h3 className="font-semibold leading-snug text-slate-900">{h.title}</h3>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <Badge tone="brand">
              <TrendingUp className="h-3 w-3" />
              <span className="font-mono">{h.kpiImpact}</span>
            </Badge>
            <Badge tone="slate">Новизна <span className="font-mono">{h.novelty}</span></Badge>
            <Badge tone="slate">Реализуемость <span className="font-mono">{h.feasibility}</span></Badge>
          </div>
        </div>
        <ChevronDown
          className={cn('h-5 w-5 flex-shrink-0 text-slate-400 transition-transform', open && 'rotate-180')}
        />
      </button>

      {open && (
        <div className="flex flex-col gap-5 border-t border-slate-100 p-5 animate-fade-in-up">
          <div className="flex gap-4">
            <Metric label="Новизна" value={h.novelty} />
            <Metric label="Реализуемость" value={h.feasibility} />
          </div>

          <Section icon={Lightbulb} title="Обоснование">
            <p className="text-sm leading-relaxed text-slate-600">{h.rationale}</p>
          </Section>

          <Section icon={Cog} title="Механизм влияния">
            <p className="text-sm leading-relaxed text-slate-600">{h.mechanism}</p>
          </Section>

          <Section icon={TrendingUp} title="Ожидаемая ценность">
            <p className="text-sm leading-relaxed text-slate-600">{h.expectedValue}</p>
          </Section>

          <Section icon={ShieldAlert} title="Риски">
            <ul className="flex flex-col gap-2">
              {h.risks.map((r, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-slate-600">
                  <Badge tone={RISK_TONE[r.level]}>
                    {riskCategoryLabel(r.category)} · {riskLevelLabel(r.level)}
                  </Badge>
                  <span className="flex-1">{r.description}</span>
                </li>
              ))}
            </ul>
          </Section>

          <Section icon={ExternalLink} title="Источники">
            <ul className="flex flex-col gap-1.5">
              {h.sources.map((s) => (
                <li key={s.id} className="flex items-center gap-2 text-sm">
                  <Badge tone="slate">{sourceKindLabel(s.kind)}</Badge>
                  {s.url ? (
                    <a
                      href={s.url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-brand-600 hover:underline"
                    >
                      {s.title}
                    </a>
                  ) : (
                    <span className="text-slate-600">{s.title}</span>
                  )}
                  {s.year && <span className="text-xs text-slate-400">({s.year})</span>}
                </li>
              ))}
            </ul>
          </Section>
        </div>
      )}
    </Card>
  )
}

function Section({
  icon: Icon,
  title,
  children,
}: {
  icon: typeof Lightbulb
  title: string
  children: ReactNode
}) {
  return (
    <div>
      <div className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-slate-400">
        <Icon className="h-3.5 w-3.5" />
        {title}
      </div>
      {children}
    </div>
  )
}
