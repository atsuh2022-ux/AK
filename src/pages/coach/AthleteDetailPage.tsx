import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { toast } from 'sonner'
import { useTrends } from '@/hooks/useTrends'
import { useAthleteList } from '@/hooks/useAthleteList'
import { useAthleteSettings } from '@/hooks/useAthleteSettings'
import { exportAthleteExcel } from '@/lib/exportExcel'
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

const toDateStr = (d: Date) => d.toISOString().split('T')[0]

export function AthleteDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [days, setDays] = useState<7 | 30>(30)
  const { data: trends, isLoading } = useTrends(id ?? '', days)
  const { data: athletes } = useAthleteList()
  const athlete = athletes?.find(a => a.id === id)

  const { settings, updateSettings, isUpdating } = useAthleteSettings(id ?? '')
  const [logTab, setLogTab] = useState<'practice' | 'weight'>('practice')

  const defaultTo = toDateStr(new Date())
  const defaultFrom = toDateStr(new Date(Date.now() - 30 * 24 * 60 * 60 * 1000))
  const [exportFrom, setExportFrom] = useState(defaultFrom)
  const [exportTo, setExportTo] = useState(defaultTo)
  const [isExporting, setIsExporting] = useState(false)

  async function handleExport() {
    if (!id || !athlete) return
    setIsExporting(true)
    try {
      await exportAthleteExcel(id, athlete.full_name, exportFrom, exportTo, settings)
      toast.success('Excelをダウンロードしました')
    } catch {
      toast.error('ダウンロードに失敗しました')
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <Link to="/coach">
          <Button size="sm" variant="ghost">← 戻る</Button>
        </Link>
        <div>
          <h1 className="text-xl font-bold text-gray-900">{athlete?.full_name ?? '読み込み中...'}</h1>
          <p className="text-sm text-gray-500">アスリート詳細</p>
        </div>
        <div className="ml-auto flex gap-2">
          <Button size="sm" variant={days === 7 ? 'primary' : 'secondary'} onClick={() => setDays(7)}>7日</Button>
          <Button size="sm" variant={days === 30 ? 'primary' : 'secondary'} onClick={() => setDays(30)}>30日</Button>
        </div>
      </div>

      {/* Excelダウンロード */}
      <Card>
        <p className="text-sm font-semibold text-gray-700 mb-3">Excelダウンロード</p>
        <div className="flex flex-wrap items-end gap-3">
          <div>
            <label className="block text-xs text-gray-500 mb-1">開始日</label>
            <input
              type="date"
              value={exportFrom}
              onChange={e => setExportFrom(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-500 mb-1">終了日</label>
            <input
              type="date"
              value={exportTo}
              onChange={e => setExportTo(e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
            />
          </div>
          <Button onClick={() => void handleExport()} disabled={isExporting}>
            {isExporting ? 'ダウンロード中...' : '📥 Excelダウンロード'}
          </Button>
        </div>
      </Card>

      {/* 入力項目設定 */}
      <Card>
        <p className="text-sm font-semibold text-gray-700 mb-3">入力項目の設定</p>
        <p className="text-xs text-gray-400 mb-4">オフにした項目はアスリートの入力フォームに表示されません</p>
        <div className="space-y-3">
          {[
            { key: 'show_fatigue_before', label: '疲労度（練習前）' },
            { key: 'show_fatigue_after', label: '疲労度（練習後）' },
            { key: 'show_weight', label: '体重 (kg)' },
            { key: 'show_body_fat', label: '体脂肪率 (%)' },
            { key: 'show_heart_rate', label: '安静時心拍数 (bpm)' },
            { key: 'show_appetite', label: '食欲' },
            { key: 'show_nutrition_balance', label: '栄養バランス' },
            { key: 'show_meal_count', label: '食事回数' },
            { key: 'show_water_ml', label: '水分摂取量' },
            { key: 'show_mushroom_seaweed', label: 'きのこ・海藻類の摂取' },
            { key: 'show_carb_intake', label: '糖質摂取量（朝・昼・夕）' },
            { key: 'show_carb_snack', label: '糖質メインの補食' },
            { key: 'show_protein_source', label: '主菜のタンパク質源（昼・夕）' },
          ].map(({ key, label }) => (
            <label key={key} className="flex items-center justify-between">
              <span className="text-sm text-gray-700">{label}</span>
              <button
                type="button"
                disabled={isUpdating}
                onClick={() => void updateSettings({ [key]: !settings[key as keyof typeof settings] })}
                className={`relative w-12 h-6 rounded-full transition-colors ${
                  settings[key as keyof typeof settings] ? 'bg-blue-600' : 'bg-gray-300'
                }`}
              >
                <span className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${
                  settings[key as keyof typeof settings] ? 'translate-x-7' : 'translate-x-1'
                }`} />
              </button>
            </label>
          ))}
        </div>
      </Card>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {(settings.show_fatigue_before || settings.show_fatigue_after) && (
              <Card>
                <p className="text-sm font-semibold text-gray-700 mb-3">主観的体調の推移（疲労度）</p>
                <TrendLineChart
                  data={trends?.subjective ?? []}
                  showFatigueBefore={settings.show_fatigue_before}
                  showFatigueAfter={settings.show_fatigue_after}
                />
              </Card>
            )}

            <Card>
              <p className="text-sm font-semibold text-gray-700 mb-3">運動強度 (RPE)</p>
              <RPEBarChart data={trends?.training ?? []} />
            </Card>

            <Card>
              <p className="text-sm font-semibold text-gray-700 mb-1">トレーニング詳細</p>
              <p className="text-xs text-gray-400 mb-3">時間・爆発力・持久力・運動後疲労（右軸: 1〜5）</p>
              <TrainingDetailChart data={trends?.training ?? []} />
            </Card>

            <Card>
              <p className="text-sm font-semibold text-gray-700 mb-1">睡眠の推移</p>
              <p className="text-xs text-gray-400 mb-3">睡眠時間（左軸）・睡眠の質（右軸: 1=良 5=悪）</p>
              <SleepChart data={trends?.subjective ?? []} />
            </Card>

            {(settings.show_weight || settings.show_body_fat || settings.show_heart_rate) && (
              <Card>
                <p className="text-sm font-semibold text-gray-700 mb-3">体重・安静時心拍の推移</p>
                <MultiMetricChart
                  data={trends?.physical ?? []}
                  showWeight={settings.show_weight}
                  showBodyFat={settings.show_body_fat}
                  showHeartRate={settings.show_heart_rate}
                />
              </Card>
            )}

            {(settings.show_appetite || settings.show_nutrition_balance || settings.show_meal_count || settings.show_water_ml) && (
              <Card className="col-span-1 md:col-span-2">
                <p className="text-sm font-semibold text-gray-700 mb-1">食事・栄養の推移</p>
                <p className="text-xs text-gray-400 mb-3">食欲・栄養バランス（1=良 5=悪）・水分摂取量（L）</p>
                <MealChart
                  data={trends?.meal ?? []}
                  showAppetite={settings.show_appetite}
                  showNutritionBalance={settings.show_nutrition_balance}
                  showMealCount={settings.show_meal_count}
                  showWaterMl={settings.show_water_ml}
                />
              </Card>
            )}

            {settings.show_carb_intake && (
              <Card className="col-span-1 md:col-span-2">
                <p className="text-sm font-semibold text-gray-700 mb-1">糖質摂取量の推移</p>
                <p className="text-xs text-gray-400 mb-3">朝・昼・夕の主食量（1=なし 〜 5=かなり多い）</p>
                <CarbChart data={trends?.meal ?? []} />
              </Card>
            )}

            {(settings.show_mushroom_seaweed || settings.show_carb_snack || settings.show_protein_source) && (
              <Card className="col-span-1 md:col-span-2">
                <p className="text-sm font-semibold text-gray-700 mb-1">食事チェック（直近7日）</p>
                <p className="text-xs text-gray-400 mb-3">補食・きのこ海藻・タンパク質源の確認</p>
                <MealCheckSummary
                  data={trends?.meal ?? []}
                  showMushroomSeaweed={settings.show_mushroom_seaweed}
                  showCarbSnack={settings.show_carb_snack}
                  showProteinSource={settings.show_protein_source}
                />
              </Card>
            )}
          </div>

          <Card>
            <p className="text-sm font-semibold text-gray-700 mb-3">トレーニングログ</p>

            {/* タブ */}
            <div className="flex gap-1 mb-4 bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setLogTab('practice')}
                className={`flex-1 py-1.5 text-sm font-medium rounded-md transition-colors ${logTab === 'practice' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500'}`}
              >
                実践練習
              </button>
              <button
                onClick={() => setLogTab('weight')}
                className={`flex-1 py-1.5 text-sm font-medium rounded-md transition-colors ${logTab === 'weight' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-500'}`}
              >
                ウエイト
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-100">
                    <th className="text-left py-2 pr-4 text-gray-500 font-medium">日付</th>
                    <th className="text-right py-2 pr-4 text-gray-500 font-medium">時間</th>
                    <th className="text-right py-2 pr-4 text-gray-500 font-medium">RPE</th>
                    <th className="text-left py-2 text-gray-500 font-medium">メモ</th>
                  </tr>
                </thead>
                <tbody>
                  {[...(trends?.training ?? [])]
                    .filter(log => logTab === 'practice' ? log.training_type === 'practice' : log.training_type === 'weight')
                    .reverse()
                    .map(log => (
                      <tr key={log.id} className="border-b border-gray-50">
                        <td className="py-2 pr-4 text-gray-600">{log.log_date}</td>
                        <td className="py-2 pr-4 text-right text-gray-600">{log.duration_min}分</td>
                        <td className="py-2 pr-4 text-right font-medium">{log.rpe}/10</td>
                        <td className="py-2 text-gray-500 text-xs">{log.notes ?? '—'}</td>
                      </tr>
                    ))}
                  {(trends?.training ?? []).filter(log => logTab === 'practice' ? log.training_type === 'practice' : log.training_type === 'weight').length === 0 && (
                    <tr>
                      <td colSpan={4} className="py-4 text-center text-gray-400">データがありません</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </Card>
        </>
      )}
    </div>
  )
}
