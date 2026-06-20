import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { useAuth } from '@/hooks/useAuth'
import { useAlerts } from '@/hooks/useAlerts'

export function AppLayout() {
  const { profile, signOut } = useAuth()
  const { criticalCount } = useAlerts()
  const navigate = useNavigate()

  const isCoach = profile?.role === 'coach'

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* PC用サイドバー */}
      <div className="hidden md:block">
        <Sidebar />
      </div>

      {/* メインコンテンツ */}
      <main className="flex-1 overflow-auto pb-20 md:pb-0">
        <Outlet />
      </main>

      {/* モバイル用ボトムナビゲーション */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-gray-900 text-white border-t border-gray-700 z-50">
        <div className="flex">
          {isCoach ? (
            <NavLink
              to="/coach"
              className={({ isActive }) =>
                `flex-1 flex flex-col items-center py-3 text-xs gap-1 ${isActive ? 'text-blue-400' : 'text-gray-400'}`
              }
            >
              <span className="text-xl">👥</span>
              <span>チーム一覧</span>
              {criticalCount > 0 && (
                <span className="absolute top-1 bg-red-500 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">
                  {criticalCount}
                </span>
              )}
            </NavLink>
          ) : (
            <>
              <NavLink
                to="/check"
                className={({ isActive }) =>
                  `flex-1 flex flex-col items-center py-3 text-xs gap-1 ${isActive ? 'text-blue-400' : 'text-gray-400'}`
                }
              >
                <span className="text-xl">📋</span>
                <span>今日のチェック</span>
              </NavLink>
              <NavLink
                to="/dashboard"
                className={({ isActive }) =>
                  `flex-1 flex flex-col items-center py-3 text-xs gap-1 ${isActive ? 'text-blue-400' : 'text-gray-400'}`
                }
              >
                <span className="text-xl">📊</span>
                <span>ダッシュボード</span>
              </NavLink>
            </>
          )}
          <button
            onClick={() => void signOut().then(() => navigate('/login'))}
            className="flex-1 flex flex-col items-center py-3 text-xs gap-1 text-gray-400"
          >
            <span className="text-xl">🚪</span>
            <span>ログアウト</span>
          </button>
        </div>
      </nav>
    </div>
  )
}
