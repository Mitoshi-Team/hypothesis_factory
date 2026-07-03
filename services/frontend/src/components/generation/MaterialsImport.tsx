import { Database } from 'lucide-react'
import { FileDropzone } from '@/components/ui/FileDropzone'

interface Props {
  files: string[]
  onFilesChange: (files: string[]) => void
}

export function MaterialsImport({ files, onFilesChange }: Props) {
  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-2">
        <Database className="h-5 w-5 text-brand-600" />
        <h3 className="text-sm font-semibold text-slate-800">
          Структурированные материалы
        </h3>
      </div>
      <p className="text-xs text-slate-500">
        Параметры экспериментов, составы материалов, результаты испытаний
      </p>
      <FileDropzone
        files={files}
        onFilesChange={onFilesChange}
        accept=".xlsx,.xls,.csv,.json,.pdf"
        hint="Excel, CSV, JSON, PDF · до 20 МБ"
      />
    </div>
  )
}
