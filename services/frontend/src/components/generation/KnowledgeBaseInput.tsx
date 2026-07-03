import { useState } from 'react'
import { FileText, ScrollText, Newspaper } from 'lucide-react'
import { Textarea } from '@/components/ui/Textarea'
import { cn } from '@/lib/cn'

export interface KnowledgeBase {
  articles: string
  patents: string
  reports: string
}

interface Props {
  value: KnowledgeBase
  onChange: (value: KnowledgeBase) => void
}

const TABS = [
  { key: 'articles', label: 'Статьи', icon: Newspaper, placeholder: 'Вставьте текст научных публикаций…' },
  { key: 'patents', label: 'Патенты', icon: ScrollText, placeholder: 'Вставьте описания патентов…' },
  { key: 'reports', label: 'Отчёты', icon: FileText, placeholder: 'Вставьте внутренние отчёты и результаты экспериментов…' },
] as const

export function KnowledgeBaseInput({ value, onChange }: Props) {
  const [active, setActive] = useState<keyof KnowledgeBase>('articles')

  const filledCount = (key: keyof KnowledgeBase) => (value[key].trim() ? 1 : 0)
  const totalFilled = filledCount('articles') + filledCount('patents') + filledCount('reports')

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-800">База знаний</h3>
        <span className="text-xs text-slate-400">Заполнено разделов: {totalFilled}/3</span>
      </div>

      <div className="flex gap-1 rounded-lg bg-slate-100 p-1">
        {TABS.map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            type="button"
            onClick={() => setActive(key)}
            className={cn(
              'flex flex-1 items-center justify-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-colors',
              active === key
                ? 'bg-white text-brand-700 shadow-sm'
                : 'text-slate-500 hover:text-slate-700',
            )}
          >
            <Icon className="h-4 w-4" />
            {label}
            {value[key].trim() && (
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
            )}
          </button>
        ))}
      </div>

      {TABS.map(
        ({ key, placeholder }) =>
          active === key && (
            <Textarea
              key={key}
              value={value[key]}
              placeholder={placeholder}
              rows={6}
              onChange={(e) => onChange({ ...value, [key]: e.target.value })}
            />
          ),
      )}
    </div>
  )
}
