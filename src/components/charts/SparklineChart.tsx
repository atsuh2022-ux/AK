import { LineChart, Line, ResponsiveContainer } from 'recharts'

interface Props {
  data: number[]
}

export function SparklineChart({ data }: Props) {
  const chartData = data.map((v, i) => ({ i, v }))

  if (chartData.length < 2) {
    return <div className="h-8 flex items-center text-xs text-gray-400">データなし</div>
  }

  return (
    <ResponsiveContainer width="100%" height={32}>
      <LineChart data={chartData}>
        <Line
          type="monotone"
          dataKey="v"
          stroke="#ef4444"
          strokeWidth={1.5}
          dot={false}
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
