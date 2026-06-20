import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useAuth } from '@/hooks/useAuth'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'

const schema = z.object({
  email: z.string().email('メールアドレスの形式が正しくありません'),
  password: z.string().min(6, '6文字以上で入力してください'),
})

type FormValues = z.infer<typeof schema>

export function LoginPage() {
  const { user, profile, signIn, enterDemoMode } = useAuth()
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormValues>({
    resolver: zodResolver(schema),
  })

  if (user && profile) {
    return <Navigate to={profile.role === 'coach' ? '/coach' : '/check'} replace />
  }

  async function onSubmit(data: FormValues) {
    setError(null)
    try {
      await signIn(data.email, data.password)
    } catch {
      setError('メールアドレスまたはパスワードが正しくありません')
    }
  }

  function handleDemo(role: 'athlete' | 'coach') {
    enterDemoMode(role)
    void navigate(role === 'coach' ? '/coach' : '/check')
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900">久野選手 Condition</h1>
          <p className="text-sm text-gray-500 mt-1">100m短距離 コンディション管理</p>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <Input
              label="メールアドレス"
              type="email"
              autoComplete="email"
              required
              error={errors.email?.message}
              {...register('email')}
            />
            <Input
              label="パスワード"
              type="password"
              autoComplete="current-password"
              required
              error={errors.password?.message}
              {...register('password')}
            />

            {error && (
              <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg">{error}</p>
            )}

            <Button type="submit" className="w-full" disabled={isSubmitting} size="lg">
              {isSubmitting ? 'ログイン中...' : 'ログイン'}
            </Button>
          </form>
        </div>

        {/* デモセクション */}
        <div className="mt-6">
          <div className="flex items-center gap-3 mb-3">
            <div className="flex-1 h-px bg-gray-200" />
            <span className="text-xs text-gray-400">ログイン不要で試す</span>
            <div className="flex-1 h-px bg-gray-200" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => handleDemo('athlete')}
              className="flex flex-col items-center gap-1 p-4 bg-white rounded-xl border border-gray-200 shadow-sm active:bg-gray-50"
            >
              <span className="text-2xl">🏃</span>
              <span className="text-sm font-medium text-gray-700">アスリートデモ</span>
              <span className="text-xs text-gray-400">コンディション入力</span>
            </button>
            <button
              onClick={() => handleDemo('coach')}
              className="flex flex-col items-center gap-1 p-4 bg-white rounded-xl border border-gray-200 shadow-sm active:bg-gray-50"
            >
              <span className="text-2xl">👥</span>
              <span className="text-sm font-medium text-gray-700">コーチデモ</span>
              <span className="text-xs text-gray-400">チーム管理</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
