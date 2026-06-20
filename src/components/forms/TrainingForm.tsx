import { useState } from 'react'
import { Slider } from '@/components/ui/Slider'
import { Button } from '@/components/ui/Button'
import type { TrainingEntry } from '@/types/app.types'

interface Props {
  defaultValues?: TrainingEntry[]
  onNext: (data: TrainingEntry[]) => void
  onBack: () => void
}

type SectionKey = 'sprint' | 'start' | 'weight'

interface SectionData {
  duration_min: number
  rpe: number
  explosive_power: number
  endurance: number
  exercise_fatigue: number
  notes: string
}

const SECTION_LABELS: Record<SectionKey, string> = {
  sprint: '⚡ 短距離ダッシュ',
  start: '🚀 スタート練習',
  weight: '🏋️ ウエイトトレーニング',
}

export function TrainingForm({ defaultValues, onNext, onBack }: Props) {
  const isRestDefault = defaultValues?.some(v => v.training_type === 'rest') ?? false
  const sprintDefault = defaultValues?.find(v => v.training_type === 'sprint')
  const startDefault = defaultValues?.find(v => v.training_type === 'start')
  const weightDefault = defaultValues?.find(v => v.training_type === 'weight')

  const [isRest, setIsRest] = useState(isRestDefault)
  const [enabled, setEnabled] = useState<Record<SectionKey, boolean>>({
    sprint: !!sprintDefault || (!isRestDefault && !startDefault && !weightDefault),
    start: !!startDefault,
    weight: !!weightDefault,
  })
  const [sections, setSections] = useState<Record<SectionKey, SectionData>>({
    sprint: {
      duration_min: sprintDefault?.duration_min ?? 60,
      rpe: sprintDefault?.rpe ?? 5,
      explosive_power: sprintDefault?.explosive_power ?? 3,
      endurance: sprintDefault?.endurance ?? 3,
      exercise_fatigue: sprintDefault?.exercise_fatigue ?? 3,
      notes: sprintDefault?.notes ?? '',
    },
    start: {
      duration_min: startDefault?.duration_min ?? 30,
      rpe: startDefault?.rpe ?? 5,
      explosive_power: startDefault?.explosive_power ?? 3,
      endurance: startDefault?.endurance ?? 3,
      exercise_fatigue: startDefault?.exercise_fatigue ?? 3,
      notes: startDefault?.notes ?? '',
    },
    weight: {
      duration_min: weightDefault?.duration_min ?? 60,
      rpe: weightDefault?.rpe ?? 5,
      explosive_power: weightDefault?.explosive_power ?? 3,
      endurance: weightDefault?.endurance ?? 3,
      exercise_fatigue: weightDefault?.exercise_fatigue ?? 3,
      notes: weightDefault?.notes ?? '',
    },
  })
  const [error, setError] = useState('')

  function toggleRest() {
    setIsRest(v => !v)
    setError('')
  }

  function toggleSection(key: SectionKey) {
    setEnabled(prev => ({ ...prev, [key]: !prev[key] }))
    setIsRest(false)
    setError('')
  }

  function updateSection(key: SectionKey, field: keyof SectionData, value: number | string) {
    setSections(prev => ({ ...prev, [key]: { ...prev[key], [field]: value } }))
  }

  function handleSubmit() {
    if (isRest) {
      onNext([{ training_type: 'rest', duration_min: 0, rpe: 1, explosive_power: 1, endurance: 1, exercise_fatigue: 1 }])
      return
    }
    const keys: SectionKey[] = ['sprint', 'start', 'weight']
    if (!keys.some(k => enabled[k])) {
      setError('少なくとも1つ選択してください')
      return
    }
    for (const key of keys) {
      if (enabled[key] && sections[key].duration_min < 1) {
        setError(`${SECTION_LABELS[key]}の練習時間を1分以上入力してください`)
        return
      }
    }
    const entries: TrainingEntry[] = []
    for (const key of keys) {
      if (enabled[key]) {
        entries.push({ training_type: key, ...sections[key], notes: sections[key].notes || undefined })
      }
    }
    onNext(entries)
  }

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-gray-800 mb-1">トレーニングログ</h2>
        <p className="text-sm text-gray-500">今日実施したトレーニングを選んでください（複数選択可）</p>
      </div>

      <button
        type="button"
        onClick={toggleRest}
        className={`w-full py-3 rounded-xl text-sm font-bold border-2 transition-colors ${
          isRest ? 'bg-gray-800 text-white border-gray-800' : 'bg-white text-gray-600 border-gray-200'
        }`}
      >
        🛌 休養日
      </button>

      {(['sprint', 'start', 'weight'] as SectionKey[]).map(key => (
        <div key={key} className={`rounded-xl border-2 overflow-hidden transition-colors ${enabled[key] && !isRest ? 'border-blue-500' : 'border-gray-200'}`}>
          <button
            type="button"
            onClick={() => toggleSection(key)}
            disabled={isRest}
            className={`w-full flex items-center justify-between px-4 py-3 text-sm font-bold ${
              enabled[key] && !isRest ? 'bg-blue-50 text-blue-700' : 'bg-gray-50 text-gray-400'
            }`}
          >
            <span>{SECTION_LABELS[key]}</span>
            <span className="text-lg">{enabled[key] && !isRest ? '✓' : '+'}</span>
          </button>

          {enabled[key] && !isRest && (
            <div className="p-4 space-y-5">
              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-gray-700">練習時間 (分) <span className="text-red-500">*</span></label>
                <input
                  type="number"
                  min="1"
                  max="480"
                  placeholder="例: 90"
                  value={sections[key].duration_min}
                  onChange={e => updateSection(key, 'duration_min', Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <Slider
                label="RPE（運動強度）"
                value={sections[key].rpe}
                onChange={v => updateSection(key, 'rpe', v)}
                min={1}
                max={10}
                leftLabel="楽"
                rightLabel="最大"
              />

              <Slider
                label="瞬発力・爆発力"
                value={sections[key].explosive_power}
                onChange={v => updateSection(key, 'explosive_power', v)}
                leftLabel="低い"
                rightLabel="高い"
              />

              <Slider
                label={key === 'weight' ? 'トレーニング質' : 'ストライド感・スピード感'}
                value={sections[key].endurance}
                onChange={v => updateSection(key, 'endurance', v)}
                leftLabel="悪い"
                rightLabel="良い"
              />

              <Slider
                label="運動中の疲労感"
                value={sections[key].exercise_fatigue}
                onChange={v => updateSection(key, 'exercise_fatigue', v)}
                leftLabel="なし"
                rightLabel="強い"
              />

              <div className="flex flex-col gap-1">
                <label className="text-sm font-medium text-gray-700">メモ（任意）</label>
                <textarea
                  rows={2}
                  placeholder="タイム、気づいたこと、身体の感覚など"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                  value={sections[key].notes}
                  onChange={e => updateSection(key, 'notes', e.target.value)}
                />
              </div>
            </div>
          )}
        </div>
      ))}

      {error && <p className="text-xs text-red-600">{error}</p>}

      <div className="flex justify-between pt-2">
        <Button type="button" variant="secondary" onClick={onBack}>← 戻る</Button>
        <Button type="button" onClick={handleSubmit}>確認 →</Button>
      </div>
    </div>
  )
}
