interface Props {
  submitted: boolean
}

export function TodayStatus({ submitted }: Props) {
  return submitted ? (
    <span className="text-xs text-green-600 font-medium">✓ 提出済み</span>
  ) : (
    <span className="text-xs text-gray-400">未提出</span>
  )
}
