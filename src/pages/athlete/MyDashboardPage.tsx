import { useState } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useTrends } from '@/hooks/useTrends'
import { useAthleteSettings } from '@/hooks/useAthleteSettings'
import { Card } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { TrendLineChart } from '@/components/charts/TrendLineChart'
import { RPEBarChart } from '@/components/charts/RPEBarChart'
import { MultiMetricChart } from '@/components/charts/MultiMetricChart'
import { MealChart } from '@/components/charts/MealChart'
import { CarbChart } from '@/components/charts/CarbChart'
import { MealCheckSummary } from '@/components/charts/MealCheckSummary'
import { SleepChart } from '@/components/charts/SleepChart'
import { TrainingDetailChart } from '@/components/charts/TrainingDetailChart'

export function MyDashboardPage() {
  const { profile } = useAuth()
  const [days, setDays] = useState<7 | 30>(7)
  const { data, isLoading } = useTrends(profile?.id ?? '', days)
  const { settings } = useAthleteSettings(profile?.id ?? '')


  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">マイダッシュボード</h1>
          <p className="text-sm text-gray-500">{profile?.full_name}</p>
        </div>
        <div className="flex gap-2">
          <Button size="sm" variant={days === 7 ? 'primary' : 'secondary'} onClick={() => setDays(7)}>7日</Button>
          <Button size="sm" variant={days === 30 ? 'primary' : 'secondary'} onClick={() => setDays(30)}>30日</Button>
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {(settings.show_fatigue_before || settings.show_fatigue_after) && (
            <Card>
              <p className="text-sm font-semibold text-gray-700 mb-1">疲労度の推移</p>
              <p className="text-xs text-gray-400 mb-3">練習前 / 後（1=元気 5=疲れ）</p>
              <TrendLineChart
                data={data?.subjective ?? []}
                showFatigueBefore={settings.show_fatigue_before}
                showFatigueAfter={settings.show_fatigue_after}
              />
            </Card>
          )}

          <Card>
            <p className="text-sm font-semibold text-gray-700 mb-1">運動強度 (RPE)</p>
            <p className="text-xs text-gray-400 mb-3">トレーニング種目・強度の推移</p>
            <RPEBarChart data={data?.training ?? []} />
          </Card>

          <Card>
            <p className="text-sm font-semibold text-gray-700 mb-1">トレーニング詳細</p>
            <p className="text-xs text-gray-400 mb-3">時間・爆発力・持久力・運動後疲労（右軸: 1〜5）</p>
            <TrainingDetailChart data={data?.training ?? []} />
          </Card>

          <Card>
            <p className="text-sm font-semibold text-gray-700 mb-1">睡眠の推移</p>
            <p className="text-xs text-gray-400 mb-3">睡眠時間（左軸）・睡眠の質（右軸: 1=良 5=悪）</p>
            <SleepChart data={data?.subjective ?? []} />
          </Card>

          {(settings.show_weight || settings.show_body_fat || settings.show_heart_rate) && (
            <Card>
              <p className="text-sm font-semibold text-gray-700 mb-1">身体データの推移</p>
              <p className="text-xs text-gray-400 mb-3">体重（kg）・体脂肪率（%）・安静時心拍（bpm）</p>
              <MultiMetricChart
                data={data?.physical ?? []}
                showWeight={settings.show_weight}
                showBodyFat={settings.show_body_fat}
                showHeartRate={settings.show_heart_rate}
              />
            </Card>
          )}

          {(settings.show_appetite || settings.show_nutrition_balance || settings.show_meal_count || settings.show_water_ml) && (
            <Card className="md:col-span-2">
              <p className="text-sm font-semibold text-gray-700 mb-1">食事・栄養の推移</p>
              <p className="text-xs text-gray-400 mb-3">食欲・栄養バランス（1=良 5=悪）・水分摂取量（L）</p>
              <MealChart
                data={data?.meal ?? []}
                showAppetite={settings.show_appetite}
                showNutritionBalance={settings.show_nutrition_balance}
                showMealCount={settings.show_meal_count}
                showWaterMl={settings.show_water_ml}
              />
            </Card>
          )}

          {settings.show_carb_intake && (
            <Card className="md:col-span-2">
              <p className="text-sm font-semibold text-gray-700 mb-1">糖質摂取量の推移</p>
              <p className="text-xs text-gray-400 mb-3">朝・昼・夕の主食量（1=なし 〜 5=かなり多い）</p>
              <CarbChart data={data?.meal ?? []} />
            </Card>
          )}

          {(settings.show_mushroom_seaweed || settings.show_carb_snack || settings.show_protein_source) && (
            <Card className="md:col-span-2">
              <p className="text-sm font-semibold text-gray-700 mb-1">食事チェック（直近7日）</p>
              <p className="text-xs text-gray-400 mb-3">補食・きのこ海藻・タンパク質源の確認</p>
              <MealCheckSummary
                data={data?.meal ?? []}
                showMushroomSeaweed={settings.show_mushroom_seaweed}
                showCarbSnack={settings.show_carb_snack}
                showProteinSource={settings.show_protein_source}
              />
            </Card>
          )}
        </div>
      )}
    </div>
  )
}
