import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { useAlerts } from '@/hooks/useAlerts'
import type { UserRole } from '@/types/app.types'

const IS_DEMO = import.meta.env.VITE_SUPABASE_URL?.includes('your-project-id') ?? true

const athleteLinks = [
  { to: '/check', label: '今日のチェック', icon: '📋' },
  { to: '/dashboard', label: 'マイダッシュボード', icon: '📊' },
]

const coachLinks = [
  { to: '/coach', label: 'チーム一覧', icon: '👥' },
]

export function Sidebar() {
  const { profile, demoRole, setDemoRole, signOut } = useAuth()
  const { criticalCount } = useAlerts()
  const navigate = useNavigate()
  const links = profile?.role === 'coach' ? coachLinks : athleteLinks

  function switchRole(role: UserRole) {
    setDemoRole(role)
    void navigate(role === 'coach' ? '/coach' : '/check')
  }

  return (
    <aside className="w-56 shrink-0 h-screen sticky top-0 bg-gray-900 text-white flex flex-col">
      <div className="p-4 border-b border-gray-700">
        <p className="text-xs text-gray-400 uppercase tracking-wider">久野選手 Condition</p>
        <p className="font-semibold truncate mt-0.5">{profile?.full_name}</p>
        <p className="text-xs text-gray-400">{profile?.role === 'coach' ? 'コーチ' : 'アスリート'}</p>
      </div>

      <nav className="flex-1 p-3 space-y-1">
        {links.map(link => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              `flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive ? 'bg-blue-600 text-white' : 'text-gray-300 hover:bg-gray-800'
              }`
            }
          >
            <span>{link.icon}</span>
            <span>{link.label}</span>
            {link.to === '/coach' && criticalCount > 0 && (
              <span className="ml-auto bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                {criticalCount}
              </span>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="p-3 border-t border-gray-700 space-y-1">
        {IS_DEMO ? (
          <>
            <p className="text-xs text-gray-500 px-1 mb-2">🛠 デモ切替</p>
            <button
              onClick={() => switchRole('athlete')}
              className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                demoRole === 'athlete' ? 'bg-blue-700 text-white' : 'text-gray-300 hover:bg-gray-800'
              }`}
            >
              <span>🏃</span><span>アスリート</span>
            </button>
            <button
              onClick={() => switchRole('coach')}
              className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                demoRole === 'coach' ? 'bg-blue-700 text-white' : 'text-gray-300 hover:bg-gray-800'
              }`}
            >
              <span>📋</span><span>コーチ</span>
            </button>
          </>
        ) : (
          <button
            onClick={() => void signOut()}
            className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-300 hover:bg-gray-800 transition-colors"
          >
            <span>🚪</span><span>ログアウト</span>
          </button>
        )}
      </div>
    </aside>
  )
}
