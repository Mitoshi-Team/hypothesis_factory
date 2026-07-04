import { useMemo } from 'react'
import { ArrowRight, GitBranch } from 'lucide-react'
import type { GraphChain, KnowledgeGraph } from '@/types'
import { useI18n } from '@/lib/i18n'

interface Props {
  graph: KnowledgeGraph
  onShowChain: (chain: GraphChain) => void
}

/** List of reasoning chains; clicking one jumps to the graph with it highlighted. */
export function ChainsTab({ graph, onShowChain }: Props) {
  const { t } = useI18n()
  const nameById = useMemo(() => {
    const m = new Map<string, string>()
    for (const n of graph.nodes) m.set(n.id, n.name)
    return m
  }, [graph.nodes])

  if (graph.chains.length === 0) {
    return (
      <div className="grid h-full place-items-center px-6 text-center">
        <p className="text-[13px] text-ink-faint">{t('graph.chainsEmpty')}</p>
      </div>
    )
  }

  return (
    <div className="mx-auto w-full max-w-3xl px-4 py-5">
      <ul className="flex flex-col gap-3">
        {graph.chains.map((c) => (
          <li key={c.chainId}>
            <button
              type="button"
              onClick={() => onShowChain(c)}
              className="group flex w-full flex-col gap-2 rounded-xl border border-line bg-card p-3.5 text-left shadow-soft transition-colors hover:border-accent-200 hover:bg-accent-50/40"
            >
              <div className="flex items-center justify-between gap-3">
                <span className="inline-flex items-center gap-1.5 text-[12px] font-medium text-ink-soft">
                  <GitBranch className="h-3.5 w-3.5 text-accent-500" />
                  {t('graph.chainNodes', { n: c.nodeIds.length })}
                </span>
                <span className="text-[12px] text-accent-600 opacity-0 transition-opacity group-hover:opacity-100">
                  {t('graph.showOnGraph')}
                </span>
              </div>
              <div className="flex flex-wrap items-center gap-x-1.5 gap-y-1.5">
                {c.nodeIds.map((id, i) => (
                  <span key={id + i} className="flex items-center gap-1.5">
                    <span className="rounded-md bg-panel px-2 py-0.5 text-[13px] font-medium text-ink">
                      {nameById.get(id) ?? id}
                    </span>
                    {i < c.nodeIds.length - 1 && (
                      <span className="flex items-center gap-1 text-[11px] text-ink-faint">
                        <ArrowRight className="h-3 w-3" />
                        {c.edgeLabels[i] && (
                          <span>{t(`graph.rel.${c.edgeLabels[i]}`)}</span>
                        )}
                      </span>
                    )}
                  </span>
                ))}
              </div>
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
