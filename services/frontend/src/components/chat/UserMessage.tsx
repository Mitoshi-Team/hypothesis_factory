import { Paperclip } from 'lucide-react'

interface Props {
  content: string
  files: string[]
}

export function UserMessage({ content, files }: Props) {
  return (
    <div className="flex flex-col items-end gap-1.5">
      <div className="max-w-[85%] rounded-2xl rounded-br-sm bg-accent-500 px-4 py-2.5 text-[14px] leading-relaxed text-white">
        {content}
      </div>
      {files.length > 0 && (
        <div className="flex max-w-[85%] flex-wrap justify-end gap-1.5">
          {files.map((name) => (
            <span
              key={name}
              className="inline-flex items-center gap-1.5 rounded-lg border border-line bg-card px-2 py-1 text-[12px] text-ink-soft"
            >
              <Paperclip className="h-3 w-3 text-ink-faint" />
              <span className="max-w-[160px] truncate">{name}</span>
            </span>
          ))}
        </div>
      )}
    </div>
  )
}
