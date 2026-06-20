import { useQuery } from '@tanstack/react-query'
import { supabase } from '@/lib/supabase'
import { demoSubjective, demoPhysical, demoTraining, demoMeal } from '@/lib/demoData'
import { useAuth } from '@/hooks/useAuth'

export function useTrends(athleteId: string, days: 7 | 30 = 30) {
  const { isDemoMode } = useAuth()
  return useQuery({
    queryKey: ['trends', athleteId, days, isDemoMode],
    queryFn: async () => {
      if (isDemoMode) {
        return {
          subjective: demoSubjective,
          physical: demoPhysical,
          training: demoTraining,
          meal: demoMeal,
        }
      }

      const since = new Date()
      since.setDate(since.getDate() - days)
      const sinceStr = since.toISOString().split('T')[0]

      const [subjRes, physRes, trainRes, mealRes] = await Promise.all([
        supabase.from('subjective_checks').select('*').eq('athlete_id', athleteId).gte('check_date', sinceStr).order('check_date'),
        supabase.from('physical_checks').select('*').eq('athlete_id', athleteId).gte('check_date', sinceStr).order('check_date'),
        supabase.from('training_logs').select('*').eq('athlete_id', athleteId).gte('log_date', sinceStr).order('log_date'),
        supabase.from('meal_logs').select('*').eq('athlete_id', athleteId).gte('log_date', sinceStr).order('log_date'),
      ])

      return {
        subjective: subjRes.data ?? [],
        physical: physRes.data ?? [],
        training: trainRes.data ?? [],
        meal: mealRes.data ?? [],
      }
    },
    enabled: !!athleteId,
    staleTime: 5 * 60 * 1000,
  })
}
