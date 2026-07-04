import { useId } from 'react'
import { cn } from '@/lib/cn'
import type { Lang } from '@/lib/lang'

/** Path for a 5-point star centred at (cx,cy), outer radius r, rotation in deg. */
function star(cx: number, cy: number, r: number, rot = 0): string {
  const inner = r * 0.382
  const pts: string[] = []
  for (let i = 0; i < 10; i++) {
    const rad = ((rot - 90 + i * 36) * Math.PI) / 180
    const rr = i % 2 === 0 ? r : inner
    pts.push(`${(cx + rr * Math.cos(rad)).toFixed(2)},${(cy + rr * Math.sin(rad)).toFixed(2)}`)
  }
  return `M${pts.join('L')}Z`
}

function RuFlag() {
  return (
    <svg viewBox="0 0 9 6" width="100%" height="100%" preserveAspectRatio="xMidYMid slice">
      <rect width="9" height="6" fill="#fff" />
      <rect y="2" width="9" height="2" fill="#0039A6" />
      <rect y="4" width="9" height="2" fill="#D52B1E" />
    </svg>
  )
}

function ZhFlag() {
  const gold = '#FFDE00'
  return (
    <svg viewBox="0 0 30 20" width="100%" height="100%" preserveAspectRatio="xMidYMid slice">
      <rect width="30" height="20" fill="#EE1C25" />
      <path d={star(5, 5, 3.2, 0)} fill={gold} />
      <path d={star(10, 2, 1.1, 20)} fill={gold} />
      <path d={star(12, 4.5, 1.1, -5)} fill={gold} />
      <path d={star(12, 8, 1.1, 15)} fill={gold} />
      <path d={star(10, 10.5, 1.1, 40)} fill={gold} />
    </svg>
  )
}

function EnFlag() {
  const uid = useId().replace(/:/g, '')
  const s = `s-${uid}`
  const t = `t-${uid}`
  return (
    <svg viewBox="0 0 60 30" width="100%" height="100%" preserveAspectRatio="xMidYMid slice">
      <clipPath id={s}>
        <path d="M0,0 v30 h60 v-30 z" />
      </clipPath>
      <clipPath id={t}>
        <path d="M30,15 h30 v15 z v-30 h-30 z M0,0 h30 v30 h-30 z" />
      </clipPath>
      <g clipPath={`url(#${s})`}>
        <path d="M0,0 v30 h60 v-30 z" fill="#012169" />
        <path d="M0,0 L60,30 M60,0 L0,30" stroke="#fff" strokeWidth="6" />
        <path d="M0,0 L60,30 M60,0 L0,30" clipPath={`url(#${t})`} stroke="#C8102E" strokeWidth="4" />
        <path d="M30,0 v30 M0,15 h60" stroke="#fff" strokeWidth="10" />
        <path d="M30,0 v30 M0,15 h60" stroke="#C8102E" strokeWidth="6" />
      </g>
    </svg>
  )
}

const FLAGS: Record<Lang, () => JSX.Element> = {
  ru: RuFlag,
  en: EnFlag,
  zh: ZhFlag,
}

interface Props {
  lang: Lang
  className?: string
}

/** Small rounded flag chip. Default size ~24×16; override via className. */
export function Flag({ lang, className }: Props) {
  const Svg = FLAGS[lang]
  return (
    <span
      className={cn(
        'inline-block h-4 w-[22px] shrink-0 overflow-hidden rounded-[3px] ring-1 ring-black/10',
        className,
      )}
      aria-hidden="true"
    >
      <Svg />
    </span>
  )
}
