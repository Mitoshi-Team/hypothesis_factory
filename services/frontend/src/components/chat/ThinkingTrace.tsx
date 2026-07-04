import { useEffect, useState } from 'react'
import { Check } from 'lucide-react'
import { cn } from '@/lib/cn'

const STEPS = [
  'Извлекаю сущности и связи',
  'Ищу пробелы в знаниях',
  'Формирую гипотезу по аналогиям',
  'Оцениваю новизну и риски',
]

const STEP_INTERVAL_MS = 560

export function ThinkingTrace() {
  const [current, setCurrent] = useState(0)

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrent((c) => (c < STEPS.length - 1 ? c + 1 : c))
    }, STEP_INTERVAL_MS)
    return () => clearInterval(timer)
  }, [])

  return (
    <ul className="flex flex-col gap-2 py-1">
      {STEPS.map((step, i) => {
        const done = i < current
        const activeStep = i === current
        return (
          <li
            key={step}
            className={cn(
              'flex items-center gap-2.5 text-[14px] transition-colors',
              done ? 'text-ink-soft' : activeStep ? 'text-ink' : 'text-ink-faint',
            )}
          >
            <span
              className={cn(
                'grid h-4 w-4 shrink-0 place-items-center rounded-full',
                done ? 'bg-accent-500 text-white' : 'border border-line-strong',
              )}
            >
              {done ? (
                <Check className="h-2.5 w-2.5" strokeWidth={3} />
              ) : activeStep ? (
                <span className="h-1.5 w-1.5 animate-[pulse2_1.1s_ease-in-out_infinite] rounded-full bg-accent-500" />
              ) : null}
            </span>
            {step}
          </li>
        )
      })}
    </ul>
  )
}
