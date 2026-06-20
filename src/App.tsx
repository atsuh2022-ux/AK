import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'sonner'
import { queryClient } from '@/lib/queryClient'
import { AuthProvider } from '@/contexts/AuthContext'
import { AppLayout } from '@/components/layout/AppLayout'
import { ProtectedRoute } from '@/components/layout/ProtectedRoute'
import { LoginPage } from '@/pages/LoginPage'
import { DailyCheckPage } from '@/pages/athlete/DailyCheckPage'
import { MyDashboardPage } from '@/pages/athlete/MyDashboardPage'
import { CoachDashboardPage } from '@/pages/coach/CoachDashboardPage'
import { AthleteDetailPage } from '@/pages/coach/AthleteDetailPage'

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route element={<ProtectedRoute />}>
              <Route element={<AppLayout />}>
                <Route path="/check" element={<DailyCheckPage />} />
                <Route path="/dashboard" element={<MyDashboardPage />} />
                <Route path="/coach" element={<CoachDashboardPage />} />
                <Route path="/coach/athlete/:id" element={<AthleteDetailPage />} />
              </Route>
            </Route>
            <Route path="*" element={<Navigate to="/check" replace />} />
          </Routes>
        </BrowserRouter>
        <Toaster richColors position="top-right" />
      </AuthProvider>
    </QueryClientProvider>
  )
}
