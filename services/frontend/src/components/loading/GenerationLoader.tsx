import { useEffect, useState } from 'react'
import { Check, Loader2 } from 'lucide-react'
import { cn } from '@/lib/cn'

const STEPS = [
  'Извлечение сущностей и связей',
  'Поиск паттернов и пробелов в знаниях',
  'Формирование гипотез по аналогиям',
  'Ранжирование по новизне и рискам',
  'Сборка бизнес-отчёта',
]

const STEP_INTERVAL_MS = 520

export function GenerationLoader() {
  const [current, setCurrent] = useState(0)

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrent((c) => (c < STEPS.length - 1 ? c + 1 : c))
    }, STEP_INTERVAL_MS)
    return () => clearInterval(timer)
  }, [])

  return (
    <div className="mx-auto flex max-w-md flex-col gap-6 py-16 animate-fade-in-up">
      <div className="flex items-center gap-3">
        <Loader2 className="h-5 w-5 animate-spin text-brand-600" />
        <div>
          <h2 className="font-semibold tracking-tight text-slate-900">Генерируем гипотезы</h2>
          <p className="text-sm text-slate-500">
            Анализируем базу знаний и формируем обоснованные гипотезы
          </p>
        </div>
      </div>

      <ol className="flex w-full flex-col gap-2">
        {STEPS.map((step, i) => {
          const done = i < current
          const active = i === current
          return (
            <li
              key={step}
              className={cn(
                'flex items-center gap-3 rounded-lg border px-4 py-3 transition-all',
                done && 'border-emerald-200 bg-emerald-50',
                active && 'border-brand-300 bg-brand-50 shadow-sm',
                !done && !active && 'border-slate-200 bg-white opacity-50',
              )}
            >
              <span
                className={cn(
                  'flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full',
                  done && 'bg-emerald-500 text-white',
                  active && 'bg-brand-600 text-white',
                  !done && !active && 'bg-slate-200 text-slate-400',
                )}
              >
                {done ? (
                  <Check className="h-4 w-4" />
                ) : active ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <span className="text-xs">{i + 1}</span>
                )}
              </span>
              <span
                className={cn(
                  'text-sm font-medium',
                  done ? 'text-emerald-700' : active ? 'text-brand-700' : 'text-slate-400',
                )}
              >
                {step}
              </span>
            </li>
          )
        })}
      </ol>
    </div>
  )
}
