import {
  ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'
import type { TrainingLog } from '@/types/app.types'
import { TRAINING_TYPES } from '@/constants/alertThresholds'

const TRAINING_LABEL = Object.fromEntries(TRAINING_TYPES.map(t => [t.value, t.label]))

interface Props {
  data: TrainingLog[]
}

export function TrainingDetailChart({ data }: Props) {
  const chartData = data
    .filter(d => d.training_type !== 'rest')
    .map(d => ({
      date: `${d.log_date.slice(5)}(${TRAINING_LABEL[d.training_type] ?? d.training_type})`,
      時間: d.duration_min,
      爆発力: d.explosive_power,
      持久力: d.endurance,
      運動後疲労: d.exercise_fatigue,
    }))

  if (chartData.length === 0) {
    return <div className="flex items-center justify-center h-40 text-gray-400 text-sm">データがありません</div>
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <ComposedChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="date" tick={{ fontSize: 10 }} />
        <YAxis yAxisId="min" orientation="left" tick={{ fontSize: 11 }} unit="分" domain={[0, 'auto']} />
        <YAxis yAxisId="score" orientation="right" domain={[1, 5]} ticks={[1, 2, 3, 4, 5]} tick={{ fontSize: 11 }} />
        <Tooltip />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Bar yAxisId="min" dataKey="時間" fill="#94a3b8" opacity={0.6} radius={[3, 3, 0, 0]} />
        <Line yAxisId="score" type="monotone" dataKey="爆発力" stroke="#f59e0b" strokeWidth={2} dot={{ r: 3 }} connectNulls />
        <Line yAxisId="score" type="monotone" dataKey="持久力" stroke="#10b981" strokeWidth={2} dot={{ r: 3 }} connectNulls />
        <Line yAxisId="score" type="monotone" dataKey="運動後疲労" stroke="#ef4444" strokeWidth={2} dot={{ r: 3 }} connectNulls />
      </ComposedChart>
    </ResponsiveContainer>
  )
}
