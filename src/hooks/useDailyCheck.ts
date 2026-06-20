import { useQuery, useMutation } from '@tanstack/react-query'
import { supabase } from '@/lib/supabase'
import { queryClient } from '@/lib/queryClient'
import { demoSubjective, demoPhysical, demoTraining, demoMeal } from '@/lib/demoData'
import { useAuth } from '@/hooks/useAuth'
import type { DailyCheckFormData } from '@/types/app.types'

export function useDailyCheck(athleteId: string, date: string) {
  const { isDemoMode } = useAuth()
  const query = useQuery({
    queryKey: ['dailyCheck', athleteId, date, isDemoMode],
    queryFn: async () => {
      if (isDemoMode) {
        return {
          subjective: demoSubjective.find(d => d.check_date === date) ?? null,
          physical: demoPhysical.find(d => d.check_date === date) ?? null,
          training: demoTraining.filter(d => d.log_date === date),
          meal: demoMeal.find(d => d.log_date === date) ?? null,
        }
      }

      const [subjRes, physRes, trainRes, mealRes] = await Promise.all([
        supabase.from('subjective_checks').select('*').eq('athlete_id', athleteId).eq('check_date', date).maybeSingle(),
        supabase.from('physical_checks').select('*').eq('athlete_id', athleteId).eq('check_date', date).maybeSingle(),
        supabase.from('training_logs').select('*').eq('athlete_id', athleteId).eq('log_date', date),
        supabase.from('meal_logs').select('*').eq('athlete_id', athleteId).eq('log_date', date).maybeSingle(),
      ])
      return {
        subjective: subjRes.data,
        physical: physRes.data,
        training: trainRes.data ?? [],
        meal: mealRes.data,
      }
    },
    enabled: !!athleteId && !!date,
  })

  const mutation = useMutation({
    mutationFn: async (formData: DailyCheckFormData) => {
      if (isDemoMode) return

      const parseNum = (s: string | undefined) =>
        s && s.trim() !== '' ? Number(s) : null

      // 既存レコードのIDを取得
      const [existSubj, existPhys, existTraining, existMeal] = await Promise.all([
        supabase.from('subjective_checks').select('id').eq('athlete_id', athleteId).eq('check_date', date).maybeSingle(),
        supabase.from('physical_checks').select('id').eq('athlete_id', athleteId).eq('check_date', date).maybeSingle(),
        supabase.from('training_logs').select('id, training_type').eq('athlete_id', athleteId).eq('log_date', date),
        supabase.from('meal_logs').select('id').eq('athlete_id', athleteId).eq('log_date', date).maybeSingle(),
      ])

      const subjData = {
        athlete_id: athleteId, check_date: date,
        morning_condition: formData.subjective.morning_condition,
        fatigue_before: formData.subjective.fatigue_before,
        fatigue_after: formData.subjective.fatigue_after,
        sleep_quality: formData.subjective.sleep_quality,
        sleep_hours: formData.subjective.sleep_hours,
      }
      const physData = {
        athlete_id: athleteId, check_date: date,
        weight_kg: parseNum(formData.physical.weight_kg),
        resting_heart_rate: parseNum(formData.physical.resting_heart_rate),
        body_fat_pct: parseNum(formData.physical.body_fat_pct),
      }
      const mealData = {
        athlete_id: athleteId, log_date: date,
        appetite: formData.meal.appetite,
        meal_count: formData.meal.meal_count,
        water_ml: parseNum(formData.meal.water_ml),
        nutrition_balance: formData.meal.nutrition_balance,
        post_exercise_meal: formData.meal.post_exercise_meal,
        mushroom_seaweed: formData.meal.mushroom_seaweed ?? null,
        carb_breakfast: formData.meal.carb_breakfast ?? null,
        carb_lunch: formData.meal.carb_lunch ?? null,
        carb_dinner: formData.meal.carb_dinner ?? null,
        carb_snack_wagashi: formData.meal.carb_snack_wagashi ?? null,
        carb_snack_fruit: formData.meal.carb_snack_fruit ?? null,
        carb_snack_juice_jelly: formData.meal.carb_snack_juice_jelly ?? null,
        carb_snack_other: formData.meal.carb_snack_other || null,
        protein_lunch_fish: formData.meal.protein_lunch_fish ?? null,
        protein_lunch_meat: formData.meal.protein_lunch_meat ?? null,
        protein_lunch_bean: formData.meal.protein_lunch_bean ?? null,
        protein_lunch_egg: formData.meal.protein_lunch_egg ?? null,
        protein_dinner_fish: formData.meal.protein_dinner_fish ?? null,
        protein_dinner_meat: formData.meal.protein_dinner_meat ?? null,
        protein_dinner_bean: formData.meal.protein_dinner_bean ?? null,
        protein_dinner_egg: formData.meal.protein_dinner_egg ?? null,
        notes: formData.meal.notes || null,
      }

      // トレーニング: 削除されたタイプを消し、新しいエントリをinsert/update
      const existingLogs = existTraining.data ?? []
      const newTypes = new Set(formData.training.map(t => t.training_type))
      const idsToDelete = existingLogs.filter(e => !newTypes.has(e.training_type)).map(e => e.id)

      const [subjRes, physRes, mealRes] = await Promise.all([
        existSubj.data?.id
          ? supabase.from('subjective_checks').update(subjData).eq('id', existSubj.data.id)
          : supabase.from('subjective_checks').insert(subjData),
        existPhys.data?.id
          ? supabase.from('physical_checks').update(physData).eq('id', existPhys.data.id)
          : supabase.from('physical_checks').insert(physData),
        existMeal.data?.id
          ? supabase.from('meal_logs').update(mealData).eq('id', existMeal.data.id)
          : supabase.from('meal_logs').insert(mealData),
      ])

      const baseError = subjRes.error ?? physRes.error ?? mealRes.error
      if (baseError) throw new Error(baseError.message)

      if (idsToDelete.length > 0) {
        const { error } = await supabase.from('training_logs').delete().in('id', idsToDelete)
        if (error) throw new Error(error.message)
      }

      for (const entry of formData.training) {
        const existing = existingLogs.find(e => e.training_type === entry.training_type)
        const trainData = {
          athlete_id: athleteId, log_date: date,
          training_type: entry.training_type,
          duration_min: entry.duration_min,
          rpe: entry.rpe,
          explosive_power: entry.explosive_power,
          endurance: entry.endurance,
          exercise_fatigue: entry.exercise_fatigue,
          notes: entry.notes || null,
        }
        const { error } = existing?.id
          ? await supabase.from('training_logs').update(trainData).eq('id', existing.id)
          : await supabase.from('training_logs').insert(trainData)
        if (error) throw new Error(error.message)
      }
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['dailyCheck', athleteId, date] })
      void queryClient.invalidateQueries({ queryKey: ['trends', athleteId] })
    },
  })

  return {
    data: query.data,
    isLoading: query.isLoading,
    submitCheck: mutation.mutateAsync,
    isPending: mutation.isPending,
  }
}
