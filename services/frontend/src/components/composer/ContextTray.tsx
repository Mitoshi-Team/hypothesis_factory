import type { Weights } from '@/types'
import { Textarea } from '@/components/ui/Textarea'
import { FileDropzone } from '@/components/ui/FileDropzone'
import { CRITERIA_LABELS } from '@/lib/format'

const WEIGHT_KEYS: Array<keyof Weights> = ['novelty', 'feasibility', 'effect', 'risk']

export interface ContextValue {
  constraints: string
  weights: Weights
  files: string[]
}

interface Props {
  value: ContextValue
  onChange: (next: ContextValue) => void
}

export function ContextTray({ value, onChange }: Props) {
  return (
    <div className="flex flex-col gap-4 border-b border-line px-3.5 py-3.5">
      <label className="flex flex-col gap-1.5">
        <span className="text-xs font-medium text-ink-soft">Ограничения</span>
        <Textarea
          value={value.constraints}
          onChange={(e) => onChange({ ...value, constraints: e.target.value })}
          rows={2}
          className="min-h-[56px] text-[13px]"
          placeholder="Бюджет, оборудование, нормативы, доступное сырьё…"
        />
      </label>

      <div className="flex flex-col gap-2.5">
        <span className="text-xs font-medium text-ink-soft">Веса критериев</span>
        <div className="grid grid-cols-2 gap-x-5 gap-y-2.5">
          {WEIGHT_KEYS.map((key) => (
            <div key={key} className="flex items-center gap-2.5">
              <span className="w-24 shrink-0 text-[13px] text-ink-soft">{CRITERIA_LABELS[key]}</span>
              <input
                type="range"
                min={0}
                max={3}
                step={0.1}
                value={value.weights[key]}
                onChange={(e) =>
                  onChange({
                    ...value,
                    weights: { ...value.weights, [key]: Number(e.target.value) },
                  })
                }
                className="h-1.5 flex-1 cursor-pointer appearance-none rounded-full bg-line accent-accent-500"
                aria-label={`Вес: ${CRITERIA_LABELS[key]}`}
              />
              <span className="w-7 shrink-0 text-right font-mono text-[12px] tabular-nums text-ink">
                {value.weights[key].toFixed(1)}
              </span>
            </div>
          ))}
        </div>
      </div>

      <label className="flex flex-col gap-1.5">
        <span className="text-xs font-medium text-ink-soft">Материалы и данные</span>
        <FileDropzone
          files={value.files}
          onFilesChange={(files) => onChange({ ...value, files })}
          accept=".xlsx,.xls,.csv,.json,.pdf,.docx,.txt,.md"
          hint="Excel, CSV, JSON, PDF, Word · до 20 МБ"
        />
      </label>
    </div>
  )
}
