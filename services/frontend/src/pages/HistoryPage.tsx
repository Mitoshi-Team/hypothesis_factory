import { useEffect, useState } from 'react'
import type { HistoryEntry } from '@/types'
import { HistoryTable } from '@/components/history/HistoryTable'
import { Spinner } from '@/components/ui/Spinner'
import { getHistory } from '@/lib/api'

export function HistoryPage() {
  const [entries, setEntries] = useState<HistoryEntry[] | null>(null)

  useEffect(() => {
    let mounted = true
    getHistory().then((data) => {
      if (mounted) setEntries(data)
    })
    return () => {
      mounted = false
    }
  }, [])

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-bold text-slate-900">История отчётов</h1>

      {entries === null ? (
        <div className="flex items-center justify-center gap-2 py-16 text-slate-400">
          <Spinner className="h-5 w-5" />
          Загрузка истории…
        </div>
      ) : (
        <HistoryTable entries={entries} />
      )}
    </div>
  )
}
