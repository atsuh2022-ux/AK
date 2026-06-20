import { useQuery, useMutation } from '@tanstack/react-query'
import { useEffect } from 'react'
import { supabase } from '@/lib/supabase'
import { queryClient } from '@/lib/queryClient'
import { useAuth } from '@/hooks/useAuth'
import { demoAlerts } from '@/lib/demoData'
import type { Alert } from '@/types/app.types'

export function useAlerts() {
  const { profile, isDemoMode } = useAuth()

  const query = useQuery({
    queryKey: ['alerts', isDemoMode],
    queryFn: async () => {
      if (isDemoMode) return demoAlerts

      const { data } = await supabase
        .from('alerts')
        .select('*, profiles!athlete_id(full_name)')
        .eq('acknowledged', false)
        .order('created_at', { ascending: false })
      return (data ?? []) as Alert[]
    },
    staleTime: 30 * 1000,
    enabled: profile?.role === 'coach',
  })

  useEffect(() => {
    if (profile?.role !== 'coach' || isDemoMode) return

    const channel = supabase
      .channel('alerts-realtime')
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'alerts' },
        () => {
          void queryClient.invalidateQueries({ queryKey: ['alerts'] })
        }
      )
      .subscribe()

    return () => {
      void supabase.removeChannel(channel)
    }
  }, [profile?.role, isDemoMode])

  const acknowledgeMutation = useMutation({
    mutationFn: async (alertId: string) => {
      if (isDemoMode) return
      await supabase
        .from('alerts')
        .update({
          acknowledged: true,
          acknowledged_by: profile?.id,
          acknowledged_at: new Date().toISOString(),
        })
        .eq('id', alertId)
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['alerts'] })
    },
  })

  return {
    alerts: query.data ?? [],
    criticalCount: (query.data ?? []).filter(a => a.severity === 'critical').length,
    acknowledge: acknowledgeMutation.mutate,
  }
}
