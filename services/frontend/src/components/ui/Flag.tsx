import { cn } from '@/lib/cn'
import type { Lang } from '@/lib/lang'

interface Props {
  lang: Lang
  className?: string
}

/**
 * Small rounded flag chip. Renders the SVG flag icon from
 * `public/flags/<lang>.svg`. Default size ~22×15; override via className.
 */
export function Flag({ lang, className }: Props) {
  return (
    <span
      className={cn(
        'inline-block h-[15px] w-[22px] shrink-0 overflow-hidden rounded-[3px] ring-1 ring-black/10',
        className,
      )}
      aria-hidden="true"
    >
      <img src={`/flags/${lang}.svg`} alt="" className="h-full w-full object-cover" />
    </span>
  )
}
