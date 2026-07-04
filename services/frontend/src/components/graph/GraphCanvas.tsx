import { useEffect, useMemo, useRef, useState } from 'react'
import type { KnowledgeGraph } from '@/types'
import { nodeColor } from '@/lib/graph'
import { translate, getLang } from '@/lib/lang'
import { Spinner } from '@/components/ui/Spinner'

// react-force-graph-2d mutates node/link objects (adds x/y, resolves
// source/target to references), so we work with loosely-typed graph objects.
interface FGNode {
  id: string
  label: string
  name: string
  score?: number
  x?: number
  y?: number
  vx?: number
  vy?: number
}
type FGLink = { source: string | FGNode; target: string | FGNode; relation: string; confidence: number }

interface Props {
  graph: KnowledgeGraph
  coreIds: Set<string>
  selectedId: string | null
  /** Node ids highlighted by an active chain (empty = no chain focus). */
  highlightNodes: Set<string>
  /** "src>tgt" keys of edges on the active chain. */
  highlightEdges: Set<string>
  onSelect: (id: string | null) => void
}

const edgeKey = (s: string, t: string) => `${s}>${t}`
const GOLDEN_ANGLE = Math.PI * (3 - Math.sqrt(5))

function nodeId(v: string | FGNode): string {
  return typeof v === 'object' ? v.id : v
}

export function GraphCanvas({
  graph,
  coreIds,
  selectedId,
  highlightNodes,
  highlightEdges,
  onSelect,
}: Props) {
  const wrapRef = useRef<HTMLDivElement>(null)
  const fgRef = useRef<any>(null)
  const [FG, setFG] = useState<any>(null)
  const [size, setSize] = useState({ w: 0, h: 0 })
  const [hoverId, setHoverId] = useState<string | null>(null)

  // Dynamically load the heavy force-graph bundle (kept out of the main chunk).
  useEffect(() => {
    let alive = true
    import('react-force-graph-2d').then((m) => {
      if (alive) setFG(() => m.default)
    })
    return () => {
      alive = false
    }
  }, [])

  // Track container size for an exact canvas fit.
  useEffect(() => {
    const el = wrapRef.current
    if (!el) return
    const ro = new ResizeObserver(() => {
      setSize({ w: el.clientWidth, h: el.clientHeight })
    })
    ro.observe(el)
    setSize({ w: el.clientWidth, h: el.clientHeight })
    return () => ro.disconnect()
  }, [])

  // Node degree (for sizing) from the current edge set.
  const degree = useMemo(() => {
    const d: Record<string, number> = {}
    for (const e of graph.edges) {
      d[e.source] = (d[e.source] ?? 0) + 1
      d[e.target] = (d[e.target] ?? 0) + 1
    }
    return d
  }, [graph.edges])

  const graphKey = useMemo(
    () =>
      [
        graph.nodes.map((n) => n.id).join('|'),
        graph.edges.map((e) => `${e.source}>${e.target}`).join('|'),
      ].join('::'),
    [graph.nodes, graph.edges],
  )

  const data = useMemo(
    () => {
      const isolatedNodes = graph.nodes.filter((n) => (degree[n.id] ?? 0) === 0)
      const isolatedIndex = new Map(isolatedNodes.map((n, index) => [n.id, index]))

      const nodes = graph.nodes.map((n, index) => {
        const isolated = (degree[n.id] ?? 0) === 0
        const isolatedRank = isolatedIndex.get(n.id) ?? index
        const angle = isolated ? isolatedRank * GOLDEN_ANGLE : index * GOLDEN_ANGLE
        const radius = isolated ? 86 + Math.floor(isolatedRank / 12) * 42 : 18
        return {
          id: n.id,
          label: n.label,
          name: n.name,
          score: n.score,
          x: Math.cos(angle) * radius,
          y: Math.sin(angle) * radius,
        }
      }) as FGNode[]

      const links = graph.edges.map((e) => ({
        source: e.source,
        target: e.target,
        relation: e.relation,
        confidence: e.confidence,
      })) as FGLink[]

      return { nodes, links }
    },
    [graphKey, graph.nodes, graph.edges, degree],
  )

  useEffect(() => {
    const fg = fgRef.current
    if (!fg) return

    fg.d3Force?.('charge')?.strength?.((n: FGNode) => ((degree[n.id] ?? 0) === 0 ? -28 : -45))
    fg.d3Force?.('charge')?.distanceMax?.(220)
    fg.d3Force?.('link')?.distance?.(42)
    fg.d3Force?.('link')?.strength?.(0.45)

    const satelliteForce = (alpha: number) => {
      const linkedNodes = data.nodes.filter((n) => (degree[n.id] ?? 0) > 0 && n.x != null && n.y != null)
      const isolatedNodes = data.nodes.filter((n) => (degree[n.id] ?? 0) === 0)
      const anchorNodes = linkedNodes.length > 0 ? linkedNodes : data.nodes
      const cx = anchorNodes.reduce((sum, n) => sum + (n.x ?? 0), 0) / Math.max(anchorNodes.length, 1)
      const cy = anchorNodes.reduce((sum, n) => sum + (n.y ?? 0), 0) / Math.max(anchorNodes.length, 1)

      let coreRadius = 80
      for (const n of anchorNodes) {
        const dx = (n.x ?? cx) - cx
        const dy = (n.y ?? cy) - cy
        coreRadius = Math.max(coreRadius, Math.hypot(dx, dy))
      }

      for (const n of data.nodes) {
        if (n.x == null || n.y == null) continue
        const isolated = (degree[n.id] ?? 0) === 0
        if (!isolated) {
          n.vx = (n.vx ?? 0) - (n.x - cx) * 0.006 * alpha
          n.vy = (n.vy ?? 0) - (n.y - cy) * 0.006 * alpha
          continue
        }

        const rank = isolatedNodes.indexOf(n)
        const ring = Math.floor(rank / 12)
        const angle = rank * GOLDEN_ANGLE
        const radius = coreRadius + 42 + ring * 40
        const tx = cx + Math.cos(angle) * radius
        const ty = cy + Math.sin(angle) * radius

        n.vx = (n.vx ?? 0) + (tx - n.x) * 0.095 * alpha
        n.vy = (n.vy ?? 0) + (ty - n.y) * 0.095 * alpha
      }

      for (let i = 0; i < isolatedNodes.length; i++) {
        const a = isolatedNodes[i]
        if (a.x == null || a.y == null) continue
        for (let j = i + 1; j < isolatedNodes.length; j++) {
          const b = isolatedNodes[j]
          if (b.x == null || b.y == null) continue
          const dx = b.x - a.x
          const dy = b.y - a.y
          const distance = Math.hypot(dx, dy) || 1
          const minDistance = 34
          if (distance >= minDistance) continue
          const push = ((minDistance - distance) / distance) * 0.18 * alpha
          const px = dx * push
          const py = dy * push
          a.vx = (a.vx ?? 0) - px
          a.vy = (a.vy ?? 0) - py
          b.vx = (b.vx ?? 0) + px
          b.vy = (b.vy ?? 0) + py
        }
      }
    }
    satelliteForce.initialize = () => undefined

    fg.d3Force?.('cluster-near-core', null)
    fg.d3Force?.('satellites-around-core', satelliteForce)
    fg.d3ReheatSimulation?.()
  }, [FG, data, degree])

  // Re-heat and fit whenever the visible node set changes.
  useEffect(() => {
    const fg = fgRef.current
    if (!fg || size.w === 0) return
    const id = window.setTimeout(() => fg.zoomToFit?.(400, 60), 350)
    return () => window.clearTimeout(id)
  }, [graphKey, size.w, size.h])

  const showLabels = data.links.length <= 60
  const focusing = highlightNodes.size > 0

  if (!FG) {
    return (
      <div ref={wrapRef} className="grid h-full w-full place-items-center">
        <Spinner className="h-6 w-6 text-ink-faint" />
      </div>
    )
  }

  return (
    <div ref={wrapRef} className="h-full w-full">
      <FG
        ref={fgRef}
        width={size.w}
        height={size.h}
        graphData={data}
        backgroundColor="#FFFFFF"
        cooldownTicks={120}
        d3VelocityDecay={0.3}
        nodeRelSize={5}
        nodeVal={(n: FGNode) => 1 + (degree[n.id] ?? 0) * 1.5 + (n.score ?? 0.5)}
        onNodeHover={(n: FGNode | null) => setHoverId(n?.id ?? null)}
        onNodeClick={(n: FGNode) => onSelect(n.id)}
        onBackgroundClick={() => onSelect(null)}
        linkColor={(l: FGLink) => {
          const s = nodeId(l.source)
          const t = nodeId(l.target)
          const on = highlightEdges.has(edgeKey(s, t))
          if (focusing && !on) return 'rgba(154,160,166,0.15)'
          return on ? '#1F57D6' : 'rgba(99,102,107,0.35)'
        }}
        linkWidth={(l: FGLink) => {
          const s = nodeId(l.source)
          const t = nodeId(l.target)
          return highlightEdges.has(edgeKey(s, t)) ? 2.5 : 0.6 + l.confidence
        }}
        linkDirectionalArrowLength={4}
        linkDirectionalArrowRelPos={1}
        linkCanvasObjectMode={() => (showLabels ? 'after' : undefined)}
        linkCanvasObject={(l: FGLink, ctx: CanvasRenderingContext2D, scale: number) => {
          if (!showLabels || scale < 1.4) return
          const s = l.source as FGNode
          const t = l.target as FGNode
          if (s.x == null || t.x == null) return
          const on = highlightEdges.has(edgeKey(s.id, t.id))
          if (focusing && !on) return
          const label = translate(getLang(), `graph.rel.${l.relation}`)
          const mx = (s.x + t.x!) / 2
          const my = (s.y! + t.y!) / 2
          const fs = 3.2
          ctx.font = `${fs}px "IBM Plex Sans", sans-serif`
          const w = ctx.measureText(label).width
          ctx.fillStyle = 'rgba(255,255,255,0.85)'
          ctx.fillRect(mx - w / 2 - 1, my - fs / 2 - 0.5, w + 2, fs + 1)
          ctx.textAlign = 'center'
          ctx.textBaseline = 'middle'
          ctx.fillStyle = on ? '#1F57D6' : '#9AA0A6'
          ctx.fillText(label, mx, my)
        }}
        nodeCanvasObject={(n: FGNode, ctx: CanvasRenderingContext2D, scale: number) => {
          if (n.x == null || n.y == null) return
          const r = Math.max(2.5, 2 + (degree[n.id] ?? 0) * 1.1 + (n.score ?? 0.5) * 2)
          const isCore = coreIds.has(n.id)
          const selected = n.id === selectedId
          const hovered = n.id === hoverId
          const isolated = (degree[n.id] ?? 0) === 0
          const dim =
            (focusing && !highlightNodes.has(n.id)) ||
            (isolated && !selected && !hovered)

          ctx.globalAlpha = dim ? 0.28 : 1
          ctx.beginPath()
          ctx.arc(n.x, n.y, r, 0, 2 * Math.PI)
          ctx.fillStyle = nodeColor(n.label)
          ctx.fill()

          if (selected || hovered || highlightNodes.has(n.id)) {
            ctx.globalAlpha = 1
            ctx.lineWidth = selected ? 1.6 : 1
            ctx.strokeStyle = selected ? '#1A47B4' : '#1F57D6'
            ctx.stroke()
          }

          // Labels: draw for core/selected/hovered, or everyone when zoomed in.
          const wantLabel = selected || hovered || (isCore && scale > 1) || scale > 2.4
          if (wantLabel && n.name) {
            ctx.globalAlpha = dim ? 0.5 : 1
            const fs = Math.max(3, 4 / Math.sqrt(scale)) * scale
            ctx.font = `${selected || isCore ? 600 : 400} ${fs / scale}px "IBM Plex Sans", sans-serif`
            ctx.textAlign = 'center'
            ctx.textBaseline = 'top'
            ctx.fillStyle = '#1C1D1F'
            const text = n.name.length > 28 ? n.name.slice(0, 27) + '…' : n.name
            ctx.fillText(text, n.x, n.y + r + 1)
          }
          ctx.globalAlpha = 1
        }}
        nodePointerAreaPaint={(n: FGNode, color: string, ctx: CanvasRenderingContext2D) => {
          if (n.x == null || n.y == null) return
          const r = Math.max(3, 2 + (degree[n.id] ?? 0) * 1.1 + (n.score ?? 0.5) * 2) + 2
          ctx.fillStyle = color
          ctx.beginPath()
          ctx.arc(n.x, n.y, r, 0, 2 * Math.PI)
          ctx.fill()
        }}
      />
    </div>
  )
}
