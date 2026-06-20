import {
  ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'
import type { SubjectiveCheck } from '@/types/app.types'

interface Props {
  data: SubjectiveCheck[]
}

export function SleepChart({ data }: Props) {
  const chartData = data.map(d => ({
    date: d.check_date.slice(5),
    睡眠時間: d.sleep_hours,
    睡眠の質: d.sleep_quality,
  }))

  if (chartData.length === 0) {
    return <div className="flex items-center justify-center h-40 text-gray-400 text-sm">データがありません</div>
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <ComposedChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="date" tick={{ fontSize: 11 }} />
        <YAxis yAxisId="hours" orientation="left" tick={{ fontSize: 11 }} unit="h" domain={[0, 12]} />
        <YAxis yAxisId="quality" orientation="right" domain={[1, 5]} ticks={[1, 2, 3, 4, 5]} tick={{ fontSize: 11 }} />
        <Tooltip formatter={(v, name) => name === '睡眠時間' ? [`${v}時間`, name] : [`${v} / 5`, name]} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Bar yAxisId="hours" dataKey="睡眠時間" fill="#818cf8" opacity={0.7} radius={[3, 3, 0, 0]} />
        <Line yAxisId="quality" type="monotone" dataKey="睡眠の質" stroke="#f43f5e" strokeWidth={2} dot={{ r: 3 }} />
      </ComposedChart>
    </ResponsiveContainer>
  )
}
