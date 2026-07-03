const RISK_LABELS: Record<string, string> = {
  technical: 'Технический',
  economic: 'Экономический',
  regulatory: 'Нормативный',
}

const RISK_LEVELS: Record<string, string> = {
  low: 'низкий',
  medium: 'средний',
  high: 'высокий',
}

const SOURCE_LABELS: Record<string, string> = {
  article: 'Статья',
  patent: 'Патент',
  report: 'Отчёт',
  dataset: 'Датасет',
}

export function riskCategoryLabel(category: string): string {
  return RISK_LABELS[category] ?? category
}

export function riskLevelLabel(level: string): string {
  return RISK_LEVELS[level] ?? level
}

export function sourceKindLabel(kind: string): string {
  return SOURCE_LABELS[kind] ?? kind
}

export function formatDate(iso: string): string {
  const d = new Date(iso)
  return d.toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function reportFileName(problem: string, ext: string): string {
  const base = problem
    .toLowerCase()
    .replace(/[^\p{L}\p{N}]+/gu, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 50)
  return `hypotheses-${base || 'report'}.${ext}`
}
