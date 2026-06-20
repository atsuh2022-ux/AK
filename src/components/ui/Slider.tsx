interface SliderProps {
  label: string
  value: number
  onChange: (value: number) => void
  min?: number
  max?: number
  step?: number
  leftLabel?: string
  rightLabel?: string
  error?: string
}

const EMOJIS: Record<number, string> = {
  1: '😊',
  2: '🙂',
  3: '😐',
  4: '😟',
  5: '😰',
}

export function Slider({
  label,
  value,
  onChange,
  min = 1,
  max = 5,
  leftLabel,
  rightLabel,
  error,
}: SliderProps) {

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-gray-700">{label}</label>
        <span className="text-2xl" title={`${value}/${max}`}>
          {EMOJIS[value] ?? value}
        </span>
      </div>

      {/* 数字ボタン */}
      <div className="flex gap-2 justify-between">
        {Array.from({ length: max - min + 1 }, (_, i) => i + min).map(v => (
          <button
            key={v}
            type="button"
            onClick={() => onChange(v)}
            className={`flex-1 py-3 rounded-xl text-sm font-bold transition-colors ${
              value === v
                ? 'bg-blue-600 text-white shadow-sm'
                : 'bg-gray-100 text-gray-600 active:bg-gray-200'
            }`}
          >
            {v}
          </button>
        ))}
      </div>

      {/* ラベル */}
      <div className="flex justify-between text-xs text-gray-400">
        <span>{leftLabel ?? String(min)}</span>
        <span>{rightLabel ?? String(max)}</span>
      </div>

      {error && <p className="text-xs text-red-600">{error}</p>}
    </div>
  )
}
