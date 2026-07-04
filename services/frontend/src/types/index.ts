// Data model aligned with docs/API_CONTRACT.md (sessions, messages, results).

/** Criteria weights set once per session. */
export interface Weights {
  novelty: number
  feasibility: number
  effect: number
  risk: number
}

/** Per-criterion scores from the review, on a 0-10 scale. */
export interface Scores {
  novelty: number
  feasibility: number
  effect: number
  risk: number
}

export type Verdict = 'accept' | 'reject'

/** A single generated hypothesis with its review, mirroring `pipeline_results`. */
export interface HypothesisResult {
  title: string
  hypothesis: string
  expectedEffect: string
  scores: Scores
  verdict: Verdict
  risks: string[]
  suggestions: string[]
  evidenceSources: string[]
}

export type Message =
  | {
      id: string
      role: 'user'
      content: string
      files: string[]
    }
  | {
      id: string
      role: 'assistant'
      status: 'thinking' | 'done' | 'failed'
      iteration: number
      result?: HypothesisResult
      error?: string
    }

export interface Session {
  id: string
  title: string
  createdAt: string
  constraints: string
  weights: Weights
  messages: Message[]
  /** True once the full history (messages + results) has been fetched. */
  loaded?: boolean
}

/** Authenticated user, as known on the client (the API has no /me endpoint). */
export interface User {
  username: string
}

export const DEFAULT_WEIGHTS: Weights = {
  novelty: 1.5,
  feasibility: 1.0,
  effect: 2.0,
  risk: 0.5,
}
