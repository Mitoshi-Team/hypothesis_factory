import { useState } from 'react'
import { FileText, FileType } from 'lucide-react'
import type { BusinessReport } from '@/types'
import { Button } from '@/components/ui/Button'
import { Spinner } from '@/components/ui/Spinner'

export function ReportActions({ report }: { report: BusinessReport }) {
  const [busy, setBusy] = useState<null | 'pdf' | 'docx'>(null)

  const handlePdf = async () => {
    setBusy('pdf')
    try {
      const { exportReportToPdf } = await import('@/lib/export')
      await exportReportToPdf(report)
    } finally {
      setBusy(null)
    }
  }

  const handleDocx = async () => {
    setBusy('docx')
    try {
      const { exportReportToDocx } = await import('@/lib/export')
      await exportReportToDocx(report)
    } finally {
      setBusy(null)
    }
  }

  return (
    <div className="flex gap-2">
      <Button variant="secondary" onClick={handlePdf} disabled={busy !== null}>
        {busy === 'pdf' ? <Spinner className="h-4 w-4" /> : <FileText className="h-4 w-4" />}
        Скачать PDF
      </Button>
      <Button variant="secondary" onClick={handleDocx} disabled={busy !== null}>
        {busy === 'docx' ? <Spinner className="h-4 w-4" /> : <FileType className="h-4 w-4" />}
        Скачать DOCX
      </Button>
    </div>
  )
}
