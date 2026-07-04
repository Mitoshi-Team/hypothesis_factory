import type { HypothesisResult, Weights } from '@/types'
import { SAMPLE_RESULT } from '@/data/mock'

const GENERATION_DELAY_MS = 2400

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export interface GenerationRequest {
  problem: string
  constraints: string
  weights: Weights
  files: string[]
  iteration: number
}

/** Mocked pipeline call. Returns a single hypothesis result for the message. */
export async function generateHypothesis(req: GenerationRequest): Promise<HypothesisResult> {
  await delay(GENERATION_DELAY_MS)
  return {
    ...SAMPLE_RESULT,
    hypothesis:
      req.iteration > 0
        ? `С учётом уточнения «${req.problem.trim()}»: ${SAMPLE_RESULT.hypothesis}`
        : SAMPLE_RESULT.hypothesis,
  }
}
