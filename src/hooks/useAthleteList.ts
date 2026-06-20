import { useQuery } from '@tanstack/react-query'
import { supabase } from '@/lib/supabase'
import { useAuth } from '@/hooks/useAuth'
import { demoAthleteList } from '@/lib/demoData'
import type { AthleteWithStatus } from '@/types/app.types'

export function useAthleteList() {
  const { isDemoMode } = useAuth()

  return useQuery({
    queryKey: ['athleteList', isDemoMode],
    queryFn: async () => {
      if (isDemoMode) return demoAthleteList

      const today = new Date().toISOString().split('T')[0]

      const { data: profiles } = await supabase
        .from('profiles')
        .select('*')
        .eq('role', 'athlete')
        .order('full_name')

      if (!profiles || profiles.length === 0) return [] as AthleteWithStatus[]

      const athleteIds = profiles.map(p => p.id)

      const [subjRes, alertRes, recentSubjRes] = await Promise.all([
        supabase
          .from('subjective_checks')
          .select('athlete_id')
          .in('athlete_id', athleteIds)
          .eq('check_date', today),
        supabase
          .from('alerts')
          .select('*')
          .in('athlete_id', athleteIds)
          .eq('acknowledged', false)
          .order('created_at', { ascending: false }),
        supabase
          .from('subjective_checks')
          .select('athlete_id, fatigue_after, check_date')
          .in('athlete_id', athleteIds)
          .gte(
            'check_date',
            new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
          )
          .order('check_date', { ascending: true }),
      ])

      const submittedIds = new Set((subjRes.data ?? []).map(s => s.athlete_id))
      const alertsByAthlete = new Map<string, typeof alertRes.data>()
      for (const a of alertRes.data ?? []) {
        if (!alertsByAthlete.has(a.athlete_id)) {
          alertsByAthlete.set(a.athlete_id, [])
        }
        alertsByAthlete.get(a.athlete_id)!.push(a)
      }

      const recentFatigueMap = new Map<string, number[]>()
      for (const r of recentSubjRes.data ?? []) {
        if (!recentFatigueMap.has(r.athlete_id)) {
          recentFatigueMap.set(r.athlete_id, [])
        }
        recentFatigueMap.get(r.athlete_id)!.push(r.fatigue_after)
      }

      return profiles.map(p => ({
        ...p,
        submitted_today: submittedIds.has(p.id),
        latest_alert: (alertsByAthlete.get(p.id)?.[0] ?? null) as AthleteWithStatus['latest_alert'],
        recent_fatigue: recentFatigueMap.get(p.id) ?? [],
      })) as AthleteWithStatus[]
    },
    staleTime: 60 * 1000,
  })
}
