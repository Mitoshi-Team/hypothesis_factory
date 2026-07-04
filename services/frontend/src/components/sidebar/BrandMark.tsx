import { FlaskConical } from 'lucide-react'

export function BrandMark() {
  return (
    <div className="flex items-center gap-2.5">
      <span className="grid h-8 w-8 place-items-center rounded-lg bg-accent-500 text-white">
        <FlaskConical className="h-[18px] w-[18px]" strokeWidth={2} />
      </span>
      <span className="text-[15px] font-semibold tracking-tight text-ink">Фабрика гипотез</span>
    </div>
  )
}
