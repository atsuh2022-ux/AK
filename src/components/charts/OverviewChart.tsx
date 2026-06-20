import {
  ComposedChart,
  Line,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts'
import type { SubjectiveCheck, PhysicalCheck, MealLog, TrainingLog } from '@/types/app.types'
import { TRAINING_TYPES } from '@/constants/alertThresholds'

interface Props {
  subjective: SubjectiveCheck[]
  physical: PhysicalCheck[]
  meal: MealLog[]
  training: TrainingLog[]
}

const TRAINING_LABEL = Object.fromEntries(TRAINING_TYPES.map(t => [t.value, t.label]))

const SYNC_ID = 'overview'

// 全データを日付キーでマージ
function mergeByDate(
  subjective: SubjectiveCheck[],
  physical: PhysicalCheck[],
  meal: MealLog[],
  training: TrainingLog[],
) {
  const map = new Map<string, Record<string, number | string | null>>()

  for (const d of subjective) {
    map.set(d.check_date, {
      ...map.get(d.check_date),
      date: d.check_date.slice(5),
      fatigue_before: d.fatigue_before,
      fatigue_after: d.fatigue_after,
      sleep_quality: d.sleep_quality,
      sleep_hours: d.sleep_hours,
    })
  }
  for (const d of physical) {
    map.set(d.check_date, {
      ...map.get(d.check_date),
      date: d.check_date.slice(5),
      weight_kg: d.weight_kg,
      body_fat_pct: d.body_fat_pct,
      resting_heart_rate: d.resting_heart_rate,
    })
  }
  for (const d of meal) {
    map.set(d.log_date, {
      ...map.get(d.log_date),
      date: d.log_date.slice(5),
      appetite: d.appetite,
      nutrition_balance: d.nutrition_balance,
      water_l: d.water_ml ? Math.round(d.water_ml / 100) / 10 : null,
    })
  }
  for (const d of training) {
    map.set(d.log_date, {
      ...map.get(d.log_date),
      date: d.log_date.slice(5),
      rpe: d.rpe,
      training_type: TRAINING_LABEL[d.training_type] ?? d.training_type,
    })
  }

  return Array.from(map.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([, v]) => v)
}

// 高強度日（RPE >= 8）の日付を抽出
function getHighIntensityDates(training: TrainingLog[]) {
  return training.filter(d => d.rpe >= 8).map(d => d.log_date.slice(5))
}

interface PanelTooltipProps {
  active?: boolean
  payload?: { name: string; value: number | null; color: string; unit?: string }[]
  label?: string
}

function CustomTooltip({ active, payload, label }: PanelTooltipProps) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-2 text-xs">
      <p className="font-semibold text-gray-700 mb-1">{label}</p>
      {payload.map((p, i) => (
        p.value !== null && p.value !== undefined ? (
          <p key={i} style={{ color: p.color }}>
            {p.name}: <span className="font-medium">{p.value}{p.unit ?? ''}</span>
          </p>
        ) : null
      ))}
    </div>
  )
}

export function OverviewChart({ subjective, physical, meal, training }: Props) {
  const data = mergeByDate(subjective, physical, meal, training)
  const highIntensityDates = getHighIntensityDates(training)

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-40 text-gray-400 text-sm">
        データがありません
      </div>
    )
  }

  return (
    <div className="space-y-0">
      {/* --- Panel 1: コンディション（疲労度・睡眠） --- */}
      <div>
        <div className="flex items-center gap-2 mb-1 px-1">
          <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">コンディション</span>
          <span className="text-xs text-gray-400">疲労度（1=元気 5=疲れ）・睡眠時間</span>
        </div>
        <ResponsiveContainer width="100%" height={160}>
          <ComposedChart data={data} syncId={SYNC_ID} margin={{ top: 4, right: 48, left: 4, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" tick={false} axisLine={false} />
            <YAxis yAxisId="fatigue" domain={[1, 5]} ticks={[1, 2, 3, 4, 5]} tick={{ fontSize: 10 }} width={20} />
            <YAxis yAxisId="sleep" orientation="right" domain={[0, 12]} ticks={[0, 4, 8, 12]} tick={{ fontSize: 10 }} unit="h" width={28} />
            {highIntensityDates.map(d => (
              <ReferenceLine key={d} x={d} yAxisId="fatigue" stroke="#fca5a5" strokeDasharray="3 3" />
            ))}
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Bar yAxisId="sleep" dataKey="sleep_hours" name="睡眠時間" fill="#bfdbfe" opacity={0.6} radius={[2, 2, 0, 0]} unit="h" />
            <Line yAxisId="fatigue" type="monotone" dataKey="fatigue_before" name="練習前疲労" stroke="#60a5fa" strokeWidth={2} dot={{ r: 3 }} />
            <Line yAxisId="fatigue" type="monotone" dataKey="fatigue_after" name="練習後疲労" stroke="#ef4444" strokeWidth={2} dot={{ r: 3 }} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* --- Panel 2: 身体データ --- */}
      <div>
        <div className="flex items-center gap-2 mb-1 px-1 pt-3 border-t border-gray-100">
          <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">身体データ</span>
          <span className="text-xs text-gray-400">体重（kg）・体脂肪率（%）・安静時心拍（bpm）</span>
        </div>
        <ResponsiveContainer width="100%" height={140}>
          <ComposedChart data={data} syncId={SYNC_ID} margin={{ top: 4, right: 48, left: 4, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" tick={false} axisLine={false} />
            <YAxis yAxisId="weight" domain={['auto', 'auto']} tick={{ fontSize: 10 }} width={20} unit="kg" />
            <YAxis yAxisId="hr" orientation="right" domain={['auto', 'auto']} tick={{ fontSize: 10 }} unit="bpm" width={36} />
            {highIntensityDates.map(d => (
              <ReferenceLine key={d} x={d} yAxisId="weight" stroke="#fca5a5" strokeDasharray="3 3" />
            ))}
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Line yAxisId="weight" type="monotone" dataKey="weight_kg" name="体重" stroke="#8b5cf6" strokeWidth={2} dot={{ r: 3 }} unit="kg" />
            <Line yAxisId="weight" type="monotone" dataKey="body_fat_pct" name="体脂肪率" stroke="#10b981" strokeWidth={2} dot={{ r: 3 }} strokeDasharray="4 2" unit="%" />
            <Bar yAxisId="hr" dataKey="resting_heart_rate" name="安静時心拍" fill="#f97316" opacity={0.5} radius={[2, 2, 0, 0]} unit="bpm" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* --- Panel 3: 食事 --- */}
      <div>
        <div className="flex items-center gap-2 mb-1 px-1 pt-3 border-t border-gray-100">
          <span className="text-xs font-semibold text-gray-600 uppercase tracking-wide">食事・栄養</span>
          <span className="text-xs text-gray-400">食欲・栄養バランス（1=良 5=悪）・水分摂取量（L）</span>
        </div>
        <ResponsiveContainer width="100%" height={140}>
          <ComposedChart data={data} syncId={SYNC_ID} margin={{ top: 4, right: 48, left: 4, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" tick={{ fontSize: 10 }} />
            <YAxis yAxisId="score" domain={[1, 5]} ticks={[1, 2, 3, 4, 5]} tick={{ fontSize: 10 }} width={20} />
            <YAxis yAxisId="water" orientation="right" domain={[0, 4]} tick={{ fontSize: 10 }} unit="L" width={28} />
            {highIntensityDates.map(d => (
              <ReferenceLine key={d} x={d} yAxisId="score" stroke="#fca5a5" strokeDasharray="3 3" label={{ value: '高強度', position: 'top', fontSize: 9, fill: '#ef4444' }} />
            ))}
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Bar yAxisId="score" dataKey="appetite" name="食欲" fill="#fb923c" opacity={0.6} radius={[2, 2, 0, 0]} />
            <Line yAxisId="score" type="monotone" dataKey="nutrition_balance" name="栄養バランス" stroke="#10b981" strokeWidth={2} dot={{ r: 3 }} />
            <Line yAxisId="water" type="monotone" dataKey="water_l" name="水分摂取" stroke="#3b82f6" strokeWidth={2} dot={{ r: 3 }} strokeDasharray="4 2" unit="L" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
