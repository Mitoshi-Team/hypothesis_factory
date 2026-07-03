import { useState } from 'react'
import { RotateCcw } from 'lucide-react'
import type { BusinessReport as Report, GenerationInput } from '@/types'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { ProblemInput } from '@/components/generation/ProblemInput'
import {
  KnowledgeBaseInput,
  type KnowledgeBase,
} from '@/components/generation/KnowledgeBaseInput'
import { MaterialsImport } from '@/components/generation/MaterialsImport'
import { GenerateButton } from '@/components/generation/GenerateButton'
import { GenerationLoader } from '@/components/loading/GenerationLoader'
import { BusinessReport } from '@/components/report/BusinessReport'
import { generateHypotheses } from '@/lib/api'

type Phase = 'idle' | 'generating' | 'done'

const EMPTY_KB: KnowledgeBase = { articles: '', patents: '', reports: '' }

export function MainPage() {
  const [phase, setPhase] = useState<Phase>('idle')
  const [report, setReport] = useState<Report | null>(null)

  const [problem, setProblem] = useState('')
  const [constraints, setConstraints] = useState('')
  const [knowledgeBase, setKnowledgeBase] = useState<KnowledgeBase>(EMPTY_KB)
  const [materials, setMaterials] = useState<string[]>([])

  const canGenerate = problem.trim().length > 0

  const handleGenerate = async () => {
    setPhase('generating')
    const input: GenerationInput = {
      problem,
      constraints,
      knowledgeBase,
      materials,
    }
    const result = await generateHypotheses(input)
    setReport(result)
    setPhase('done')
  }

  const handleReset = () => {
    setPhase('idle')
    setReport(null)
  }

  if (phase === 'generating') {
    return <GenerationLoader />
  }

  if (phase === 'done' && report) {
    return (
      <div className="flex flex-col gap-6">
        <Button variant="ghost" onClick={handleReset} className="self-start">
          <RotateCcw className="h-4 w-4" />
          Новая генерация
        </Button>
        <BusinessReport report={report} />
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-slate-900">Генерация гипотез</h1>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="p-6">
          <ProblemInput
            problem={problem}
            constraints={constraints}
            onProblemChange={setProblem}
            onConstraintsChange={setConstraints}
          />
        </Card>

        <Card className="p-6">
          <KnowledgeBaseInput value={knowledgeBase} onChange={setKnowledgeBase} />
        </Card>

        <Card className="p-6 lg:col-span-2">
          <MaterialsImport files={materials} onFilesChange={setMaterials} />
        </Card>
      </div>

      <div className="mx-auto w-full max-w-md">
        <GenerateButton disabled={!canGenerate} onClick={handleGenerate} />
        {!canGenerate && (
          <p className="mt-2 text-center text-xs text-slate-400">
            Введите технологическую проблему, чтобы начать
          </p>
        )}
      </div>
    </div>
  )
}
