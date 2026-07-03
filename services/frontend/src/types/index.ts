export interface Source {
  id: string
  title: string
  kind: 'article' | 'patent' | 'report' | 'dataset'
  url?: string
  year?: number
}

export interface Risk {
  category: 'technical' | 'economic' | 'regulatory'
  description: string
  level: 'low' | 'medium' | 'high'
}

export interface Hypothesis {
  id: string
  title: string
  rationale: string
  mechanism: string
  sources: Source[]
  novelty: number
  feasibility: number
  risks: Risk[]
  expectedValue: string
  kpiImpact: string
}

export interface BusinessReport {
  id: string
  createdAt: string
  problem: string
  constraints: string[]
  summary: string
  hypotheses: Hypothesis[]
}

export interface HistoryEntry {
  id: string
  createdAt: string
  problem: string
  reportId: string
  hypothesisCount: number
}

export interface GenerationInput {
  problem: string
  constraints: string
  knowledgeBase: {
    articles: string
    patents: string
    reports: string
  }
  materials: string[]
}
