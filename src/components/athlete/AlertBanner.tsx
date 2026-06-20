import type { Alert } from '@/types/app.types'

interface Props {
  alert: Alert | null
}

export function AlertBanner({ alert }: Props) {
  if (!alert) return null

  const isCritical = alert.severity === 'critical'

  return (
    <div
      className={`text-xs px-2 py-1 rounded font-medium ${
        isCritical ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'
      }`}
    >
      {isCritical ? '🔴 重要' : '🟡 注意'}
    </div>
  )
}
