import { useReducer } from 'react'
import { SubjectiveForm } from './SubjectiveForm'
import { PhysicalForm } from './PhysicalForm'
import { TrainingForm } from './TrainingForm'
import { MealForm } from './MealForm'
import { Button } from '@/components/ui/Button'
import { evaluateAlertPreview } from '@/lib/alertEngine'
import { useAthleteSettings } from '@/hooks/useAthleteSettings'
import { useAuth } from '@/hooks/useAuth'
import type { SubjectiveFormValues, PhysicalFormValues, MealFormValues } from '@/schemas/dailyCheck.schema'
import type { DailyCheckFormData, TrainingEntry } from '@/types/app.types'

type Step = 'subjective' | 'physical' | 'training' | 'meal' | 'confirm'

interface State {
  step: Step
  subjective: SubjectiveFormValues | null
  physical: PhysicalFormValues | null
  training: TrainingEntry[] | null
  meal: MealFormValues | null
}

type Action =
  | { type: 'SET_SUBJECTIVE'; payload: SubjectiveFormValues }
  | { type: 'SET_PHYSICAL'; payload: PhysicalFormValues }
  | { type: 'SET_TRAINING'; payload: TrainingEntry[] }
  | { type: 'SET_MEAL'; payload: MealFormValues }
  | { type: 'BACK' }

const STEPS: Step[] = ['subjective', 'physical', 'training', 'meal', 'confirm']

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'SET_SUBJECTIVE':
      return { ...state, step: 'physical', subjective: action.payload }
    case 'SET_PHYSICAL':
      return { ...state, step: 'training', physical: action.payload }
    case 'SET_TRAINING':
      return { ...state, step: 'meal', training: action.payload }
    case 'SET_MEAL':
      return { ...state, step: 'confirm', meal: action.payload }
    case 'BACK': {
      const idx = STEPS.indexOf(state.step)
      return { ...state, step: STEPS[Math.max(0, idx - 1)] }
    }
  }
}

const STEP_LABELS: Record<Step, string> = {
  subjective: '主観的体調',
  physical: '身体データ',
  training: 'トレーニング',
  meal: '食事',
  confirm: '確認',
}

const TRAINING_TYPE_LABEL: Record<string, string> = {
  practice: '実践トレーニング',
  weight: 'ウエイトトレーニング',
  rest: '休養日',
}

interface Props {
  onSubmit: (data: DailyCheckFormData) => Promise<void>
  isPending: boolean
  existingData?: DailyCheckFormData | null
}

export function DailyCheckWizard({ onSubmit, isPending, existingData }: Props) {
  const { profile } = useAuth()
  const { settings } = useAthleteSettings(profile?.id ?? '')

  const [state, dispatch] = useReducer(reducer, {
    step: 'subjective',
    subjective: existingData?.subjective ?? null,
    physical: existingData?.physical ?? null,
    training: existingData?.training ?? null,
    meal: existingData?.meal ?? null,
  })

  const currentStepIdx = STEPS.indexOf(state.step)
  const progress = (currentStepIdx / (STEPS.length - 1)) * 100

  function handleConfirm() {
    if (!state.subjective || !state.physical || !state.training || !state.meal) return
    void onSubmit({
      subjective: state.subjective,
      physical: state.physical,
      training: state.training,
      meal: state.meal,
    })
  }

  const alertPreview =
    state.step === 'confirm' && state.subjective && state.physical
      ? evaluateAlertPreview({ subjective: state.subjective, physical: state.physical })
      : null

  return (
    <div className="max-w-lg mx-auto">
      {/* Step indicator */}
      <div className="mb-6">
        <div className="flex justify-between text-xs text-gray-500 mb-2">
          {STEPS.map((s, i) => (
            <span
              key={s}
              className={`font-medium ${
                i === currentStepIdx ? 'text-blue-600' : i < currentStepIdx ? 'text-green-600' : ''
              }`}
            >
              {i < currentStepIdx ? '✓ ' : ''}{STEP_LABELS[s]}
            </span>
          ))}
        </div>
        <div className="w-full bg-gray-200 rounded-full h-1.5">
          <div
            className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Form steps */}
      {state.step === 'subjective' && (
        <SubjectiveForm
          defaultValues={state.subjective ?? undefined}
          onNext={data => dispatch({ type: 'SET_SUBJECTIVE', payload: data })}
          showFatigueBefore={settings.show_fatigue_before}
          showFatigueAfter={settings.show_fatigue_after}
        />
      )}

      {state.step === 'physical' && (
        <PhysicalForm
          defaultValues={state.physical ?? undefined}
          onNext={data => dispatch({ type: 'SET_PHYSICAL', payload: data })}
          onBack={() => dispatch({ type: 'BACK' })}
          showWeight={settings.show_weight}
          showBodyFat={settings.show_body_fat}
          showHeartRate={settings.show_heart_rate}
        />
      )}

      {state.step === 'training' && (
        <TrainingForm
          defaultValues={state.training ?? undefined}
          onNext={data => dispatch({ type: 'SET_TRAINING', payload: data })}
          onBack={() => dispatch({ type: 'BACK' })}
        />
      )}

      {state.step === 'meal' && (
        <MealForm
          defaultValues={state.meal ?? undefined}
          onNext={data => dispatch({ type: 'SET_MEAL', payload: data })}
          onBack={() => dispatch({ type: 'BACK' })}
          showAppetite={settings.show_appetite}
          showMealCount={settings.show_meal_count}
          showNutritionBalance={settings.show_nutrition_balance}
          showWaterMl={settings.show_water_ml}
          showMushroomSeaweed={settings.show_mushroom_seaweed}
          showCarbIntake={settings.show_carb_intake}
          showCarbSnack={settings.show_carb_snack}
          showProteinSource={settings.show_protein_source}
        />
      )}

      {state.step === 'confirm' &&
        state.subjective && state.physical && state.training && state.meal && (
        <div className="space-y-5">
          <div>
            <h2 className="text-lg font-semibold text-gray-800 mb-1">入力内容の確認</h2>
            <p className="text-sm text-gray-500">送信前に内容を確認してください</p>
          </div>

          {alertPreview?.severity && (
            <div
              className={`p-3 rounded-lg border text-sm ${
                alertPreview.severity === 'critical'
                  ? 'bg-red-50 border-red-200 text-red-700'
                  : 'bg-yellow-50 border-yellow-200 text-yellow-700'
              }`}
            >
              <p className="font-medium">
                {alertPreview.severity === 'critical' ? '⚠️ 体調に注意が必要です' : '📢 体調を気にかけてください'}
              </p>
              <p className="mt-0.5">
                {alertPreview.triggeredBy.join('・')} のスコアが気になります。コーチに通知されます。
              </p>
            </div>
          )}

          <div className="bg-gray-50 rounded-lg p-4 space-y-4 text-sm">
            <section>
              <p className="font-medium text-gray-700 mb-2">主観的体調</p>
              <div className="grid grid-cols-2 gap-2 text-gray-600">
                <span>起床時コンディション</span><span className="font-medium">{state.subjective.morning_condition} / 5</span>
                <span>練習前疲労度</span><span className="font-medium">{state.subjective.fatigue_before} / 5</span>
                <span>練習後疲労度</span><span className="font-medium">{state.subjective.fatigue_after} / 5</span>
                <span>睡眠の質</span><span className="font-medium">{state.subjective.sleep_quality} / 5</span>
                <span>睡眠時間</span><span className="font-medium">{state.subjective.sleep_hours}時間</span>
              </div>
            </section>

            <section>
              <p className="font-medium text-gray-700 mb-2">身体データ</p>
              <div className="grid grid-cols-2 gap-2 text-gray-600">
                <span>体重</span><span className="font-medium">{state.physical.weight_kg || '—'} kg</span>
                <span>体脂肪率</span><span className="font-medium">{state.physical.body_fat_pct || '—'} %</span>
                <span>安静時心拍</span><span className="font-medium">{state.physical.resting_heart_rate || '—'} bpm</span>
              </div>
            </section>

            <section>
              <p className="font-medium text-gray-700 mb-2">トレーニング</p>
              <div className="space-y-2">
                {state.training.map((entry, i) => (
                  <div key={i} className="grid grid-cols-2 gap-2 text-gray-600">
                    <span>種目</span>
                    <span className="font-medium">{TRAINING_TYPE_LABEL[entry.training_type] ?? entry.training_type}</span>
                    {entry.training_type !== 'rest' && (
                      <>
                        <span>時間</span><span className="font-medium">{entry.duration_min}分</span>
                        <span>RPE</span><span className="font-medium">{entry.rpe} / 10</span>
                        {entry.notes && <><span>メモ</span><span className="font-medium">{entry.notes}</span></>}
                      </>
                    )}
                  </div>
                ))}
              </div>
            </section>

            <section>
              <p className="font-medium text-gray-700 mb-2">食事</p>
              <div className="grid grid-cols-2 gap-2 text-gray-600">
                <span>練習後補食</span><span className="font-medium">{state.meal.post_exercise_meal ? 'あり' : 'なし'}</span>
                <span>食欲</span><span className="font-medium">{state.meal.appetite} / 5</span>
                <span>栄養バランス</span><span className="font-medium">{state.meal.nutrition_balance} / 5</span>
                <span>食事回数</span><span className="font-medium">{state.meal.meal_count}回</span>
                <span>水分摂取量</span><span className="font-medium">{state.meal.water_ml || '—'} ml</span>
                {state.meal.notes && (
                  <><span>メモ</span><span className="font-medium">{state.meal.notes}</span></>
                )}
              </div>
            </section>
          </div>

          <div className="flex justify-between">
            <Button type="button" variant="secondary" onClick={() => dispatch({ type: 'BACK' })}>
              ← 戻る
            </Button>
            <Button type="button" onClick={handleConfirm} disabled={isPending}>
              {isPending ? '送信中...' : '送信する ✓'}
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
