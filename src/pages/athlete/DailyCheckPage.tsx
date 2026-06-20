import { useState } from 'react'
import { toast } from 'sonner'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { useDailyCheck } from '@/hooks/useDailyCheck'
import { DailyCheckWizard } from '@/components/forms/DailyCheckWizard'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import type { DailyCheckFormData } from '@/types/app.types'

const toDateStr = (d: Date) => d.toISOString().split('T')[0]

export function DailyCheckPage() {
  const { profile } = useAuth()
  const navigate = useNavigate()
  const [selectedDate, setSelectedDate] = useState(toDateStr(new Date()))

  const { data, isLoading, submitCheck, isPending } = useDailyCheck(
    profile?.id ?? '',
    selectedDate
  )

  const isEditing = Boolean(data?.subjective || data?.physical || (data?.training ?? []).length > 0)

  async function handleSubmit(formData: DailyCheckFormData) {
    try {
      await submitCheck(formData)
      toast.success('コンディションを記録しました！')
      void navigate('/dashboard')
    } catch (err) {
      const msg = err instanceof Error ? err.message : '不明なエラー'
      toast.error(`送信失敗: ${msg}`)
    }
  }

  if (isLoading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
      </div>
    )
  }

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-gray-900">コンディション記録</h1>
        <p className="text-sm text-gray-500 mt-0.5">日付を選んで記録してください</p>
      </div>

      {/* 日付選択 */}
      <div className="mb-4 flex items-center gap-3">
        <label className="text-sm font-medium text-gray-700 shrink-0">日付</label>
        <input
          type="date"
          value={selectedDate}
          max={toDateStr(new Date())}
          onChange={e => setSelectedDate(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm flex-1"
        />
      </div>

      {isEditing && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg flex items-center justify-between text-sm">
          <p className="text-blue-700">この日のデータは既に入力済みです。</p>
          <Button size="sm" variant="ghost" onClick={() => void navigate('/dashboard')}>
            ダッシュボードへ
          </Button>
        </div>
      )}

      <Card padding="lg">
        <DailyCheckWizard
          onSubmit={handleSubmit}
          isPending={isPending}
          existingData={
            data?.subjective || data?.physical || data?.meal || (data?.training ?? []).length > 0
              ? {
                  subjective: {
                    morning_condition: data?.subjective?.morning_condition ?? 3,
                    fatigue_before: data?.subjective?.fatigue_before ?? 3,
                    fatigue_after: data?.subjective?.fatigue_after ?? 3,
                    sleep_quality: data?.subjective?.sleep_quality ?? 3,
                    sleep_hours: Number(data?.subjective?.sleep_hours ?? 7),
                  },
                  physical: {
                    weight_kg: String(data?.physical?.weight_kg ?? ''),
                    resting_heart_rate: String(data?.physical?.resting_heart_rate ?? ''),
                    body_fat_pct: String(data?.physical?.body_fat_pct ?? ''),
                  },
                  training: (data?.training ?? []).map(t => ({
                    training_type: t.training_type,
                    duration_min: t.duration_min,
                    rpe: t.rpe,
                    explosive_power: t.explosive_power ?? 3,
                    endurance: t.endurance ?? 3,
                    exercise_fatigue: t.exercise_fatigue ?? 3,
                    notes: t.notes ?? '',
                  })),
                  meal: {
                    appetite: data?.meal?.appetite ?? 3,
                    meal_count: data?.meal?.meal_count ?? 3,
                    water_ml: String(data?.meal?.water_ml ?? ''),
                    nutrition_balance: data?.meal?.nutrition_balance ?? 3,
                    post_exercise_meal: data?.meal?.post_exercise_meal ?? false,
                    mushroom_seaweed: data?.meal?.mushroom_seaweed ?? undefined,
                    carb_breakfast: data?.meal?.carb_breakfast ?? undefined,
                    carb_lunch: data?.meal?.carb_lunch ?? undefined,
                    carb_dinner: data?.meal?.carb_dinner ?? undefined,
                    carb_snack_wagashi: data?.meal?.carb_snack_wagashi ?? undefined,
                    carb_snack_fruit: data?.meal?.carb_snack_fruit ?? undefined,
                    carb_snack_juice_jelly: data?.meal?.carb_snack_juice_jelly ?? undefined,
                    carb_snack_other: data?.meal?.carb_snack_other ?? undefined,
                    protein_lunch_fish: data?.meal?.protein_lunch_fish ?? undefined,
                    protein_lunch_meat: data?.meal?.protein_lunch_meat ?? undefined,
                    protein_lunch_bean: data?.meal?.protein_lunch_bean ?? undefined,
                    protein_lunch_egg: data?.meal?.protein_lunch_egg ?? undefined,
                    protein_dinner_fish: data?.meal?.protein_dinner_fish ?? undefined,
                    protein_dinner_meat: data?.meal?.protein_dinner_meat ?? undefined,
                    protein_dinner_bean: data?.meal?.protein_dinner_bean ?? undefined,
                    protein_dinner_egg: data?.meal?.protein_dinner_egg ?? undefined,
                    notes: data?.meal?.notes ?? '',
                  },
                }
              : null
          }
        />
      </Card>
    </div>
  )
}
