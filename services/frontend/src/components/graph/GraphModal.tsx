import { useEffect, useMemo, useState } from 'react'
import { createPortal } from 'react-dom'
import { Network, X } from 'lucide-react'
import type { GraphChain, KnowledgeGraph } from '@/types'
import { cn } from '@/lib/cn'
import { useI18n } from '@/lib/i18n'
import { fetchGraph, humanizeError } from '@/lib/api'
import { connectedNodeIds, filterGraph } from '@/lib/graph'
import { Spinner } from '@/components/ui/Spinner'
import { GraphCanvas } from './GraphCanvas'
import { GraphLegend } from './GraphLegend'
import { NodeDetail } from './NodeDetail'
import { ChainsTab } from './ChainsTab'

interface Props {
  sessionId: string
  /** Hypothesis supporting nodes, kept in the core view when present. */
  supportingNodes?: string[]
  onClose: () => void
}

type Tab = 'graph' | 'chains'

const EMPTY_SUPPORTING_NODES: string[] = []

const edgeKey = (s: string, t: string) => `${s}>${t}`

export function GraphModal({ sessionId, supportingNodes = EMPTY_SUPPORTING_NODES, onClose }: Props) {
  const { t } = useI18n()
  const [graph, setGraph] = useState<KnowledgeGraph | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [tab, setTab] = useState<Tab>('graph')

  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [showAll, setShowAll] = useState(false)
  const [types, setTypes] = useState<Set<string>>(new Set())
  const [query, setQuery] = useState('')
  const [chain, setChain] = useState<GraphChain | null>(null)

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const load = () => {
    setLoading(true)
    setError(null)
    fetchGraph(sessionId)
      .then(setGraph)
      .catch((e) => setError(humanizeError(e)))
      .finally(() => setLoading(false))
  }

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(load, [sessionId])

  const coreIds = useMemo(
    () => (graph ? connectedNodeIds(graph, supportingNodes) : new Set<string>()),
    [graph, supportingNodes],
  )

  const filtered = useMemo(
    () =>
      graph
        ? filterGraph(graph, { showAll, types, query, keepIds: coreIds })
        : { nodes: [], edges: [], chains: [] },
    [graph, showAll, types, query, coreIds],
  )

  const highlightNodes = useMemo(
    () => new Set(chain?.nodeIds ?? []),
    [chain],
  )
  const highlightEdges = useMemo(() => {
    const set = new Set<string>()
    if (chain) {
      for (let i = 0; i < chain.nodeIds.length - 1; i++) {
        set.add(edgeKey(chain.nodeIds[i], chain.nodeIds[i + 1]))
      }
    }
    return set
  }, [chain])

  const selectedNode = useMemo(
    () => graph?.nodes.find((n) => n.id === selectedId) ?? null,
    [graph, selectedId],
  )

  const toggleType = (label: string) => {
    setTypes((prev) => {
      const next = new Set(prev)
      if (next.has(label)) next.delete(label)
      else next.add(label)
      return next
    })
  }

  const showChain = (c: GraphChain) => {
    setChain(c)
    setTab('graph')
    setSelectedId(null)
  }

  return createPortal(
    <div
      className="fixed inset-0 z-[110] flex items-stretch justify-center"
      role="dialog"
      aria-modal="true"
      aria-label={t('graph.title')}
    >
      <div className="absolute inset-0 bg-ink/30 animate-fade-in" onClick={onClose} />

      <div className="relative m-2 flex min-h-0 flex-1 flex-col overflow-hidden rounded-2xl border border-line bg-card shadow-pop animate-fade-up sm:m-6">
        {/* Header */}
        <div className="flex shrink-0 items-center gap-3 border-b border-line px-4 py-3">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-accent-50 text-accent-600">
            <Network className="h-[18px] w-[18px]" />
          </span>
          <div className="min-w-0">
            <h2 className="text-[15px] font-semibold leading-tight text-ink">{t('graph.title')}</h2>
            <p className="truncate text-[12px] text-ink-soft">
              {graph
                ? t('graph.stats', { nodes: filtered.nodes.length, edges: filtered.edges.length })
                : t('graph.subtitle')}
            </p>
          </div>

          {/* Tabs */}
          <div className="ml-auto flex items-center gap-1 rounded-lg bg-panel p-0.5">
            {(['graph', 'chains'] as Tab[]).map((key) => (
              <button
                key={key}
                type="button"
                onClick={() => setTab(key)}
                className={cn(
                  'rounded-md px-3 py-1.5 text-[13px] font-medium transition-colors',
                  tab === key ? 'bg-card text-ink shadow-soft' : 'text-ink-soft hover:text-ink',
                )}
              >
                {t(key === 'graph' ? 'graph.tab.graph' : 'graph.tab.chains')}
              </button>
            ))}
          </div>

          <button
            type="button"
            onClick={onClose}
            className="shrink-0 rounded-lg p-1.5 text-ink-faint hover:bg-panel hover:text-ink"
            aria-label={t('graph.close')}
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Body */}
        <div className="relative min-h-0 flex-1">
          {loading ? (
            <div className="grid h-full place-items-center">
              <div className="flex items-center gap-3 text-ink-faint">
                <Spinner className="h-5 w-5" />
                <span className="text-[14px]">{t('graph.loading')}</span>
              </div>
            </div>
          ) : error ? (
            <div className="grid h-full place-items-center px-6 text-center">
              <div className="flex flex-col items-center gap-3">
                <p className="text-[14px] text-ink-soft">{error}</p>
                <button
                  type="button"
                  onClick={load}
                  className="rounded-lg border border-line bg-panel px-3 py-1.5 text-[13px] font-medium text-ink hover:bg-card"
                >
                  {t('graph.retry')}
                </button>
              </div>
            </div>
          ) : !graph || graph.nodes.length === 0 ? (
            <div className="grid h-full place-items-center px-6 text-center">
              <p className="text-[13px] text-ink-faint">{t('graph.empty')}</p>
            </div>
          ) : tab === 'chains' ? (
            <div className="h-full overflow-y-auto scroll-slim">
              <ChainsTab graph={graph} onShowChain={showChain} />
            </div>
          ) : (
            <div className="flex h-full flex-col">
              <GraphLegend
                graph={graph}
                coreCount={coreIds.size}
                types={types}
                onToggleType={toggleType}
                showAll={showAll}
                onToggleShowAll={setShowAll}
                query={query}
                onQuery={setQuery}
              />
              <div className="relative min-h-0 flex-1">
                <GraphCanvas
                  graph={filtered}
                  coreIds={coreIds}
                  selectedId={selectedId}
                  highlightNodes={highlightNodes}
                  highlightEdges={highlightEdges}
                  onSelect={setSelectedId}
                />

                {/* Node detail — floating panel on the right */}
                {selectedNode ? (
                  <div className="absolute inset-y-3 right-3 w-72 overflow-hidden rounded-xl border border-line bg-card shadow-pop animate-fade-in">
                    <NodeDetail node={selectedNode} onClose={() => setSelectedId(null)} />
                  </div>
                ) : (
                  <div className="pointer-events-none absolute bottom-3 left-1/2 -translate-x-1/2 rounded-full bg-card/90 px-3 py-1.5 text-[12px] text-ink-faint shadow-soft">
                    {t('graph.selectHint')}
                  </div>
                )}

                {/* Active chain pill */}
                {chain && (
                  <button
                    type="button"
                    onClick={() => setChain(null)}
                    className="absolute left-3 top-3 inline-flex items-center gap-1.5 rounded-full bg-accent-600 px-3 py-1.5 text-[12px] font-medium text-white shadow-pop"
                  >
                    {chain.summary}
                    <X className="h-3.5 w-3.5" />
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>,
    document.body,
  )
}
