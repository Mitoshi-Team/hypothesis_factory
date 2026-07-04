import type { Verdict } from '@/types'

export const CRITERIA_LABELS: Record<string, string> = {
  novelty: 'Новизна',
  feasibility: 'Реализуемость',
  effect: 'Эффект',
  risk: 'Риск',
}

export function verdictLabel(v: Verdict): string {
  return v === 'accept' ? 'Принята' : 'Отклонена'
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/** Compact date for the sidebar: "сегодня", "вчера", or "3 июл". */
export function relativeDay(iso: string): string {
  const d = new Date(iso)
  const now = new Date()
  const startOf = (x: Date) => new Date(x.getFullYear(), x.getMonth(), x.getDate()).getTime()
  const diff = Math.round((startOf(now) - startOf(d)) / 86_400_000)
  if (diff <= 0) return 'сегодня'
  if (diff === 1) return 'вчера'
  if (diff < 7) return `${diff} дн назад`
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}

export function reportFileName(title: string, ext: string): string {
  const base = title
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 50)
  return `hypothesis-${base || 'result'}.${ext}`
}
