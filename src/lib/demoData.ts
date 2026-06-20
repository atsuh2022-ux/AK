import type { SubjectiveCheck, PhysicalCheck, TrainingLog, MealLog, AthleteWithStatus, Alert } from '@/types/app.types'

const ATHLETE_ID = 'mock-athlete-1'

function dateStr(daysAgo: number): string {
  const d = new Date()
  d.setDate(d.getDate() - daysAgo)
  return d.toISOString().split('T')[0]
}

// 7日分（0=今日、6=6日前）
const DAYS = [6, 5, 4, 3, 2, 1, 0]

export const demoSubjective: SubjectiveCheck[] = [
  { id: 's1', athlete_id: ATHLETE_ID, check_date: dateStr(6), morning_condition: 2, fatigue_before: 2, fatigue_after: 3, sleep_quality: 2, sleep_hours: 7.5, created_at: '' },
  { id: 's2', athlete_id: ATHLETE_ID, check_date: dateStr(5), morning_condition: 2, fatigue_before: 2, fatigue_after: 4, sleep_quality: 2, sleep_hours: 7.0, created_at: '' },
  { id: 's3', athlete_id: ATHLETE_ID, check_date: dateStr(4), morning_condition: 1, fatigue_before: 2, fatigue_after: 2, sleep_quality: 1, sleep_hours: 8.5, created_at: '' },
  { id: 's4', athlete_id: ATHLETE_ID, check_date: dateStr(3), morning_condition: 3, fatigue_before: 3, fatigue_after: 5, sleep_quality: 3, sleep_hours: 6.5, created_at: '' },
  { id: 's5', athlete_id: ATHLETE_ID, check_date: dateStr(2), morning_condition: 4, fatigue_before: 4, fatigue_after: 4, sleep_quality: 4, sleep_hours: 5.5, created_at: '' },
  { id: 's6', athlete_id: ATHLETE_ID, check_date: dateStr(1), morning_condition: 3, fatigue_before: 3, fatigue_after: 3, sleep_quality: 2, sleep_hours: 7.5, created_at: '' },
  { id: 's7', athlete_id: ATHLETE_ID, check_date: dateStr(0), morning_condition: 2, fatigue_before: 2, fatigue_after: 3, sleep_quality: 2, sleep_hours: 8.0, created_at: '' },
]

export const demoPhysical: PhysicalCheck[] = DAYS.map((d, i) => ({
  id: `p${i}`,
  athlete_id: ATHLETE_ID,
  check_date: dateStr(d),
  weight_kg: parseFloat((70.2 - i * 0.1 + (i % 3 === 0 ? 0.3 : 0)).toFixed(1)),
  resting_heart_rate: [54, 56, 52, 60, 62, 57, 54][i],
  body_fat_pct: parseFloat((12.8 - i * 0.05).toFixed(1)),
  created_at: '',
}))

export const demoTraining: TrainingLog[] = [
  { id: 't1', athlete_id: ATHLETE_ID, log_date: dateStr(6), training_type: 'sprint', duration_min: 90, rpe: 6, explosive_power: 3, endurance: 3, exercise_fatigue: 3, notes: '60mダッシュ×8本', created_at: '' },
  { id: 't2', athlete_id: ATHLETE_ID, log_date: dateStr(5), training_type: 'weight', duration_min: 75, rpe: 7, explosive_power: 4, endurance: 2, exercise_fatigue: 3, notes: 'スクワット・クリーン中心', created_at: '' },
  { id: 't3', athlete_id: ATHLETE_ID, log_date: dateStr(4), training_type: 'rest', duration_min: 0, rpe: 1, explosive_power: null, endurance: null, exercise_fatigue: null, notes: null, created_at: '' },
  { id: 't4', athlete_id: ATHLETE_ID, log_date: dateStr(3), training_type: 'sprint', duration_min: 120, rpe: 9, explosive_power: 4, endurance: 4, exercise_fatigue: 5, notes: '100m全力走×5本、試合想定', created_at: '' },
  { id: 't5', athlete_id: ATHLETE_ID, log_date: dateStr(2), training_type: 'start', duration_min: 60, rpe: 7, explosive_power: 3, endurance: 2, exercise_fatigue: 4, notes: 'クラウチングスタート練習', created_at: '' },
  { id: 't6', athlete_id: ATHLETE_ID, log_date: dateStr(1), training_type: 'sprint', duration_min: 80, rpe: 6, explosive_power: 3, endurance: 3, exercise_fatigue: 3, notes: 'フォーム修正・ドリル', created_at: '' },
  { id: 't7', athlete_id: ATHLETE_ID, log_date: dateStr(0), training_type: 'sprint', duration_min: 90, rpe: 7, explosive_power: 4, endurance: 3, exercise_fatigue: 3, notes: null, created_at: '' },
]

export const demoMeal: MealLog[] = [
  { id: 'm1', athlete_id: ATHLETE_ID, log_date: dateStr(6), appetite: 2, meal_count: 4, water_ml: 2200, nutrition_balance: 2, post_exercise_meal: true, morning_protein: true, fish_dinner: false, mushroom_seaweed: true, carb_breakfast: 3, carb_lunch: 4, carb_dinner: 3, carb_snack_wagashi: true, carb_snack_fruit: false, carb_snack_juice_jelly: false, carb_snack_other: null, protein_lunch_fish: false, protein_lunch_meat: true, protein_lunch_bean: false, protein_lunch_egg: false, protein_dinner_fish: true, protein_dinner_meat: false, protein_dinner_bean: false, protein_dinner_egg: false, notes: null, hoshoku: null, created_at: '' },
  { id: 'm2', athlete_id: ATHLETE_ID, log_date: dateStr(5), appetite: 2, meal_count: 3, water_ml: 2000, nutrition_balance: 3, post_exercise_meal: false, morning_protein: true, fish_dinner: true, mushroom_seaweed: false, carb_breakfast: 2, carb_lunch: 3, carb_dinner: 3, carb_snack_wagashi: false, carb_snack_fruit: true, carb_snack_juice_jelly: false, carb_snack_other: null, protein_lunch_fish: true, protein_lunch_meat: false, protein_lunch_bean: false, protein_lunch_egg: true, protein_dinner_fish: true, protein_dinner_meat: false, protein_dinner_bean: false, protein_dinner_egg: false, notes: '夕食が遅くなった', hoshoku: null, created_at: '' },
  { id: 'm3', athlete_id: ATHLETE_ID, log_date: dateStr(4), appetite: 1, meal_count: 4, water_ml: 2500, nutrition_balance: 1, post_exercise_meal: null, morning_protein: false, fish_dinner: false, mushroom_seaweed: true, carb_breakfast: 3, carb_lunch: 3, carb_dinner: 4, carb_snack_wagashi: false, carb_snack_fruit: false, carb_snack_juice_jelly: false, carb_snack_other: null, protein_lunch_fish: false, protein_lunch_meat: true, protein_lunch_bean: true, protein_lunch_egg: false, protein_dinner_fish: false, protein_dinner_meat: true, protein_dinner_bean: false, protein_dinner_egg: false, notes: '休養日は食が進んだ', hoshoku: null, created_at: '' },
  { id: 'm4', athlete_id: ATHLETE_ID, log_date: dateStr(3), appetite: 3, meal_count: 3, water_ml: 2800, nutrition_balance: 2, post_exercise_meal: true, morning_protein: true, fish_dinner: true, mushroom_seaweed: false, carb_breakfast: 3, carb_lunch: 5, carb_dinner: 4, carb_snack_wagashi: true, carb_snack_fruit: false, carb_snack_juice_jelly: true, carb_snack_other: null, protein_lunch_fish: false, protein_lunch_meat: true, protein_lunch_bean: false, protein_lunch_egg: true, protein_dinner_fish: true, protein_dinner_meat: false, protein_dinner_bean: false, protein_dinner_egg: false, notes: 'プロテイン追加', hoshoku: null, created_at: '' },
  { id: 'm5', athlete_id: ATHLETE_ID, log_date: dateStr(2), appetite: 4, meal_count: 3, water_ml: 1800, nutrition_balance: 4, post_exercise_meal: false, morning_protein: false, fish_dinner: false, mushroom_seaweed: false, carb_breakfast: 2, carb_lunch: 2, carb_dinner: 2, carb_snack_wagashi: false, carb_snack_fruit: false, carb_snack_juice_jelly: false, carb_snack_other: null, protein_lunch_fish: false, protein_lunch_meat: false, protein_lunch_bean: false, protein_lunch_egg: true, protein_dinner_fish: false, protein_dinner_meat: true, protein_dinner_bean: false, protein_dinner_egg: false, notes: '食欲なし、疲労感強い', hoshoku: null, created_at: '' },
  { id: 'm6', athlete_id: ATHLETE_ID, log_date: dateStr(1), appetite: 2, meal_count: 4, water_ml: 2200, nutrition_balance: 2, post_exercise_meal: true, morning_protein: true, fish_dinner: true, mushroom_seaweed: true, carb_breakfast: 3, carb_lunch: 4, carb_dinner: 3, carb_snack_wagashi: false, carb_snack_fruit: true, carb_snack_juice_jelly: false, carb_snack_other: null, protein_lunch_fish: true, protein_lunch_meat: false, protein_lunch_bean: false, protein_lunch_egg: false, protein_dinner_fish: true, protein_dinner_meat: false, protein_dinner_bean: true, protein_dinner_egg: false, notes: null, hoshoku: null, created_at: '' },
  { id: 'm7', athlete_id: ATHLETE_ID, log_date: dateStr(0), appetite: 2, meal_count: 4, water_ml: 2400, nutrition_balance: 2, post_exercise_meal: true, morning_protein: true, fish_dinner: false, mushroom_seaweed: true, carb_breakfast: 3, carb_lunch: 3, carb_dinner: 4, carb_snack_wagashi: true, carb_snack_fruit: false, carb_snack_juice_jelly: false, carb_snack_other: 'おにぎり', protein_lunch_fish: false, protein_lunch_meat: true, protein_lunch_bean: false, protein_lunch_egg: true, protein_dinner_fish: false, protein_dinner_meat: true, protein_dinner_bean: false, protein_dinner_egg: true, notes: null, hoshoku: null, created_at: '' },
]

// コーチ向けデモデータ
export const demoAlerts: Alert[] = [
  {
    id: 'a1',
    athlete_id: ATHLETE_ID,
    alert_date: dateStr(2),
    severity: 'critical',
    triggered_by: ['練習後疲労度', '睡眠の質'],
    message: '練習後疲労度・睡眠の質が基準を超えています',
    acknowledged: false,
    acknowledged_by: null,
    acknowledged_at: null,
    created_at: '',
    profiles: { id: ATHLETE_ID, role: 'athlete', full_name: '久野 選手', created_at: '', show_hoshoku: false },
  },
]

export const demoAthleteList: AthleteWithStatus[] = [
  {
    id: ATHLETE_ID,
    role: 'athlete',
    full_name: '久野 選手',
    created_at: '',
    show_hoshoku: false,
    submitted_today: true,
    latest_alert: demoAlerts[0],
    recent_fatigue: demoSubjective.map(d => d.fatigue_after),
  },
]
