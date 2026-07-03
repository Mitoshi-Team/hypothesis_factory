import { Target } from 'lucide-react'
import { Textarea } from '@/components/ui/Textarea'

interface Props {
  problem: string
  constraints: string
  onProblemChange: (value: string) => void
  onConstraintsChange: (value: string) => void
}

export function ProblemInput({
  problem,
  constraints,
  onProblemChange,
  onConstraintsChange,
}: Props) {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-2">
        <Target className="h-5 w-5 text-brand-600" />
        <h3 className="text-sm font-semibold text-slate-800">Технологическая проблема</h3>
      </div>

      <Textarea
        value={problem}
        onChange={(e) => onProblemChange(e.target.value)}
        rows={3}
        placeholder="Например: повысить жаропрочность сплава на 15% без роста себестоимости шихты"
      />

      <Textarea
        label="Ограничения (по одному на строку)"
        value={constraints}
        onChange={(e) => onConstraintsChange(e.target.value)}
        rows={4}
        placeholder={'Доступное сырьё: Ni, Cr, Nb\nБюджет: не более +8% к себестоимости\nОборудование: печи отжига до 1200 °C\nНормативы: ГОСТ 5632-2014'}
      />
    </div>
  )
}
