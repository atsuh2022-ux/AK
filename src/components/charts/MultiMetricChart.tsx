import {
  ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'
import type { PhysicalCheck } from '@/types/app.types'

interface Props {
  data: PhysicalCheck[]
  showWeight?: boolean
  showBodyFat?: boolean
  showHeartRate?: boolean
}

export function MultiMetricChart({ data, showWeight = true, showBodyFat = true, showHeartRate = true }: Props) {
  const chartData = data
    .filter(d => d.weight_kg !== null || d.body_fat_pct !== null)
    .map(d => ({
      date: d.check_date.slice(5),
      体重: d.weight_kg,
      体脂肪率: d.body_fat_pct,
      安静時心拍: d.resting_heart_rate,
    }))

  if (chartData.length === 0) {
    return <div className="flex items-center justify-center h-40 text-gray-400 text-sm">データがありません</div>
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <ComposedChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="date" tick={{ fontSize: 11 }} />
        <YAxis yAxisId="weight" orientation="left" tick={{ fontSize: 11 }} unit="kg" domain={['auto', 'auto']} />
        <YAxis yAxisId="hr" orientation="right" tick={{ fontSize: 11 }} unit="bpm" domain={['auto', 'auto']} />
        <Tooltip />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        {showWeight && (
          <Line yAxisId="weight" type="monotone" dataKey="体重" stroke="#8b5cf6" strokeWidth={2} dot={{ r: 3 }} />
        )}
        {showBodyFat && (
          <Line yAxisId="weight" type="monotone" dataKey="体脂肪率" stroke="#10b981" strokeWidth={2} dot={{ r: 3 }} strokeDasharray="4 2" />
        )}
        {showHeartRate && (
          <Bar yAxisId="hr" dataKey="安静時心拍" fill="#f97316" opacity={0.6} radius={[2, 2, 0, 0]} />
        )}
      </ComposedChart>
    </ResponsiveContainer>
  )
}
