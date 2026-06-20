import { ALERT_THRESHOLDS } from '@/constants/alertThresholds'

export type AlertSeverity = 'warning' | 'critical' | null

export interface AlertPreview {
  severity: AlertSeverity
  triggeredBy: string[]
}

interface AlertInput {
  subjective: {
    fatigue_before: number
    fatigue_after: number
    sleep_quality: number
    sleep_hours: number
  }
  physical: { resting_heart_rate?: string }
}

export function evaluateAlertPreview(data: AlertInput): AlertPreview {
  const triggered: string[] = []
  let criticalCount = 0
  let warningCount = 0

  const { subjective, physical } = data

  // 練習後疲労度を最重視
  if (subjective.fatigue_after >= ALERT_THRESHOLDS.fatigue_level.critical) {
    triggered.push('練習後疲労度')
    criticalCount++
  } else if (subjective.fatigue_after >= ALERT_THRESHOLDS.fatigue_level.warning) {
    triggered.push('練習後疲労度')
    warningCount++
  }

  // 練習前疲労度
  if (subjective.fatigue_before >= ALERT_THRESHOLDS.fatigue_level.critical) {
    triggered.push('練習前疲労度')
    criticalCount++
  } else if (subjective.fatigue_before >= ALERT_THRESHOLDS.fatigue_level.warning) {
    triggered.push('練習前疲労度')
    warningCount++
  }

  if (subjective.sleep_quality <= ALERT_THRESHOLDS.sleep_quality.critical) {
    triggered.push('睡眠の質')
    criticalCount++
  } else if (subjective.sleep_quality <= ALERT_THRESHOLDS.sleep_quality.warning) {
    triggered.push('睡眠の質')
    warningCount++
  }

  if (subjective.sleep_hours < ALERT_THRESHOLDS.sleep_hours.critical) {
    triggered.push('睡眠時間')
    criticalCount++
  } else if (subjective.sleep_hours < ALERT_THRESHOLDS.sleep_hours.warning) {
    triggered.push('睡眠時間')
    warningCount++
  }

  const hr = physical.resting_heart_rate ? Number(physical.resting_heart_rate) : null
  if (hr !== null && hr > ALERT_THRESHOLDS.resting_heart_rate.critical) {
    triggered.push('安静時心拍数')
    criticalCount++
  } else if (hr !== null && hr > ALERT_THRESHOLDS.resting_heart_rate.warning) {
    triggered.push('安静時心拍数')
    warningCount++
  }

  if (triggered.length === 0) return { severity: null, triggeredBy: [] }

  const severity: AlertSeverity =
    criticalCount > 0 || warningCount >= 2 ? 'critical' : 'warning'

  return { severity, triggeredBy: triggered }
}
