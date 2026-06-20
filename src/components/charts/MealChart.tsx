import {
  ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from 'recharts'
import type { MealLog } from '@/types/app.types'

interface Props {
  data: MealLog[]
  showAppetite?: boolean
  showNutritionBalance?: boolean
  showMealCount?: boolean
  showWaterMl?: boolean
}

export function MealChart({
  data,
  showAppetite = true,
  showNutritionBalance = true,
  showMealCount = true,
  showWaterMl = true,
}: Props) {
  const chartData = data.map(d => ({
    date: d.log_date.slice(5),
    食欲: d.appetite,
    栄養バランス: d.nutrition_balance,
    食事回数: d.meal_count,
    水分: d.water_ml ? Math.round(d.water_ml / 100) / 10 : null,
  }))

  if (chartData.length === 0) {
    return <div className="flex items-center justify-center h-40 text-gray-400 text-sm">データがありません</div>
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <ComposedChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey="date" tick={{ fontSize: 11 }} />
        <YAxis yAxisId="score" domain={[1, 5]} ticks={[1, 2, 3, 4, 5]} tick={{ fontSize: 11 }} />
        <YAxis yAxisId="water" orientation="right" tick={{ fontSize: 11 }} unit="L" domain={[0, 4]} />
        <Tooltip />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        {showAppetite && (
          <Bar yAxisId="score" dataKey="食欲" fill="#f97316" opacity={0.7} radius={[2, 2, 0, 0]} />
        )}
        {showNutritionBalance && (
          <Line yAxisId="score" type="monotone" dataKey="栄養バランス" stroke="#10b981" strokeWidth={2} dot={{ r: 3 }} />
        )}
        {showMealCount && (
          <Line yAxisId="score" type="monotone" dataKey="食事回数" stroke="#a855f7" strokeWidth={2} dot={{ r: 3 }} strokeDasharray="4 2" />
        )}
        {showWaterMl && (
          <Line yAxisId="water" type="monotone" dataKey="水分" stroke="#3b82f6" strokeWidth={2} dot={{ r: 3 }} strokeDasharray="4 2" />
        )}
      </ComposedChart>
    </ResponsiveContainer>
  )
}
