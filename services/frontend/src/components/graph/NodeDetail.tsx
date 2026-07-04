import { X } from 'lucide-react'
import type { GraphNode } from '@/types'
import { useI18n } from '@/lib/i18n'
import { nodeColor, nodeLabelKey } from '@/lib/graph'

interface Props {
  node: GraphNode
  onClose: () => void
}

/** Right-hand panel with the selected entity's type, score and source passages. */
export function NodeDetail({ node, onClose }: Props) {
  const { t } = useI18n()
  const color = nodeColor(node.label)

  return (
    <div className="flex h-full w-full flex-col overflow-hidden">
      <div className="flex items-start justify-between gap-2 border-b border-line px-4 py-3">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span
              className="inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-[11px] font-medium"
              style={{ backgroundColor: `${color}1A`, color }}
            >
              <span className="h-2 w-2 rounded-full" style={{ backgroundColor: color }} />
              {t(nodeLabelKey(node.label))}
            </span>
            {node.score != null && (
              <span className="text-[11px] tabular-nums text-ink-faint">
                {t('graph.score')} {node.score.toFixed(2)}
              </span>
            )}
          </div>
          <h3 className="mt-1.5 break-words text-[15px] font-semibold leading-snug text-ink">
            {node.name}
          </h3>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="-mr-1 shrink-0 rounded-lg p-1.5 text-ink-faint hover:bg-panel hover:text-ink"
          aria-label={t('graph.close')}
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto scroll-slim px-4 py-3">
        <span className="text-xs font-medium text-ink-faint">
          {t('graph.sources')} · {node.sourceChunks.length}
        </span>
        {node.sourceChunks.length === 0 ? (
          <p className="mt-2 text-[13px] text-ink-soft">{t('graph.noSources')}</p>
        ) : (
          <ul className="mt-2 flex flex-col gap-3">
            {node.sourceChunks.map((c, i) => (
              <li key={c.chunkId || i} className="rounded-xl border border-line bg-panel p-3">
                {(c.documentTitle || c.sectionPath) && (
                  <p className="mb-1.5 text-[12px] font-medium text-ink">
                    {c.documentTitle}
                    {c.sectionPath && (
                      <span className="font-normal text-ink-faint"> · {c.sectionPath}</span>
                    )}
                  </p>
                )}
                <p className="text-[13px] leading-relaxed text-ink-soft">{c.text}</p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
