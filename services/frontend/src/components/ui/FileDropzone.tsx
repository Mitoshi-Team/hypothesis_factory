import { useRef, useState } from 'react'
import { FileUp, X } from 'lucide-react'
import { cn } from '@/lib/cn'
import { useI18n } from '@/lib/i18n'

interface FileDropzoneProps {
  files: File[]
  onFilesChange: (files: File[]) => void
  accept?: string
  hint?: string
}

export function FileDropzone({ files, onFilesChange, accept, hint }: FileDropzoneProps) {
  const { t } = useI18n()
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)

  const addFiles = (list: FileList | null) => {
    if (!list) return
    const existing = new Set(files.map((f) => f.name))
    const added = Array.from(list).filter((f) => !existing.has(f.name))
    if (added.length > 0) onFilesChange([...files, ...added])
  }

  const removeFile = (name: string) => {
    onFilesChange(files.filter((f) => f.name !== name))
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
          'flex w-full flex-col items-center justify-center gap-2 rounded-xl border border-dashed px-4 py-7 text-center transition-all duration-200 ease-out active:scale-[0.99]',
          dragging
            ? 'scale-[1.01] border-accent-200 bg-accent-50'
            : 'border-line-strong bg-panel hover:border-accent-200 hover:bg-accent-50/60',
        )}
      >
        <FileUp
          className={cn(
            'h-5 w-5 text-accent-500 transition-transform duration-200 ease-out',
            dragging && '-translate-y-0.5',
          )}
        />
        <span className="text-sm font-medium text-ink">
          {t('dropzone.prompt')}
        </span>
        {hint && <span className="text-xs text-ink-faint">{hint}</span>}
      </button>

      <input
        ref={inputRef}
        type="file"
        multiple
        accept={accept}
        className="hidden"
        onChange={(e) => {
          addFiles(e.target.files)
          // Allow re-selecting the same file after removal.
          e.target.value = ''
        }}
      />

      {files.length > 0 && (
        <ul className="flex flex-wrap gap-2">
          {files.map((file) => (
            <li
              key={file.name}
              className="inline-flex animate-fade-up items-center gap-1.5 rounded-lg border border-line bg-card py-1 pl-2.5 pr-1.5 text-xs text-ink-soft"
            >
              <span className="max-w-[180px] truncate">{file.name}</span>
              <button
                type="button"
                onClick={() => removeFile(file.name)}
                className="grid h-5 w-5 place-items-center rounded-md text-ink-faint transition-colors duration-150 hover:bg-red-50 hover:text-red-500"
                aria-label={t('dropzone.remove', { name: file.name })}
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
