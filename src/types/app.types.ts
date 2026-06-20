export type UserRole = 'athlete' | 'coach'

export interface Profile {
  id: string
  role: UserRole
  full_name: string
  created_at: string
}

export interface SubjectiveCheck {
  id: string
  athlete_id: string
  check_date: string
  morning_condition: number
  fatigue_before: number
  fatigue_after: number
  sleep_quality: number
  sleep_hours: number
  created_at: string
}

export interface PhysicalCheck {
  id: string
  athlete_id: string
  check_date: string
  weight_kg: number | null
  resting_heart_rate: number | null
  body_fat_pct: number | null
  created_at: string
}

export interface TrainingLog {
  id: string
  athlete_id: string
  log_date: string
  training_type: string
  duration_min: number
  rpe: number
  explosive_power: number | null
  endurance: number | null
  exercise_fatigue: number | null
  notes: string | null
  created_at: string
}

export interface MealLog {
  id: string
  athlete_id: string
  log_date: string
  appetite: number
  meal_count: number
  water_ml: number | null
  nutrition_balance: number
  post_exercise_meal: boolean | null
  morning_protein: boolean | null
  fish_dinner: boolean | null
  carb_breakfast: number | null
  carb_lunch: number | null
  carb_dinner: number | null
  mushroom_seaweed: boolean | null
  carb_snack_wagashi: boolean | null
  carb_snack_fruit: boolean | null
  carb_snack_juice_jelly: boolean | null
  carb_snack_other: string | null
  protein_lunch_fish: boolean | null
  protein_lunch_meat: boolean | null
  protein_lunch_bean: boolean | null
  protein_lunch_egg: boolean | null
  protein_dinner_fish: boolean | null
  protein_dinner_meat: boolean | null
  protein_dinner_bean: boolean | null
  protein_dinner_egg: boolean | null
  notes: string | null
  created_at: string
}

export interface Alert {
  id: string
  athlete_id: string
  alert_date: string
  severity: 'warning' | 'critical'
  triggered_by: string[]
  message: string
  acknowledged: boolean
  acknowledged_by: string | null
  acknowledged_at: string | null
  created_at: string
  profiles?: Profile
}

export interface AthleteWithStatus extends Profile {
  submitted_today: boolean
  latest_alert: Alert | null
  recent_fatigue: number[]
}

export interface TrainingEntry {
  training_type: string
  duration_min: number
  rpe: number
  explosive_power: number
  endurance: number
  exercise_fatigue: number
  notes?: string
}

export interface DailyCheckFormData {
  subjective: {
    morning_condition: number
    fatigue_before: number
    fatigue_after: number
    sleep_quality: number
    sleep_hours: number
  }
  physical: {
    weight_kg?: string
    resting_heart_rate?: string
    body_fat_pct?: string
  }
  training: TrainingEntry[]
  meal: {
    appetite: number
    meal_count: number
    water_ml?: string
    nutrition_balance: number
    post_exercise_meal: boolean
    mushroom_seaweed?: boolean
    carb_breakfast?: number
    carb_lunch?: number
    carb_dinner?: number
    carb_snack_wagashi?: boolean
    carb_snack_fruit?: boolean
    carb_snack_juice_jelly?: boolean
    carb_snack_other?: string
    protein_lunch_fish?: boolean
    protein_lunch_meat?: boolean
    protein_lunch_bean?: boolean
    protein_lunch_egg?: boolean
    protein_dinner_fish?: boolean
    protein_dinner_meat?: boolean
    protein_dinner_bean?: boolean
    protein_dinner_egg?: boolean
    notes?: string
  }
}
