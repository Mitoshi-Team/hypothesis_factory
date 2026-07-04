import { useEffect, useState } from 'react'
import { FileText, FileType, X } from 'lucide-react'
import type { HypothesisResult } from '@/types'
import { useI18n } from '@/lib/i18n'
import { Spinner } from '@/components/ui/Spinner'

interface SaveModalProps {
  result: HypothesisResult
  onClose: () => void
}

const FORMATS = [
  { key: 'pdf' as const, label: 'PDF', icon: FileText, hintKey: 'save.pdfHint' },
  { key: 'docx' as const, label: 'DOCX', icon: FileType, hintKey: 'save.docxHint' },
]

export function SaveModal({ result, onClose }: SaveModalProps) {
  const { t } = useI18n()
  const [busy, setBusy] = useState<null | 'pdf' | 'docx'>(null)

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const save = async (format: 'pdf' | 'docx') => {
    setBusy(format)
    try {
      const { exportResultToPdf, exportResultToDocx } = await import('@/lib/export')
      if (format === 'pdf') await exportResultToPdf(result)
      else await exportResultToDocx(result)
      onClose()
    } finally {
      setBusy(null)
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center p-4 sm:items-center"
      role="dialog"
      aria-modal="true"
      aria-label={t('save.title')}
    >
      <div className="absolute inset-0 bg-ink/25 animate-fade-in" onClick={onClose} />

      <div className="relative w-full max-w-sm rounded-2xl border border-line bg-card p-5 shadow-pop animate-fade-up">
        <div className="mb-1 flex items-start justify-between">
          <div>
            <h2 className="text-[15px] font-semibold text-ink">{t('save.title')}</h2>
            <p className="mt-0.5 text-[13px] text-ink-soft">{t('save.chooseFormat')}</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="-mr-1 -mt-1 rounded-lg p-1.5 text-ink-faint hover:bg-panel hover:text-ink"
            aria-label={t('save.close')}
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="mt-4 flex flex-col gap-2">
          {FORMATS.map(({ key, label, icon: Icon, hintKey }) => (
            <button
              key={key}
              type="button"
              onClick={() => save(key)}
              disabled={busy !== null}
              className="group flex items-center gap-3 rounded-xl border border-line bg-panel px-3.5 py-3 text-left transition-colors hover:border-accent-200 hover:bg-accent-50 disabled:opacity-60"
            >
              <span className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-panel text-accent-600 group-hover:bg-card">
                {busy === key ? <Spinner className="h-4 w-4" /> : <Icon className="h-[18px] w-[18px]" />}
              </span>
              <span className="min-w-0 flex-1">
                <span className="block text-sm font-semibold text-ink">{label}</span>
                <span className="block text-xs text-ink-soft">{t(hintKey)}</span>
              </span>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
