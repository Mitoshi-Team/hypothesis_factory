// Knowledge-graph helpers: wire-format mapping, type colors, connectivity and
// filtering. Kept UI-agnostic so both the API client and the graph components
// share one source of truth. See docs/API_CONTRACT.md → Graph.

import type { GraphChain, GraphEdge, GraphNode, KnowledgeGraph } from '@/types'

// ---------------------------------------------------------------------------
// Wire format (snake_case, as returned by GET /sessions/{id}/graph)

interface ApiGraphChunk {
  chunk_id?: string
  element_id?: string
  text?: string
  document_title?: string
  section_path?: string
}

interface ApiGraphNode {
  id: string
  label?: string
  name?: string
  source_chunks?: ApiGraphChunk[]
  metadata?: { model?: string; score?: number }
}

interface ApiGraphEdge {
  source: string
  target: string
  relation?: string
  confidence?: number
  metadata?: { evidence?: string }
}

interface ApiGraphChain {
  chain_id: string
  node_ids?: string[]
  edge_labels?: string[]
  summary?: string
}

export interface ApiGraph {
  nodes?: ApiGraphNode[]
  edges?: ApiGraphEdge[]
  chains?: ApiGraphChain[]
}

/** Normalize the wire graph into the camelCase client model. */
export function mapGraph(g: ApiGraph): KnowledgeGraph {
  const nodes: GraphNode[] = (g.nodes ?? []).map((n) => ({
    id: n.id,
    label: n.label ?? 'Material',
    name: (n.name ?? '').trim(),
    score: n.metadata?.score,
    sourceChunks: (n.source_chunks ?? []).map((c) => ({
      chunkId: c.chunk_id ?? c.element_id ?? '',
      text: c.text ?? '',
      documentTitle: c.document_title ?? '',
      sectionPath: c.section_path ?? '',
    })),
  }))
  const edges: GraphEdge[] = (g.edges ?? []).map((e) => ({
    source: e.source,
    target: e.target,
    relation: e.relation ?? 'influences',
    confidence: e.confidence ?? 0,
    evidence: e.metadata?.evidence,
  }))
  const chains: GraphChain[] = (g.chains ?? []).map((c) => ({
    chainId: c.chain_id,
    nodeIds: c.node_ids ?? [],
    edgeLabels: c.edge_labels ?? [],
    summary: c.summary ?? '',
  }))
  return { nodes, edges, chains }
}

// ---------------------------------------------------------------------------
// Presentation constants

/** Node fill by entity type. Aligned with the app's cool-blue accent + a
 *  distinct, tasteful hue per remaining type. Unknown labels fall back to grey. */
export const NODE_COLORS: Record<string, string> = {
  Material: '#2E6BF0', // accent-500
  Process: '#0E9E8E', // teal
  Property: '#E0912F', // amber
  Parameter: '#8B5CF6', // violet
}

export const NODE_FALLBACK_COLOR = '#9AA0A6' // ink-faint

export function nodeColor(label: string): string {
  return NODE_COLORS[label] ?? NODE_FALLBACK_COLOR
}

/** Canonical order for legends and filters. */
export const NODE_LABELS = ['Material', 'Process', 'Property', 'Parameter'] as const

/** i18n key for a node type; unknown labels render their raw string. */
export function nodeLabelKey(label: string): string {
  return `graph.node.${label}`
}

/** i18n key for a relation type. */
export function relationLabelKey(relation: string): string {
  return `graph.rel.${relation}`
}

// ---------------------------------------------------------------------------
// Connectivity & filtering

/** Ids of every node that participates in an edge or a chain (the "core"),
 *  plus any hypothesis supporting nodes passed in. */
export function connectedNodeIds(
  graph: KnowledgeGraph,
  supportingNodes: string[] = [],
): Set<string> {
  const ids = new Set<string>(supportingNodes)
  for (const e of graph.edges) {
    ids.add(e.source)
    ids.add(e.target)
  }
  for (const c of graph.chains) {
    for (const id of c.nodeIds) ids.add(id)
  }
  return ids
}

export interface GraphFilter {
  /** When false, only the connected core is shown. */
  showAll: boolean
  /** Visible node types; empty set means "all types". */
  types: Set<string>
  /** Case-insensitive substring match on node name. */
  query: string
  /** Node ids that always stay visible (e.g. the connected core). */
  keepIds?: Set<string>
}

/** Apply the active filters, returning a subgraph whose edges only connect
 *  visible nodes. */
export function filterGraph(graph: KnowledgeGraph, filter: GraphFilter): KnowledgeGraph {
  const { showAll, types, query, keepIds } = filter
  const q = query.trim().toLowerCase()

  const nodes = graph.nodes.filter((n) => {
    if (!showAll && !(keepIds?.has(n.id) ?? false)) return false
    if (types.size > 0 && !types.has(n.label)) return false
    if (q && !n.name.toLowerCase().includes(q)) return false
    return true
  })

  const visible = new Set(nodes.map((n) => n.id))
  const edges = graph.edges.filter((e) => visible.has(e.source) && visible.has(e.target))

  return { nodes, edges, chains: graph.chains }
}

/** Count nodes per type across the full graph (for legend badges). */
export function countByLabel(graph: KnowledgeGraph): Record<string, number> {
  const counts: Record<string, number> = {}
  for (const n of graph.nodes) counts[n.label] = (counts[n.label] ?? 0) + 1
  return counts
}
