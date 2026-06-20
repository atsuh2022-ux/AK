import * as XLSX from 'xlsx'
import { supabase } from '@/lib/supabase'
import { TRAINING_TYPES } from '@/constants/alertThresholds'
import type { AthleteSettings } from '@/hooks/useAthleteSettings'

const TRAINING_LABEL = Object.fromEntries(TRAINING_TYPES.map(t => [t.value, t.label]))

const CARB_LABELS: Record<number, string> = {
  1: '主食なし', 2: '少なめ', 3: '普通', 4: '多め', 5: 'かなり多い',
}

export async function exportAthleteExcel(
  athleteId: string,
  athleteName: string,
  fromDate: string,
  toDate: string,
  settings?: AthleteSettings
) {
  const [subjRes, physRes, trainRes, mealRes] = await Promise.all([
    supabase.from('subjective_checks').select('*').eq('athlete_id', athleteId).gte('check_date', fromDate).lte('check_date', toDate).order('check_date'),
    supabase.from('physical_checks').select('*').eq('athlete_id', athleteId).gte('check_date', fromDate).lte('check_date', toDate).order('check_date'),
    supabase.from('training_logs').select('*').eq('athlete_id', athleteId).gte('log_date', fromDate).lte('log_date', toDate).order('log_date'),
    supabase.from('meal_logs').select('*').eq('athlete_id', athleteId).gte('log_date', fromDate).lte('log_date', toDate).order('log_date'),
  ])

  const s = settings

  const wb = XLSX.utils.book_new()

  // シート1: 主観的体調
  const subjRows = (subjRes.data ?? []).map(d => ({
    日付: d.check_date,
    起床時コンディション: d.morning_condition,
    ...(s?.show_fatigue_before !== false && { 練習前疲労度: d.fatigue_before }),
    ...(s?.show_fatigue_after !== false && { 練習後疲労度: d.fatigue_after }),
    睡眠の質: d.sleep_quality,
    睡眠時間: d.sleep_hours,
  }))
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(subjRows), '主観的体調')

  // シート2: 身体データ
  const physRows = (physRes.data ?? []).map(d => ({
    日付: d.check_date,
    ...(s?.show_weight !== false && { 体重_kg: d.weight_kg }),
    ...(s?.show_body_fat !== false && { 体脂肪率_pct: d.body_fat_pct }),
    ...(s?.show_heart_rate !== false && { 安静時心拍_bpm: d.resting_heart_rate }),
  }))
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(physRows), '身体データ')

  // シート3: トレーニング
  const trainRows = (trainRes.data ?? []).map(d => ({
    日付: d.log_date,
    種目: TRAINING_LABEL[d.training_type] ?? d.training_type,
    時間_分: d.duration_min,
    RPE: d.rpe,
    爆発力: d.explosive_power ?? '',
    持久力: d.endurance ?? '',
    運動後疲労: d.exercise_fatigue ?? '',
    メモ: d.notes ?? '',
  }))
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(trainRows), 'トレーニング')

  // シート4: 食事
  const mealRows = (mealRes.data ?? []).map(d => ({
    日付: d.log_date,
    練習後補食: d.post_exercise_meal ? 'はい' : 'いいえ',
    ...(s?.show_appetite !== false && { 食欲: d.appetite }),
    ...(s?.show_nutrition_balance !== false && { 栄養バランス: d.nutrition_balance }),
    ...(s?.show_meal_count !== false && { 食事回数: d.meal_count }),
    ...(s?.show_water_ml !== false && { 水分摂取量_ml: d.water_ml }),
    ...(s?.show_mushroom_seaweed !== false && { きのこ海藻: d.mushroom_seaweed ? 'はい' : 'いいえ' }),
    ...(s?.show_carb_intake !== false && {
      糖質_朝: CARB_LABELS[d.carb_breakfast] ?? d.carb_breakfast,
      糖質_昼: CARB_LABELS[d.carb_lunch] ?? d.carb_lunch,
      糖質_夕: CARB_LABELS[d.carb_dinner] ?? d.carb_dinner,
    }),
    ...(s?.show_carb_snack !== false && {
      補食_和菓子: d.carb_snack_wagashi ? '○' : '',
      補食_果物: d.carb_snack_fruit ? '○' : '',
      補食_ジュースゼリー: d.carb_snack_juice_jelly ? '○' : '',
      補食_その他: d.carb_snack_other ?? '',
    }),
    ...(s?.show_protein_source !== false && {
      昼タンパク質_魚: d.protein_lunch_fish ? '○' : '',
      昼タンパク質_肉: d.protein_lunch_meat ? '○' : '',
      昼タンパク質_豆: d.protein_lunch_bean ? '○' : '',
      昼タンパク質_卵: d.protein_lunch_egg ? '○' : '',
      夕タンパク質_魚: d.protein_dinner_fish ? '○' : '',
      夕タンパク質_肉: d.protein_dinner_meat ? '○' : '',
      夕タンパク質_豆: d.protein_dinner_bean ? '○' : '',
      夕タンパク質_卵: d.protein_dinner_egg ? '○' : '',
    }),
    メモ: d.notes ?? '',
  }))
  XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(mealRows), '食事')

  const fileName = `${athleteName}_${fromDate}_${toDate}.xlsx`
  XLSX.writeFile(wb, fileName)
}
