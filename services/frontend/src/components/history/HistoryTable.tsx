import { useState } from 'react'
import { Download, FileText, FileType } from 'lucide-react'
import type { HistoryEntry } from '@/types'
import { Card } from '@/components/ui/Card'
import { formatDate } from '@/lib/format'
import { getReport } from '@/lib/api'

export function HistoryTable({ entries }: { entries: HistoryEntry[] }) {
  const [downloading, setDownloading] = useState<string | null>(null)

  const download = async (reportId: string, format: 'pdf' | 'docx') => {
    setDownloading(`${reportId}:${format}`)
    try {
      const report = await getReport(reportId)
      const { exportReportToDocx, exportReportToPdf } = await import('@/lib/export')
      if (format === 'pdf') await exportReportToPdf(report)
      else await exportReportToDocx(report)
    } finally {
      setDownloading(null)
    }
  }

  if (entries.length === 0) {
    return (
      <Card className="p-12 text-center text-sm text-slate-400">
        История пуста — сгенерируйте первый отчёт.
      </Card>
    )
  }

  return (
    <Card className="overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
              <th className="px-5 py-3 font-semibold">Дата генерации</th>
              <th className="px-5 py-3 font-semibold">Технологическая проблема</th>
              <th className="px-5 py-3 font-semibold">Гипотезы</th>
              <th className="px-5 py-3 text-right font-semibold">Скачать отчёт</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {entries.map((entry) => (
              <tr key={entry.id} className="hover:bg-slate-50">
                <td className="whitespace-nowrap px-5 py-4 text-slate-500">
                  {formatDate(entry.createdAt)}
                </td>
                <td className="px-5 py-4 font-medium text-slate-800">{entry.problem}</td>
                <td className="px-5 py-4">
                  <span className="font-mono tabular-nums text-slate-700">
                    {entry.hypothesisCount}
                  </span>
                </td>
                <td className="px-5 py-4">
                  <div className="flex items-center justify-end gap-2">
                    <button
                      type="button"
                      onClick={() => download(entry.reportId, 'pdf')}
                      disabled={downloading !== null}
                      className="inline-flex items-center gap-1.5 rounded-md border border-slate-200 px-2.5 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-100 disabled:opacity-50"
                    >
                      {downloading === `${entry.reportId}:pdf` ? (
                        <Download className="h-3.5 w-3.5 animate-bounce" />
                      ) : (
                        <FileText className="h-3.5 w-3.5" />
                      )}
                      PDF
                    </button>
                    <button
                      type="button"
                      onClick={() => download(entry.reportId, 'docx')}
                      disabled={downloading !== null}
                      className="inline-flex items-center gap-1.5 rounded-md border border-slate-200 px-2.5 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-100 disabled:opacity-50"
                    >
                      {downloading === `${entry.reportId}:docx` ? (
                        <Download className="h-3.5 w-3.5 animate-bounce" />
                      ) : (
                        <FileType className="h-3.5 w-3.5" />
                      )}
                      DOCX
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  )
}
