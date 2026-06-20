import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'
import type { MealLog } from '@/types/app.types'

const CARB_LABELS: Record<number, string> = {
  1: '主食なし', 2: '少なめ', 3: '普通', 4: '多め', 5: 'かなり多い',
}

interface Props {
  data: MealLog[]
}

export function CarbChart({ data }: Props) {
  const chartData = data
    .filter(d => d.carb_breakfast != null || d.carb_lunch != null || d.carb_dinner != null)
    .map(d => ({
      date: d.log_date.slice(5),
      朝食: d.carb_breakfast ?? null,
      昼食: d.carb_lunch ?? null,
      夕食: d.carb_dinner ?? null,
    }))

  if (chartData.length === 0) {
    return <div className="flex items-center justify-center h-40 text-gray-400 text-sm">データがありません</div>
  }

  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="date" tick={{ fontSize: 11 }} />
        <YAxis domain={[1, 5]} ticks={[1, 2, 3, 4, 5]} tick={{ fontSize: 11 }}
          tickFormatter={v => CARB_LABELS[v] ?? v} width={60} />
        <Tooltip formatter={(v) => CARB_LABELS[v as number] ?? v} />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        <Line type="monotone" dataKey="朝食" stroke="#f59e0b" strokeWidth={2} dot={{ r: 3 }} connectNulls />
        <Line type="monotone" dataKey="昼食" stroke="#10b981" strokeWidth={2} dot={{ r: 3 }} connectNulls />
        <Line type="monotone" dataKey="夕食" stroke="#6366f1" strokeWidth={2} dot={{ r: 3 }} connectNulls />
      </LineChart>
    </ResponsiveContainer>
  )
}
