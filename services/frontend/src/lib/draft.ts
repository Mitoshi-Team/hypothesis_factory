// Pending message draft: what an unauthenticated user tried to send.
// Kept in memory (File objects survive because navigation is client-side only)
// with a sessionStorage backup for the text parts, so a hard reload on the
// auth screen still restores the message and settings — only files are lost.

import type { Weights } from '@/types'

export interface PendingDraft {
  problem: string
  constraints: string
  weights: Weights
  files: File[]
}

const STORAGE_KEY = 'hf.pending_draft'

let memoryDraft: PendingDraft | null = null

export function saveDraft(draft: PendingDraft): void {
  memoryDraft = draft
  try {
    sessionStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        problem: draft.problem,
        constraints: draft.constraints,
        weights: draft.weights,
      }),
    )
  } catch {
    // Storage full/unavailable — the in-memory copy still works for SPA flow.
  }
}

export function hasDraft(): boolean {
  return memoryDraft !== null || sessionStorage.getItem(STORAGE_KEY) !== null
}

/** Read and clear the draft (it is sent exactly once, right after login). */
export function takeDraft(): PendingDraft | null {
  const stored = sessionStorage.getItem(STORAGE_KEY)
  sessionStorage.removeItem(STORAGE_KEY)
  const draft = memoryDraft
  memoryDraft = null
  if (draft) return draft
  if (!stored) return null
  try {
    const parsed = JSON.parse(stored)
    return {
      problem: parsed.problem ?? '',
      constraints: parsed.constraints ?? '',
      weights: parsed.weights,
      files: [],
    }
  } catch {
    return null
  }
}
