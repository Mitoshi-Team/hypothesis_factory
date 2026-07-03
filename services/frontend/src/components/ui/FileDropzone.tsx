import { useRef, useState } from 'react'
import { FileUp, X } from 'lucide-react'
import { cn } from '@/lib/cn'

interface FileDropzoneProps {
  files: string[]
  onFilesChange: (files: string[]) => void
  accept?: string
  hint?: string
}

export function FileDropzone({ files, onFilesChange, accept, hint }: FileDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)

  const addFiles = (list: FileList | null) => {
    if (!list) return
    const names = Array.from(list).map((f) => f.name)
    onFilesChange([...new Set([...files, ...names])])
  }

  const removeFile = (name: string) => {
    onFilesChange(files.filter((f) => f !== name))
  }

  return (
    <div className="flex flex-col gap-2">
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault()
          setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragging(false)
          addFiles(e.dataTransfer.files)
        }}
        className={cn(
          'flex w-full flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed px-4 py-8 text-center transition-colors',
          dragging
            ? 'border-brand-400 bg-brand-50'
            : 'border-slate-300 bg-slate-50 hover:border-brand-300 hover:bg-brand-50/50',
        )}
      >
        <FileUp className="h-6 w-6 text-brand-500" />
        <span className="text-sm font-medium text-slate-700">
          Перетащите файлы или нажмите для выбора
        </span>
        {hint && <span className="text-xs text-slate-400">{hint}</span>}
      </button>

      <input
        ref={inputRef}
        type="file"
        multiple
        accept={accept}
        className="hidden"
        onChange={(e) => addFiles(e.target.files)}
      />

      {files.length > 0 && (
        <ul className="flex flex-wrap gap-2">
          {files.map((name) => (
            <li
              key={name}
              className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-2.5 py-1 text-xs text-slate-700"
            >
              <span className="max-w-[180px] truncate">{name}</span>
              <button
                type="button"
                onClick={() => removeFile(name)}
                className="text-slate-400 hover:text-red-500"
                aria-label={`Удалить ${name}`}
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
