import { createContext, useState, useEffect, type ReactNode } from 'react'
import { supabase } from '@/lib/supabase'
import type { Profile, UserRole } from '@/types/app.types'

const IS_DEMO_ENV = import.meta.env.VITE_SUPABASE_URL?.includes('your-project-id') ?? true

const DEMO_PROFILES: Record<UserRole, Profile> = {
  athlete: { id: 'mock-athlete-1', role: 'athlete', full_name: '山田 太郎', created_at: '' },
  coach:   { id: 'mock-coach-1',   role: 'coach',   full_name: '田中 コーチ', created_at: '' },
}

interface AuthContextValue {
  user: { id: string } | null
  profile: Profile | null
  isLoading: boolean
  isDemoMode: boolean
  demoRole: UserRole | null
  setDemoRole: (role: UserRole) => void
  enterDemoMode: (role: UserRole) => void
  exitDemoMode: () => void
  signIn: (email: string, password: string) => Promise<void>
  signOut: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isDemoMode, setIsDemoMode] = useState(IS_DEMO_ENV)
  const [user, setUser] = useState<{ id: string } | null>(IS_DEMO_ENV ? { id: 'mock-athlete-1' } : null)
  const [profile, setProfile] = useState<Profile | null>(IS_DEMO_ENV ? DEMO_PROFILES.athlete : null)
  const [isLoading, setIsLoading] = useState(!IS_DEMO_ENV)
  const [demoRole, setDemoRoleState] = useState<UserRole | null>(IS_DEMO_ENV ? 'athlete' : null)

  function setDemoRole(role: UserRole) {
    if (!isDemoMode) return
    setDemoRoleState(role)
    setUser({ id: DEMO_PROFILES[role].id })
    setProfile(DEMO_PROFILES[role])
  }

  function enterDemoMode(role: UserRole) {
    setIsDemoMode(true)
    setDemoRoleState(role)
    setUser({ id: DEMO_PROFILES[role].id })
    setProfile(DEMO_PROFILES[role])
  }

  function exitDemoMode() {
    setIsDemoMode(false)
    setDemoRoleState(null)
    setUser(null)
    setProfile(null)
  }

  useEffect(() => {
    if (IS_DEMO_ENV) return

    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user) {
        setUser({ id: session.user.id })
        void fetchProfile(session.user.id)
      }
      setIsLoading(false)
    })

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session?.user) {
        setUser({ id: session.user.id })
        void fetchProfile(session.user.id)
      } else {
        setUser(null)
        setProfile(null)
      }
    })

    return () => subscription.unsubscribe()
  }, [])

  async function fetchProfile(userId: string) {
    const { data } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', userId)
      .maybeSingle()
    setProfile(data ?? null)
  }

  async function signIn(email: string, password: string) {
    if (isDemoMode) return
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) throw error
  }

  async function signOut() {
    if (isDemoMode) {
      exitDemoMode()
      return
    }
    await supabase.auth.signOut()
  }

  return (
    <AuthContext.Provider value={{ user, profile, isLoading, isDemoMode, demoRole, setDemoRole, enterDemoMode, exitDemoMode, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  )
}
