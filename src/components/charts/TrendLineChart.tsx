import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'
import type { SubjectiveCheck } from '@/types/app.types'

interface Props {
  data: SubjectiveCheck[]
  showFatigueBefore?: boolean
  showFatigueAfter?: boolean
}

export function TrendLineChart({ data, showFatigueBefore = true, showFatigueAfter = true }: Props) {
  const chartData = data.map(d => ({
    date: d.check_date.slice(5),
    '練習前疲労': d.fatigue_before,
    '練習後疲労': d.fatigue_after,
  }))

  if (chartData.length === 0) {
    return <div className="flex items-center justify-center h-40 text-gray-400 text-sm">データがありません</div>
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="date" tick={{ fontSize: 11 }} />
        <YAxis domain={[1, 5]} ticks={[1, 2, 3, 4, 5]} tick={{ fontSize: 11 }} />
        <Tooltip />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        {showFatigueBefore && (
          <Line type="monotone" dataKey="練習前疲労" stroke="#60a5fa" strokeWidth={2} dot={{ r: 3 }} />
        )}
        {showFatigueAfter && (
          <Line type="monotone" dataKey="練習後疲労" stroke="#ef4444" strokeWidth={2} dot={{ r: 3 }} />
        )}
      </LineChart>
    </ResponsiveContainer>
  )
}
