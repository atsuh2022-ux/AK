export const ALERT_THRESHOLDS = {
  fatigue_level: { critical: 4, warning: 3 },
  sleep_quality: { critical: 2, warning: 3 },
  mood: { critical: 2, warning: 3 },
  sleep_hours: { critical: 5, warning: 6 },
  resting_heart_rate: { critical: 75, warning: 70 },
  hrv_deviation_pct: { critical: 25, warning: 15 },
} as const

export const TRAINING_TYPES = [
  { value: 'sprint', label: '短距離ダッシュ' },
  { value: 'start', label: 'スタート練習' },
  { value: 'weight', label: 'ウエイトトレーニング' },
  { value: 'rest', label: '休養日' },
] as const
