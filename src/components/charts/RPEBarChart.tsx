import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import type { TrainingLog } from '@/types/app.types'
import { TRAINING_TYPES } from '@/constants/alertThresholds'

interface Props {
  data: TrainingLog[]
}

const TRAINING_LABEL = Object.fromEntries(TRAINING_TYPES.map(t => [t.value, t.label]))

function rpeColor(rpe: number) {
  if (rpe <= 3) return '#10b981'
  if (rpe <= 6) return '#f59e0b'
  if (rpe <= 8) return '#f97316'
  return '#ef4444'
}

export function RPEBarChart({ data }: Props) {
  const chartData = data.map(d => ({
    date: d.log_date.slice(5),
    RPE: d.rpe,
    種目: TRAINING_LABEL[d.training_type] ?? d.training_type,
  }))

  if (chartData.length === 0) {
    return <div className="flex items-center justify-center h-40 text-gray-400 text-sm">データがありません</div>
  }

  return (
    <ResponsiveContainer width="100%" height={180}>
      <BarChart data={chartData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" vertical={false} />
        <XAxis dataKey="date" tick={{ fontSize: 11 }} />
        <YAxis domain={[0, 10]} ticks={[0, 2, 4, 6, 8, 10]} tick={{ fontSize: 11 }} />
        <Tooltip
          formatter={(v, _n, props) => [`RPE ${v} - ${props.payload.種目}`, '']}
        />
        <Bar dataKey="RPE" radius={[3, 3, 0, 0]}>
          {chartData.map((entry, i) => (
            <Cell key={i} fill={rpeColor(entry.RPE)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
