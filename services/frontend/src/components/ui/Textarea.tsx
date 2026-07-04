import type { TextareaHTMLAttributes } from 'react'
import { cn } from '@/lib/cn'

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
}

export function Textarea({ label, className, id, ...props }: TextareaProps) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label htmlFor={id} className="text-[13px] font-medium text-ink-soft">
          {label}
        </label>
      )}
      <textarea
        id={id}
        className={cn(
          'w-full rounded-lg border border-line bg-panel px-3 py-2 text-sm text-ink',
          'placeholder:text-ink-faint focus:border-ink focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0',
          'resize-y min-h-[96px]',
          className,
        )}
        {...props}
      />
    </div>
  )
}
