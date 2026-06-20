import { useQuery, useMutation } from '@tanstack/react-query'
import { supabase } from '@/lib/supabase'
import { queryClient } from '@/lib/queryClient'
import { useAuth } from '@/hooks/useAuth'

export interface AthleteSettings {
  athlete_id: string
  show_weight: boolean
  show_body_fat: boolean
  show_heart_rate: boolean
  show_fatigue_before: boolean
  show_fatigue_after: boolean
  show_appetite: boolean
  show_meal_count: boolean
  show_nutrition_balance: boolean
  show_water_ml: boolean
  show_mushroom_seaweed: boolean
  show_carb_intake: boolean
  show_carb_snack: boolean
  show_protein_source: boolean
}

const DEFAULT_SETTINGS: Omit<AthleteSettings, 'athlete_id'> = {
  show_weight: true,
  show_body_fat: true,
  show_heart_rate: true,
  show_fatigue_before: true,
  show_fatigue_after: true,
  show_appetite: true,
  show_meal_count: true,
  show_nutrition_balance: true,
  show_water_ml: true,
  show_mushroom_seaweed: true,
  show_carb_intake: true,
  show_carb_snack: true,
  show_protein_source: true,
}

export function useAthleteSettings(athleteId: string) {
  const { isDemoMode } = useAuth()

  const query = useQuery({
    queryKey: ['athleteSettings', athleteId],
    queryFn: async (): Promise<AthleteSettings> => {
      if (isDemoMode) return { athlete_id: athleteId, ...DEFAULT_SETTINGS }

      const { data } = await supabase
        .from('athlete_settings')
        .select('*')
        .eq('athlete_id', athleteId)
        .maybeSingle()

      return data ?? { athlete_id: athleteId, ...DEFAULT_SETTINGS }
    },
    enabled: !!athleteId,
  })

  const mutation = useMutation({
    mutationFn: async (settings: Partial<Omit<AthleteSettings, 'athlete_id'>>) => {
      if (isDemoMode) return

      await supabase
        .from('athlete_settings')
        .upsert({ athlete_id: athleteId, ...settings }, { onConflict: 'athlete_id' })
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['athleteSettings', athleteId] })
    },
  })

  return {
    settings: query.data ?? { athlete_id: athleteId, ...DEFAULT_SETTINGS },
    isLoading: query.isLoading,
    updateSettings: mutation.mutateAsync,
    isUpdating: mutation.isPending,
  }
}
