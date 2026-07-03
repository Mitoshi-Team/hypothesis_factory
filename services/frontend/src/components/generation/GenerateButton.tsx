import { Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/Button'

interface Props {
  disabled: boolean
  onClick: () => void
}

export function GenerateButton({ disabled, onClick }: Props) {
  return (
    <Button size="lg" onClick={onClick} disabled={disabled} className="w-full">
      <Sparkles className="h-5 w-5" />
      Сгенерировать гипотезы
    </Button>
  )
}
