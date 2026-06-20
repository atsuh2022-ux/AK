import { Controller, useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { subjectiveSchema, type SubjectiveFormValues } from '@/schemas/dailyCheck.schema'
import { Slider } from '@/components/ui/Slider'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'

interface Props {
  defaultValues?: Partial<SubjectiveFormValues>
  onNext: (data: SubjectiveFormValues) => void
  showFatigueBefore?: boolean
  showFatigueAfter?: boolean
}

export function SubjectiveForm({ defaultValues, onNext, showFatigueBefore = true, showFatigueAfter = true }: Props) {
  const { control, register, handleSubmit, formState: { errors } } = useForm<SubjectiveFormValues>({
    resolver: zodResolver(subjectiveSchema),
    defaultValues: {
      morning_condition: 3,
      fatigue_before: 3,
      fatigue_after: 3,
      sleep_quality: 3,
      sleep_hours: 7,
      ...defaultValues,
    },
  })

  return (
    <form onSubmit={handleSubmit(onNext)} className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-800 mb-1">主観的体調</h2>
        <p className="text-sm text-gray-500">各タイミングの疲労度を正直に教えてください</p>
      </div>

      <Controller
        name="morning_condition"
        control={control}
        render={({ field }) => (
          <Slider
            label="起床時のコンディション"
            value={field.value}
            onChange={field.onChange}
            leftLabel="とても良い"
            rightLabel="とても悪い"
            error={errors.morning_condition?.message}
          />
        )}
      />

      {(showFatigueBefore || showFatigueAfter) && (
        <div className="bg-blue-50 rounded-lg p-4 space-y-5">
          <p className="text-xs font-semibold text-blue-700 uppercase tracking-wide">疲労度</p>

          {showFatigueBefore && (
            <Controller
              name="fatigue_before"
              control={control}
              render={({ field }) => (
                <Slider
                  label="練習前"
                  value={field.value}
                  onChange={field.onChange}
                  leftLabel="元気"
                  rightLabel="疲れている"
                  error={errors.fatigue_before?.message}
                />
              )}
            />
          )}

          {showFatigueAfter && (
            <Controller
              name="fatigue_after"
              control={control}
              render={({ field }) => (
                <Slider
                  label="練習後"
                  value={field.value}
                  onChange={field.onChange}
                  leftLabel="元気"
                  rightLabel="疲れている"
                  error={errors.fatigue_after?.message}
                />
              )}
            />
          )}
        </div>
      )}

      <Controller
        name="sleep_quality"
        control={control}
        render={({ field }) => (
          <Slider
            label="睡眠の質"
            value={field.value}
            onChange={field.onChange}
            leftLabel="よく眠れた"
            rightLabel="眠れなかった"
            error={errors.sleep_quality?.message}
          />
        )}
      />

      <Input
        label="睡眠時間 (時間)"
        type="number"
        step="0.5"
        min="0"
        max="24"
        required
        hint="例: 7.5"
        error={errors.sleep_hours?.message}
        {...register('sleep_hours', { valueAsNumber: true })}
      />

      <div className="flex justify-end">
        <Button type="submit">次へ →</Button>
      </div>
    </form>
  )
}
