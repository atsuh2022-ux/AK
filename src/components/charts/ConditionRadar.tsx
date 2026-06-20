import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, Tooltip,
} from 'recharts'
import type { SubjectiveCheck, PhysicalCheck } from '@/types/app.types'

interface Props {
  subjective: SubjectiveCheck | null
  physical: PhysicalCheck | null
  showFatigueBefore?: boolean
  showFatigueAfter?: boolean
  showBodyFat?: boolean
}

export function ConditionRadar({
  subjective,
  physical,
  showFatigueBefore = true,
  showFatigueAfter = true,
  showBodyFat = true,
}: Props) {
  if (!subjective) {
    return (
      <div className="flex items-center justify-center h-40 text-gray-400 text-sm">
        今日のデータがありません
      </div>
    )
  }

  const allAxes = [
    showFatigueBefore && { subject: '練習前元気さ', value: 6 - subjective.fatigue_before, fullMark: 5 },
    showFatigueAfter && { subject: '練習後回復力', value: 6 - subjective.fatigue_after, fullMark: 5 },
    { subject: '睡眠の質', value: 6 - subjective.sleep_quality, fullMark: 5 },
    {
      subject: '睡眠時間',
      value: Math.min(5, Math.round((subjective.sleep_hours / 9) * 5)),
      fullMark: 5,
    },
    showBodyFat && {
      subject: '体脂肪率',
      value: physical?.body_fat_pct
        ? Math.min(5, Math.round(((25 - physical.body_fat_pct) / 20) * 5))
        : 3,
      fullMark: 5,
    },
  ].filter(Boolean) as { subject: string; value: number; fullMark: number }[]

  return (
    <ResponsiveContainer width="100%" height={220}>
      <RadarChart cx="50%" cy="50%" outerRadius="75%" data={allAxes}>
        <PolarGrid />
        <PolarAngleAxis dataKey="subject" tick={{ fontSize: 10 }} />
        <Radar name="今日のコンディション" dataKey="value" stroke="#2563eb" fill="#2563eb" fillOpacity={0.3} />
        <Tooltip formatter={(v: unknown) => [`${v} / 5`, '']} />
      </RadarChart>
    </ResponsiveContainer>
  )
}
