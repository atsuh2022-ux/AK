import { useAlerts } from '@/hooks/useAlerts'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'

export function AlertList() {
  const { alerts, acknowledge } = useAlerts()

  if (alerts.length === 0) {
    return (
      <div className="text-center py-6 text-gray-400 text-sm">
        アクティブなアラートはありません ✓
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {alerts.map(alert => (
        <div
          key={alert.id}
          className={`flex items-start justify-between p-3 rounded-lg border ${
            alert.severity === 'critical'
              ? 'bg-red-50 border-red-200'
              : 'bg-yellow-50 border-yellow-200'
          }`}
        >
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-0.5">
              <p className="font-medium text-sm text-gray-800">
                {(alert as { profiles?: { full_name: string } }).profiles?.full_name ?? '不明'}
              </p>
              <Badge variant={alert.severity === 'critical' ? 'critical' : 'warning'}>
                {alert.severity === 'critical' ? '重要' : '注意'}
              </Badge>
            </div>
            <p className="text-xs text-gray-600">{alert.message}</p>
            <p className="text-xs text-gray-400 mt-0.5">{alert.alert_date}</p>
          </div>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => acknowledge(alert.id)}
            className="shrink-0 ml-2 text-xs"
          >
            確認済み
          </Button>
        </div>
      ))}
    </div>
  )
}
