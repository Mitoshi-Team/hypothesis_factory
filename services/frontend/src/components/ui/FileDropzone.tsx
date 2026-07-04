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
          'flex w-full flex-col items-center justify-center gap-2 rounded-xl border border-dashed px-4 py-7 text-center transition-colors',
          dragging
            ? 'border-accent-200 bg-accent-50'
            : 'border-line-strong bg-bg hover:border-accent-200 hover:bg-accent-50/60',
        )}
      >
        <FileUp className="h-5 w-5 text-accent-500" />
        <span className="text-sm font-medium text-ink">
          Перетащите файлы или нажмите для выбора
        </span>
        {hint && <span className="text-xs text-ink-faint">{hint}</span>}
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
              className="inline-flex items-center gap-1.5 rounded-lg border border-line bg-card px-2.5 py-1 text-xs text-ink-soft"
            >
              <span className="max-w-[180px] truncate">{name}</span>
              <button
                type="button"
                onClick={() => removeFile(name)}
                className="text-ink-faint hover:text-red-500"
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
