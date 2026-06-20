import type { MealLog } from '@/types/app.types'

const PROTEIN_LABEL: Record<string, string> = {
  fish: '魚介', meat: '肉', bean: '豆', egg: '卵',
}

interface Props {
  data: MealLog[]
  showMushroomSeaweed?: boolean
  showCarbSnack?: boolean
  showProteinSource?: boolean
}

function BoolDot({ value }: { value: boolean | null }) {
  if (value === null || value === undefined) return <span className="text-gray-300">—</span>
  return (
    <span className={`inline-block w-4 h-4 rounded-full ${value ? 'bg-green-500' : 'bg-gray-200'}`} />
  )
}

function proteinLabels(log: MealLog, meal: 'lunch' | 'dinner') {
  const keys = ['fish', 'meat', 'bean', 'egg'] as const
  const active = keys.filter(k => log[`protein_${meal}_${k}` as keyof MealLog])
  return active.length > 0 ? active.map(k => PROTEIN_LABEL[k]).join('・') : '—'
}

export function MealCheckSummary({
  data,
  showMushroomSeaweed = true,
  showCarbSnack = true,
  showProteinSource = true,
}: Props) {
  const recent = [...data].reverse().slice(0, 7)

  if (recent.length === 0) {
    return <div className="flex items-center justify-center h-20 text-gray-400 text-sm">データがありません</div>
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs">
        <thead>
          <tr className="border-b border-gray-100">
            <th className="text-left py-2 pr-3 text-gray-500 font-medium whitespace-nowrap">日付</th>
            <th className="text-center py-2 px-2 text-gray-500 font-medium whitespace-nowrap">練習後補食</th>
            {showMushroomSeaweed && (
              <th className="text-center py-2 px-2 text-gray-500 font-medium whitespace-nowrap">きのこ・海藻</th>
            )}
            {showProteinSource && (
              <th className="text-left py-2 px-2 text-gray-500 font-medium whitespace-nowrap">昼タンパク質</th>
            )}
            {showProteinSource && (
              <th className="text-left py-2 px-2 text-gray-500 font-medium whitespace-nowrap">夕タンパク質</th>
            )}
            {showCarbSnack && (
              <th className="text-left py-2 px-2 text-gray-500 font-medium whitespace-nowrap">補食種類</th>
            )}
          </tr>
        </thead>
        <tbody>
          {recent.map(log => {
            const snacks = [
              log.carb_snack_wagashi && '和菓子',
              log.carb_snack_fruit && '果物',
              log.carb_snack_juice_jelly && 'ジュース・ゼリー',
              log.carb_snack_other,
            ].filter(Boolean).join('・')

            return (
              <tr key={log.id} className="border-b border-gray-50">
                <td className="py-2 pr-3 text-gray-600 whitespace-nowrap">{log.log_date.slice(5)}</td>
                <td className="py-2 px-2 text-center"><BoolDot value={log.post_exercise_meal} /></td>
                {showMushroomSeaweed && (
                  <td className="py-2 px-2 text-center"><BoolDot value={log.mushroom_seaweed} /></td>
                )}
                {showProteinSource && (
                  <td className="py-2 px-2 text-gray-600">{proteinLabels(log, 'lunch')}</td>
                )}
                {showProteinSource && (
                  <td className="py-2 px-2 text-gray-600">{proteinLabels(log, 'dinner')}</td>
                )}
                {showCarbSnack && (
                  <td className="py-2 px-2 text-gray-600">{snacks || '—'}</td>
                )}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
