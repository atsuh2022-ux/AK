import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { physicalSchema, type PhysicalFormValues } from '@/schemas/dailyCheck.schema'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'

interface Props {
  defaultValues?: Partial<PhysicalFormValues>
  onNext: (data: PhysicalFormValues) => void
  onBack: () => void
  showWeight?: boolean
  showBodyFat?: boolean
  showHeartRate?: boolean
}

export function PhysicalForm({ defaultValues, onNext, onBack, showWeight = true, showBodyFat = true, showHeartRate = true }: Props) {
  const { register, handleSubmit, formState: { errors } } = useForm<PhysicalFormValues>({
    resolver: zodResolver(physicalSchema),
    defaultValues,
  })

  return (
    <form onSubmit={handleSubmit(onNext)} className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-800 mb-1">身体データ</h2>
        <p className="text-sm text-gray-500">計測できた項目だけ入力してください（任意）</p>
      </div>

      {showWeight && (
        <Input
          label="体重 (kg)"
          type="number"
          step="0.1"
          min="20"
          max="300"
          placeholder="例: 65.5"
          hint="朝起床後に計測した体重"
          error={errors.weight_kg?.message}
          {...register('weight_kg')}
        />
      )}

      {showBodyFat && (
        <Input
          label="体脂肪率 (%)"
          type="number"
          step="0.1"
          min="1"
          max="60"
          placeholder="例: 12.5"
          hint="体組成計で計測した値"
          error={errors.body_fat_pct?.message}
          {...register('body_fat_pct')}
        />
      )}

      {showHeartRate && (
        <Input
          label="安静時心拍数 (bpm)"
          type="number"
          min="30"
          max="200"
          placeholder="例: 55"
          hint="起床直後の心拍数"
          error={errors.resting_heart_rate?.message}
          {...register('resting_heart_rate')}
        />
      )}

      <div className="flex justify-between">
        <Button type="button" variant="secondary" onClick={onBack}>← 戻る</Button>
        <Button type="submit">次へ →</Button>
      </div>
    </form>
  )
}
