import type { BusinessReport, GenerationInput, HistoryEntry } from '@/types'
import { MOCK_HISTORY, MOCK_REPORT } from '@/data/mock'

const GENERATION_DELAY_MS = 2600

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export async function generateHypotheses(input: GenerationInput): Promise<BusinessReport> {
  await delay(GENERATION_DELAY_MS)

  const constraints = input.constraints
    .split('\n')
    .map((s) => s.trim())
    .filter(Boolean)

  return {
    ...MOCK_REPORT,
    id: `rep-${Date.now()}`,
    createdAt: new Date().toISOString(),
    problem: input.problem.trim() || MOCK_REPORT.problem,
    constraints: constraints.length > 0 ? constraints : MOCK_REPORT.constraints,
  }
}

export async function getHistory(): Promise<HistoryEntry[]> {
  await delay(300)
  return MOCK_HISTORY
}

export async function getReport(_reportId: string): Promise<BusinessReport> {
  await delay(200)
  return MOCK_REPORT
}
