import { Link } from 'react-router-dom'
import { Card } from '@/components/ui/Card'
import { AlertBanner } from '@/components/athlete/AlertBanner'
import { TodayStatus } from '@/components/athlete/TodayStatus'
import { SparklineChart } from '@/components/charts/SparklineChart'
import type { AthleteWithStatus } from '@/types/app.types'

interface Props {
  athlete: AthleteWithStatus
}

export function AthleteCard({ athlete }: Props) {
  return (
    <Link to={`/coach/athlete/${athlete.id}`}>
      <Card
        className={`hover:shadow-md transition-shadow cursor-pointer ${
          athlete.latest_alert?.severity === 'critical'
            ? 'border-red-200'
            : athlete.latest_alert?.severity === 'warning'
            ? 'border-yellow-200'
            : ''
        }`}
      >
        <div className="flex items-start justify-between mb-2">
          <div>
            <p className="font-semibold text-gray-800 text-sm">{athlete.full_name}</p>
            <TodayStatus submitted={athlete.submitted_today} />
          </div>
          <AlertBanner alert={athlete.latest_alert} />
        </div>

        <div>
          <p className="text-xs text-gray-500 mb-1">疲労度 (7日間)</p>
          <SparklineChart data={athlete.recent_fatigue} />
        </div>
      </Card>
    </Link>
  )
}
