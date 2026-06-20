import { Controller, useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { mealSchema, type MealFormValues } from '@/schemas/dailyCheck.schema'
import { Slider } from '@/components/ui/Slider'
import { Button } from '@/components/ui/Button'

interface Props {
  defaultValues?: Partial<MealFormValues>
  onNext: (data: MealFormValues) => void
  onBack: () => void
  showAppetite?: boolean
  showMealCount?: boolean
  showNutritionBalance?: boolean
  showWaterMl?: boolean
  showMushroomSeaweed?: boolean
  showCarbIntake?: boolean
  showCarbSnack?: boolean
  showProteinSource?: boolean
  showHoshoku?: boolean
}

const MEAL_COUNT_OPTIONS = [1, 2, 3, 4, 5, 6]
const WATER_OPTIONS = [
  { label: '500ml以下', value: '500' },
  { label: '1L', value: '1000' },
  { label: '1.5L', value: '1500' },
  { label: '2L以上', value: '2000' },
]

const CARB_OPTIONS = [
  { value: 1, label: '主食なし' },
  { value: 2, label: '少なめ' },
  { value: 3, label: '普通' },
  { value: 4, label: '多め' },
  { value: 5, label: 'かなり多い' },
]

export function MealForm({
  defaultValues, onNext, onBack,
  showAppetite = true, showMealCount = true, showNutritionBalance = true, showWaterMl = true,
  showMushroomSeaweed = true, showCarbIntake = true, showCarbSnack = true, showProteinSource = true,
  showHoshoku = false,
}: Props) {
  const { control, register, setValue, watch, handleSubmit, formState: { errors } } = useForm<MealFormValues>({
    resolver: zodResolver(mealSchema),
    defaultValues: {
      appetite: 3,
      meal_count: 3,
      water_ml: '',
      nutrition_balance: 3,
      post_exercise_meal: false,
      notes: '',
      ...defaultValues,
    },
  })

  const mealCount = watch('meal_count')
  const waterMl = watch('water_ml')
  const postExerciseMeal = watch('post_exercise_meal')
  const mushroomSeaweed = watch('mushroom_seaweed')
  const carbBreakfast = watch('carb_breakfast')
  const carbLunch = watch('carb_lunch')
  const carbDinner = watch('carb_dinner')
  const carbSnackWagashi = watch('carb_snack_wagashi')
  const carbSnackFruit = watch('carb_snack_fruit')
  const carbSnackJuiceJelly = watch('carb_snack_juice_jelly')
  const carbSnackOther = watch('carb_snack_other')
  const proteinLunchFish = watch('protein_lunch_fish')
  const proteinLunchMeat = watch('protein_lunch_meat')
  const proteinLunchBean = watch('protein_lunch_bean')
  const proteinLunchEgg = watch('protein_lunch_egg')
  const proteinDinnerFish = watch('protein_dinner_fish')
  const proteinDinnerMeat = watch('protein_dinner_meat')
  const proteinDinnerBean = watch('protein_dinner_bean')
  const proteinDinnerEgg = watch('protein_dinner_egg')

  return (
    <form onSubmit={handleSubmit(onNext)} className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-800 mb-1">食事</h2>
        <p className="text-sm text-gray-500">今日の食事・栄養状態を記録してください</p>
      </div>

      {/* 練習後30分以内の補食 */}
      <div>
        <p className="text-sm font-medium text-gray-700 mb-2">練習後30分以内に食事・補食を摂りましたか？</p>
        <div className="flex gap-3">
          <button
            type="button"
            onClick={() => setValue('post_exercise_meal', true)}
            className={`flex-1 py-3 rounded-xl text-sm font-bold border-2 transition-colors ${
              postExerciseMeal ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 border-gray-200'
            }`}
          >
            はい
          </button>
          <button
            type="button"
            onClick={() => setValue('post_exercise_meal', false)}
            className={`flex-1 py-3 rounded-xl text-sm font-bold border-2 transition-colors ${
              !postExerciseMeal ? 'bg-gray-800 text-white border-gray-800' : 'bg-white text-gray-600 border-gray-200'
            }`}
          >
            いいえ
          </button>
        </div>
      </div>

      {showAppetite && (
        <Controller
          name="appetite"
          control={control}
          render={({ field }) => (
            <Slider
              label="食欲"
              value={field.value}
              onChange={field.onChange}
              leftLabel="旺盛"
              rightLabel="なし"
              error={errors.appetite?.message}
            />
          )}
        />
      )}

      {showNutritionBalance && (
        <Controller
          name="nutrition_balance"
          control={control}
          render={({ field }) => (
            <Slider
              label="栄養バランス（自己評価）"
              value={field.value}
              onChange={field.onChange}
              leftLabel="良い"
              rightLabel="偏っている"
              error={errors.nutrition_balance?.message}
            />
          )}
        />
      )}

      {/* 食事回数 */}
      {showMealCount && (
        <div>
          <p className="text-sm font-medium text-gray-700 mb-2">食事回数（間食含む）</p>
          <div className="flex gap-2">
            {MEAL_COUNT_OPTIONS.map(n => (
              <button
                key={n}
                type="button"
                onClick={() => setValue('meal_count', n)}
                className={`flex-1 py-3 rounded-xl text-sm font-bold transition-colors ${
                  mealCount === n ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'
                }`}
              >
                {n}
              </button>
            ))}
          </div>
          {errors.meal_count && <p className="text-xs text-red-600 mt-1">{errors.meal_count.message}</p>}
        </div>
      )}

      {/* 水分摂取量 */}
      {showWaterMl && (
        <div>
          <p className="text-sm font-medium text-gray-700 mb-2">水分摂取量</p>
          <div className="grid grid-cols-3 gap-2">
            {WATER_OPTIONS.map(opt => (
              <button
                key={opt.value}
                type="button"
                onClick={() => setValue('water_ml', opt.value)}
                className={`py-2.5 rounded-xl text-xs font-bold transition-colors ${
                  waterMl === opt.value ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* きのこ・海藻類 */}
      {showMushroomSeaweed && (
        <div>
          <p className="text-sm font-medium text-gray-700 mb-2">きのこ・海藻類を摂りましたか？</p>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => setValue('mushroom_seaweed', true)}
              className={`flex-1 py-3 rounded-xl text-sm font-bold border-2 transition-colors ${
                mushroomSeaweed ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 border-gray-200'
              }`}
            >
              はい
            </button>
            <button
              type="button"
              onClick={() => setValue('mushroom_seaweed', false)}
              className={`flex-1 py-3 rounded-xl text-sm font-bold border-2 transition-colors ${
                mushroomSeaweed === false ? 'bg-gray-800 text-white border-gray-800' : 'bg-white text-gray-600 border-gray-200'
              }`}
            >
              いいえ
            </button>
          </div>
        </div>
      )}

      {/* 糖質摂取量 */}
      {showCarbIntake && (
        <div className="space-y-4">
          <p className="text-sm font-semibold text-gray-700">糖質摂取量（主食の量）</p>
          {([
            { field: 'carb_breakfast', label: '朝食', value: carbBreakfast },
            { field: 'carb_lunch', label: '昼食', value: carbLunch },
            { field: 'carb_dinner', label: '夕食', value: carbDinner },
          ] as const).map(({ field, label, value }) => (
            <div key={field}>
              <p className="text-xs font-medium text-gray-500 mb-1.5">{label}</p>
              <div className="flex gap-1.5">
                {CARB_OPTIONS.map(opt => (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => setValue(field, opt.value)}
                    className={`flex-1 py-2 rounded-lg text-xs font-bold transition-colors ${
                      value === opt.value ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 糖質メインの補食 */}
      {showCarbSnack && (
        <div>
          <p className="text-sm font-medium text-gray-700 mb-2">糖質メインの補食を摂りましたか？（複数選択可）</p>
          <div className="flex flex-wrap gap-2 mb-3">
            {[
              { field: 'carb_snack_wagashi' as const, label: '和菓子', value: carbSnackWagashi },
              { field: 'carb_snack_fruit' as const, label: '果物', value: carbSnackFruit },
              { field: 'carb_snack_juice_jelly' as const, label: 'ジュース・ゼリー', value: carbSnackJuiceJelly },
            ].map(({ field, label, value }) => (
              <button
                key={field}
                type="button"
                onClick={() => setValue(field, !value)}
                className={`px-4 py-2.5 rounded-xl text-sm font-bold border-2 transition-colors ${
                  value ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 border-gray-200'
                }`}
              >
                {value ? '✓ ' : ''}{label}
              </button>
            ))}
          </div>
          <div className="flex items-start gap-2">
            <button
              type="button"
              onClick={() => setValue('carb_snack_other', carbSnackOther ? '' : ' ')}
              className={`shrink-0 px-4 py-2.5 rounded-xl text-sm font-bold border-2 transition-colors ${
                carbSnackOther ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 border-gray-200'
              }`}
            >
              {carbSnackOther ? '✓ ' : ''}その他
            </button>
            {carbSnackOther !== undefined && carbSnackOther !== '' && (
              <input
                type="text"
                placeholder="補食の内容を入力"
                className="flex-1 px-3 py-2.5 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                {...register('carb_snack_other')}
              />
            )}
          </div>
        </div>
      )}

      {/* タンパク質源 */}
      {showProteinSource && (
        <div className="space-y-4">
          <p className="text-sm font-semibold text-gray-700">主菜のタンパク質源（複数選択可）</p>
          {([
            {
              label: '昼食',
              items: [
                { field: 'protein_lunch_fish' as const, label: '魚介類', value: proteinLunchFish },
                { field: 'protein_lunch_meat' as const, label: '肉類', value: proteinLunchMeat },
                { field: 'protein_lunch_bean' as const, label: '豆類', value: proteinLunchBean },
                { field: 'protein_lunch_egg' as const, label: '卵類', value: proteinLunchEgg },
              ],
            },
            {
              label: '夕食',
              items: [
                { field: 'protein_dinner_fish' as const, label: '魚介類', value: proteinDinnerFish },
                { field: 'protein_dinner_meat' as const, label: '肉類', value: proteinDinnerMeat },
                { field: 'protein_dinner_bean' as const, label: '豆類', value: proteinDinnerBean },
                { field: 'protein_dinner_egg' as const, label: '卵類', value: proteinDinnerEgg },
              ],
            },
          ]).map(({ label, items }) => (
            <div key={label}>
              <p className="text-xs font-medium text-gray-500 mb-1.5">{label}</p>
              <div className="flex gap-2">
                {items.map(({ field, label: itemLabel, value }) => (
                  <button
                    key={field}
                    type="button"
                    onClick={() => setValue(field, !value)}
                    className={`flex-1 py-2.5 rounded-xl text-xs font-bold border-2 transition-colors ${
                      value ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-gray-600 border-gray-200'
                    }`}
                  >
                    {value ? '✓ ' : ''}{itemLabel}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="flex flex-col gap-1">
        <label className="text-sm font-medium text-gray-700">メモ（任意）</label>
        <textarea
          rows={2}
          placeholder="食事内容・気になること など"
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          {...register('notes')}
        />
      </div>

      {showHoshoku && (
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">補食（食べた場合は記入してください）</label>
          <textarea
            rows={2}
            placeholder="例: おにぎり1個、バナナ1本"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            {...register('hoshoku')}
          />
        </div>
      )}

      <div className="flex justify-between">
        <Button type="button" variant="secondary" onClick={onBack}>← 戻る</Button>
        <Button type="submit">確認 →</Button>
      </div>
    </form>
  )
}
