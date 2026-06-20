import { useAthleteList } from '@/hooks/useAthleteList'
import { AlertList } from '@/components/coach/AlertList'
import { AthleteCard } from '@/components/coach/AthleteCard'
import { Card } from '@/components/ui/Card'

export function CoachDashboardPage() {
  const { data: athletes, isLoading } = useAthleteList()

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-bold text-gray-900">チーム一覧</h1>
        <p className="text-sm text-gray-500">アスリートのコンディションを確認してください</p>
      </div>

      <Card>
        <p className="text-sm font-semibold text-gray-700 mb-3">アクティブなアラート</p>
        <AlertList />
      </Card>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
        </div>
      ) : (
        <div>
          <p className="text-sm font-semibold text-gray-700 mb-3">
            アスリート ({athletes?.length ?? 0}名)
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {athletes?.map(athlete => (
              <AthleteCard key={athlete.id} athlete={athlete} />
            ))}
            {athletes?.length === 0 && (
              <p className="text-sm text-gray-400 col-span-full py-4">アスリートが登録されていません</p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
