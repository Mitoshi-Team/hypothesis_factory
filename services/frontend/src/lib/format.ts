import type { Verdict } from '@/types'
import { getLang, LOCALE_TAG, t } from '@/lib/lang'

/** Criteria keys in canonical display order. */
export const CRITERIA_KEYS = ['novelty', 'feasibility', 'effect', 'risk'] as const

/** Localized label for a criterion key (novelty / feasibility / effect / risk). */
export function criteriaLabel(key: string): string {
  return t(`criteria.${key}`)
}

export function verdictLabel(v: Verdict): string {
  return v === 'accept' ? t('verdict.accept') : t('verdict.reject')
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleString(LOCALE_TAG[getLang()], {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/** Compact date for the sidebar: "today", "yesterday", "3 days ago" or "3 Jul". */
export function relativeDay(iso: string): string {
  const d = new Date(iso)
  const now = new Date()
  const startOf = (x: Date) => new Date(x.getFullYear(), x.getMonth(), x.getDate()).getTime()
  const diff = Math.round((startOf(now) - startOf(d)) / 86_400_000)
  if (diff <= 0) return t('date.today')
  if (diff === 1) return t('date.yesterday')
  if (diff < 7) return t('date.daysAgo', { n: diff })
  return d.toLocaleDateString(LOCALE_TAG[getLang()], { day: 'numeric', month: 'short' })
}

export function reportFileName(title: string, ext: string): string {
  const base = title
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 50)
  return `hypothesis-${base || 'result'}.${ext}`
}
