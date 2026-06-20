import { z } from 'zod'

export const subjectiveSchema = z.object({
  morning_condition: z.number().int().min(1).max(5),
  fatigue_before: z.number().int().min(1).max(5),
  fatigue_after: z.number().int().min(1).max(5),
  sleep_quality: z.number().int().min(1).max(5),
  sleep_hours: z.number().min(0).max(24),
})

export const physicalSchema = z.object({
  weight_kg: z.string().optional(),
  resting_heart_rate: z.string().optional(),
  body_fat_pct: z.string().optional(),
})

export const trainingSchema = z.object({
  training_type: z.string().min(1, 'トレーニング種目を選択してください'),
  duration_min: z.number().int().min(1, '時間を入力してください'),
  rpe: z.number().int().min(1).max(10),
  notes: z.string().optional(),
})

export const mealSchema = z.object({
  appetite: z.number().int().min(1).max(5),
  meal_count: z.number().int().min(1).max(10),
  water_ml: z.string().optional(),
  nutrition_balance: z.number().int().min(1).max(5),
  post_exercise_meal: z.boolean(),
  mushroom_seaweed: z.boolean().optional(),
  carb_breakfast: z.number().int().min(1).max(5).optional(),
  carb_lunch: z.number().int().min(1).max(5).optional(),
  carb_dinner: z.number().int().min(1).max(5).optional(),
  carb_snack_wagashi: z.boolean().optional(),
  carb_snack_fruit: z.boolean().optional(),
  carb_snack_juice_jelly: z.boolean().optional(),
  carb_snack_other: z.string().optional(),
  protein_lunch_fish: z.boolean().optional(),
  protein_lunch_meat: z.boolean().optional(),
  protein_lunch_bean: z.boolean().optional(),
  protein_lunch_egg: z.boolean().optional(),
  protein_dinner_fish: z.boolean().optional(),
  protein_dinner_meat: z.boolean().optional(),
  protein_dinner_bean: z.boolean().optional(),
  protein_dinner_egg: z.boolean().optional(),
  notes: z.string().optional(),
})

export type SubjectiveFormValues = z.infer<typeof subjectiveSchema>
export type PhysicalFormValues = z.infer<typeof physicalSchema>
export type TrainingFormValues = z.infer<typeof trainingSchema>
export type MealFormValues = z.infer<typeof mealSchema>
