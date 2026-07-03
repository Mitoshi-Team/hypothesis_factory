import { CalendarDays, ClipboardList, ListChecks } from 'lucide-react'
import type { BusinessReport as Report } from '@/types'
import { Card } from '@/components/ui/Card'
import { HypothesisCard } from './HypothesisCard'
import { ReportActions } from './ReportActions'
import { formatDate } from '@/lib/format'

export function BusinessReport({ report }: { report: Report }) {
  return (
    <div className="flex flex-col gap-6 animate-fade-in-up">
      <Card className="p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 text-xs font-medium text-brand-600">
              <ClipboardList className="h-4 w-4" />
              БИЗНЕС-ОТЧЁТ
            </div>
            <h1 className="mt-2 text-2xl font-bold leading-tight text-slate-900">
              {report.problem}
            </h1>
            <div className="mt-2 flex items-center gap-1.5 text-sm text-slate-400">
              <CalendarDays className="h-4 w-4" />
              {formatDate(report.createdAt)}
            </div>
          </div>
          <ReportActions report={report} />
        </div>

        <p className="mt-5 rounded-lg bg-slate-50 p-4 text-sm leading-relaxed text-slate-600">
          {report.summary}
        </p>

        {report.constraints.length > 0 && (
          <div className="mt-4">
            <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
              Ограничения
            </div>
            <ul className="flex flex-col gap-1">
              {report.constraints.map((c, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-slate-600">
                  <span className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-brand-400" />
                  {c}
                </li>
              ))}
            </ul>
          </div>
        )}
      </Card>

      <div className="flex items-center gap-2">
        <ListChecks className="h-5 w-5 text-brand-600" />
        <h2 className="text-lg font-bold text-slate-900">
          Гипотезы ({report.hypotheses.length})
        </h2>
      </div>

      <div className="flex flex-col gap-4">
        {report.hypotheses.map((h, i) => (
          <HypothesisCard key={h.id} hypothesis={h} index={i} />
        ))}
      </div>
    </div>
  )
}
