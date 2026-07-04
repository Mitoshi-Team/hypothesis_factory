import { Search } from 'lucide-react'
import type { KnowledgeGraph } from '@/types'
import { cn } from '@/lib/cn'
import { useI18n } from '@/lib/i18n'
import { NODE_LABELS, countByLabel, nodeColor, nodeLabelKey } from '@/lib/graph'
import { Switch } from '@/components/ui/Switch'

interface Props {
  graph: KnowledgeGraph
  coreCount: number
  types: Set<string>
  onToggleType: (label: string) => void
  showAll: boolean
  onToggleShowAll: (v: boolean) => void
  query: string
  onQuery: (v: string) => void
}

/** Top bar: search, node-type legend/filters and the core/all entities switch. */
export function GraphLegend({
  graph,
  coreCount,
  types,
  onToggleType,
  showAll,
  onToggleShowAll,
  query,
  onQuery,
}: Props) {
  const { t } = useI18n()
  const counts = countByLabel(graph)

  return (
    <div className="flex flex-wrap items-center gap-2 border-b border-line bg-panel/60 px-3 py-2.5">
      <div className="relative">
        <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-ink-faint" />
        <input
          value={query}
          onChange={(e) => onQuery(e.target.value)}
          placeholder={t('graph.search')}
          className="h-8 w-44 rounded-lg border border-line bg-card pl-8 pr-2 text-[13px] text-ink placeholder:text-ink-faint focus:border-accent-200"
        />
      </div>

      <div className="flex flex-wrap items-center gap-1">
        {NODE_LABELS.map((label) => {
          const active = types.size === 0 || types.has(label)
          const color = nodeColor(label)
          return (
            <button
              key={label}
              type="button"
              onClick={() => onToggleType(label)}
              className={cn(
                'inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[12px] font-medium transition-colors',
                active
                  ? 'border-line bg-card text-ink'
                  : 'border-transparent bg-transparent text-ink-faint',
              )}
            >
              <span
                className="h-2.5 w-2.5 rounded-full"
                style={{ backgroundColor: color, opacity: active ? 1 : 0.35 }}
              />
              {t(nodeLabelKey(label))}
              <span className="tabular-nums text-ink-faint">{counts[label] ?? 0}</span>
            </button>
          )
        })}
      </div>

      <div className="ml-auto inline-flex select-none items-center gap-2 text-[12px] text-ink-soft">
        <span className="text-ink-faint">
          {t('graph.showAllHint', { core: coreCount, total: graph.nodes.length })}
        </span>
        <span className="text-ink">{t('graph.showAll')}</span>
        <Switch
          checked={showAll}
          onCheckedChange={onToggleShowAll}
          aria-label={t('graph.showAll')}
        />
      </div>
    </div>
  )
}
