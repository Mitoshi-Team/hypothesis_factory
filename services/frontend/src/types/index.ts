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

// --- Knowledge graph (docs/API_CONTRACT.md → GET /sessions/{id}/graph) ---------

/** Entity type produced by the NER/graph pipeline. */
export type NodeLabel = 'Material' | 'Process' | 'Property' | 'Parameter'

/** Relation type between two entities. */
export type EdgeRelation =
  | 'contains'
  | 'influences'
  | 'produces'
  | 'requires'
  | 'cites'
  | 'part_of'
  | 'similar_to'

/** A source passage backing an entity (for the node detail panel). */
export interface GraphSourceChunk {
  chunkId: string
  text: string
  documentTitle: string
  sectionPath: string
}

export interface GraphNode {
  id: string
  /** One of `NodeLabel`, kept as string for forward compatibility. */
  label: string
  name: string
  /** Extraction confidence from `metadata.score`, 0–1. */
  score?: number
  sourceChunks: GraphSourceChunk[]
}

export interface GraphEdge {
  source: string
  target: string
  /** One of `EdgeRelation`, kept as string for forward compatibility. */
  relation: string
  confidence: number
  /** Supporting text from `metadata.evidence`. */
  evidence?: string
}

/** A reasoning chain through the graph (pipeline output). */
export interface GraphChain {
  chainId: string
  nodeIds: string[]
  edgeLabels: string[]
  summary: string
}

export interface KnowledgeGraph {
  nodes: GraphNode[]
  edges: GraphEdge[]
  chains: GraphChain[]
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
