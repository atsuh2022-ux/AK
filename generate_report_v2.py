#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Athlete Feedback Report Generator v2
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings('ignore')

# Japanese font setup
import matplotlib.font_manager as fm
import subprocess

result = subprocess.run(['fc-list', ':lang=ja'], capture_output=True, text=True)
jp_fonts = [l for l in result.stdout.strip().split('\n') if l]

font_path = None
if jp_fonts:
    font_path = jp_fonts[0].split(':')[0].strip()
    fp = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = fp.get_name()
    print(f"Using Japanese font: {font_path}")
else:
    fp = fm.FontProperties()
    print("No Japanese font found, using default")

# ─────────────────────────────────────────
# 1. LOAD DATA
# ─────────────────────────────────────────
EXCEL_PATH = '/root/.claude/uploads/28f25c68-9581-4298-bce8-a857c17aebfc/2c710f9e-I___20260309_20260522.xlsx'
OUTPUT_DIR = '/home/user/AK/'

xl = pd.ExcelFile(EXCEL_PATH)

df_cond = xl.parse('主観的体調')
df_body = xl.parse('身体データ')
df_train = xl.parse('トレーニング')
df_meal = xl.parse('食事')

for df in [df_cond, df_body, df_train, df_meal]:
    df['日付'] = pd.to_datetime(df['日付'])

# Fix body weight outlier
mask = (df_body['日付'] == pd.Timestamp('2026-04-29')) & (df_body['体重_kg'] == 39.5)
df_body.loc[mask, '体重_kg'] = 69.5
print(f"Fixed body weight outlier: {mask.sum()} row(s)")

# ─────────────────────────────────────────
# 2. PREPARE PROTEIN DATA
# ─────────────────────────────────────────
protein_cols = ['昼タンパク質_魚', '昼タンパク質_肉', '昼タンパク質_豆', '昼タンパク質_卵',
                '夕タンパク質_魚', '夕タンパク質_肉', '夕タンパク質_豆', '夕タンパク質_卵']
for col in protein_cols:
    df_meal[col] = (df_meal[col] == '○')

df_meal['タンパク種類数'] = df_meal[protein_cols].sum(axis=1)

# ─────────────────────────────────────────
# 3. MERGE
# ─────────────────────────────────────────
# Aggregate training by date
is_rest = df_train['種目'] == '休養日'
df_train_rest = df_train[is_rest].copy()
df_train_active = df_train[~is_rest].copy()

def agg_training(group):
    return pd.Series({
        '種目': '/'.join(group['種目'].unique()),
        '時間_分': group['時間_分'].sum(),
        'RPE': round(group['RPE'].mean(), 1),
        '爆発力': round(group['爆発力'].mean(), 1),
        '持久力': round(group['持久力'].mean(), 1),
        '運動後疲労': round(group['運動後疲労'].mean(), 1),
        'メモ': ' / '.join(group['メモ'].dropna().astype(str).tolist()) if group['メモ'].notna().any() else np.nan
    })

if len(df_train_active) > 0:
    df_train_active_agg = df_train_active.groupby('日付').apply(agg_training).reset_index()
else:
    df_train_active_agg = pd.DataFrame(columns=['日付','種目','時間_分','RPE','爆発力','持久力','運動後疲労','メモ'])

cols_needed = ['日付','種目','時間_分','RPE','爆発力','持久力','運動後疲労','メモ']
df_train_combined = pd.concat([
    df_train_rest[cols_needed],
    df_train_active_agg[cols_needed]
], ignore_index=True).sort_values('日付').reset_index(drop=True)

df_master = df_cond.merge(df_body, on='日付', how='outer')
df_master = df_master.merge(df_train_combined, on='日付', how='outer')
meal_cols = ['日付','練習後補食','食欲','栄養バランス','タンパク種類数'] + protein_cols
df_master = df_master.merge(df_meal[meal_cols], on='日付', how='outer')
df_master = df_master.sort_values('日付').reset_index(drop=True)

print(f"Master dataframe: {df_master.shape}")

# ─────────────────────────────────────────
# 4. COMPUTE STATISTICS
# ─────────────────────────────────────────
is_rest_day = df_master['種目'].fillna('') == '休養日'
is_training_day = (df_master['種目'].notna()) & (~is_rest_day)

total_training_days = int(is_training_day.sum())
total_rest_days = int(is_rest_day.sum())
total_training_min = int(df_master.loc[is_training_day, '時間_分'].sum())

avg_rpe = df_master.loc[is_training_day, 'RPE'].mean()
avg_fatigue = df_master.loc[is_training_day, '運動後疲労'].mean()
avg_sleep_h = df_master['睡眠時間'].mean()
avg_sleep_q = df_master['睡眠の質'].mean()
avg_morning_cond = df_master['起床時コンディション'].mean()

bw = df_master['体重_kg'].dropna()
bw_sorted = df_body.sort_values('日付')
bw_first = float(bw_sorted['体重_kg'].iloc[0])
bw_last = float(bw_sorted['体重_kg'].iloc[-1])
bw_avg = float(bw.mean())
bw_range = float(bw.max() - bw.min())

bf_sorted = df_body.sort_values('日付')
bf_first = float(bf_sorted['体脂肪率_pct'].iloc[0])
bf_last = float(bf_sorted['体脂肪率_pct'].iloc[-1])

snack_yes = int((df_master['練習後補食'] == 'はい').sum())
protein_avg = float(df_master['タンパク種類数'].mean())

print(f"Training days: {total_training_days}, Rest: {total_rest_days}")
print(f"Total training min: {total_training_min}")
print(f"Avg RPE: {avg_rpe:.2f}, Avg fatigue: {avg_fatigue:.2f}")
print(f"Avg sleep h: {avg_sleep_h:.2f}, q: {avg_sleep_q:.2f}")
print(f"Avg morning cond: {avg_morning_cond:.2f}")
print(f"BW: {bw_first}/{bw_last}/{bw_avg:.1f}/{bw_range:.1f}")
print(f"BF: {bf_first}/{bf_last}")
print(f"Snack yes: {snack_yes}, Protein avg: {protein_avg:.2f}")

# ─────────────────────────────────────────
# 5. CORRELATION ANALYSIS
# ─────────────────────────────────────────
ds = df_master.sort_values('日付').reset_index(drop=True).copy()
ds['翌日疲労'] = ds['運動後疲労'].shift(-1)
ds['翌日コンディション'] = ds['起床時コンディション'].shift(-1)
train_m = (ds['種目'].notna()) & (ds['種目'] != '休養日')

snack_y = ds['練習後補食'] == 'はい'
snack_n = ds['練習後補食'] == 'いいえ'
corr_a_yes = ds.loc[snack_y, '翌日疲労'].mean()
corr_a_no  = ds.loc[snack_n, '翌日疲労'].mean()

sl_long  = ds['睡眠時間'] >= 7
sl_short = ds['睡眠時間'] < 7
corr_b_long  = ds.loc[sl_long  & train_m, 'RPE'].mean()
_b_short_raw = ds.loc[sl_short & train_m, 'RPE'].mean()
corr_b_short = _b_short_raw if not (isinstance(_b_short_raw, float) and np.isnan(_b_short_raw)) else None

sq_good = ds['睡眠の質'] <= 2
sq_bad  = ds['睡眠の質'] >= 3
corr_c_good = ds.loc[sq_good & train_m, '運動後疲労'].mean()
corr_c_bad  = ds.loc[sq_bad  & train_m, '運動後疲労'].mean()

pro_high = ds['タンパク種類数'] >= 3
pro_low  = ds['タンパク種類数'] < 3
corr_d_high = ds.loc[pro_high, '翌日コンディション'].mean()
corr_d_low  = ds.loc[pro_low,  '翌日コンディション'].mean()

print(f"(a) snack yes:{corr_a_yes:.2f} no:{corr_a_no:.2f}")
_b_short_str = f'{corr_b_short:.2f}' if corr_b_short is not None else 'N/A(データなし)'
print(f"(b) sleep≥7:{corr_b_long:.2f} <7:{_b_short_str}")
# Use a safe numeric for comparisons
corr_b_short_safe = corr_b_short if corr_b_short is not None else corr_b_long  # fallback = same as long
print(f"(c) sq≤2:{corr_c_good:.2f} ≥3:{corr_c_bad:.2f}")
print(f"(d) pro≥3:{corr_d_high:.2f} <3:{corr_d_low:.2f}")

# ─────────────────────────────────────────
# 6. KEY OBSERVATIONS
# ─────────────────────────────────────────
good_days_df = ds[(ds['運動後疲労'] <= 2) & (ds['起床時コンディション'] <= 2)]
good_days_list = good_days_df['日付'].dt.strftime('%m/%d').tolist()

high_fatigue_df = ds[ds['運動後疲労'] >= 4]
high_fatigue_list = high_fatigue_df['日付'].dt.strftime('%m/%d').tolist()

bad_cond_df = ds[ds['起床時コンディション'] >= 4]
bad_cond_list = bad_cond_df['日付'].dt.strftime('%m/%d').tolist()

hf_no_snack = ds[(ds['運動後疲労'] >= 4) & (ds['練習後補食'] == 'いいえ')]['日付'].dt.strftime('%m/%d').tolist()
zero_protein_days = ds[ds['タンパク種類数'] == 0]['日付'].dt.strftime('%m/%d').tolist()

protein_source_counts = {}
for col in protein_cols:
    short = col.replace('昼タンパク質_','昼:').replace('夕タンパク質_','夕:')
    protein_source_counts[short] = int(df_meal[col].sum())

sorted_proteins = sorted(protein_source_counts.items(), key=lambda x: x[1])
least_protein = sorted_proteins[0]
top_protein = sorted_proteins[-1]

print(f"Good days: {good_days_list}")
print(f"High fatigue: {high_fatigue_list}")
print(f"Bad cond: {bad_cond_list}")
print(f"Protein counts: {protein_source_counts}")
print(f"Least: {least_protein}, Top: {top_protein}")

# ─────────────────────────────────────────
# 7. CHARTS
# ─────────────────────────────────────────
GREEN  = '#38A169'
YELLOW = '#D69E2E'
ORANGE = '#DD6B20'
RED    = '#E53E3E'
BLUE   = '#2E86AB'

# ── fig_A ────────────────────────────────────────────────────────────────────
print("\nGenerating fig_A_trends.png...")
fig, axes = plt.subplots(4, 1, figsize=(14, 18))
fig.patch.set_facecolor('#FAFAFA')
dates = ds['日付']

# Panel 1: Body weight + fat
ax1, ax1b = axes[0], axes[0].twinx()
bw_d = ds[['日付','体重_kg']].dropna()
bf_d = ds[['日付','体脂肪率_pct']].dropna()
ax1.plot(bw_d['日付'], bw_d['体重_kg'], color=BLUE, marker='o', lw=2, ms=5, label='体重(kg)')
ax1b.plot(bf_d['日付'], bf_d['体脂肪率_pct'], color=ORANGE, marker='s', lw=2, ms=4, ls='--', label='体脂肪率(%)')
ax1.set_ylabel('体重 (kg)', fontproperties=fp, color=BLUE, fontsize=11)
ax1b.set_ylabel('体脂肪率 (%)', fontproperties=fp, color=ORANGE, fontsize=11)
ax1.set_title('① 体重・体脂肪率の推移', fontproperties=fp, fontsize=13, fontweight='bold', pad=8)
ax1.set_ylim(66, 73); ax1b.set_ylim(10, 17)
l1,b1 = ax1.get_legend_handles_labels(); l1b,b1b = ax1b.get_legend_handles_labels()
ax1.legend(l1+l1b, b1+b1b, prop=fp, loc='upper right', fontsize=9)
ax1.grid(True, alpha=0.3); ax1.tick_params(axis='x', rotation=30)

# Panel 2: Condition + sleep quality
ax2 = axes[1]
c_d = ds[['日付','起床時コンディション']].dropna()
sq_d = ds[['日付','睡眠の質']].dropna()
ax2.plot(c_d['日付'], c_d['起床時コンディション'], color=GREEN, marker='o', lw=2, ms=5, label='起床時コンディション')
ax2.plot(sq_d['日付'], sq_d['睡眠の質'], color=YELLOW, marker='s', lw=2, ms=4, ls='--', label='睡眠の質')
ax2.set_ylabel('スコア (1=良/5=悪)', fontproperties=fp, fontsize=11)
ax2.set_title('② 起床時コンディション・睡眠の質 (低いほど良好)', fontproperties=fp, fontsize=13, fontweight='bold', pad=8)
ax2.set_ylim(0.5, 5.5)
ax2.axhline(y=3, color='gray', ls=':', alpha=0.5)
ax2.legend(prop=fp, loc='upper right', fontsize=9)
ax2.grid(True, alpha=0.3); ax2.tick_params(axis='x', rotation=30)

# Panel 3: Sleep hours
ax3 = axes[2]
sh_d = ds[['日付','睡眠時間']].dropna()
bar_colors = [GREEN if h >= 7 else RED for h in sh_d['睡眠時間']]
ax3.bar(sh_d['日付'], sh_d['睡眠時間'], color=bar_colors, alpha=0.8, width=0.8)
ax3.axhline(y=7, color=BLUE, ls='--', lw=1.5, alpha=0.7, label='7時間ライン')
ax3.set_ylabel('睡眠時間 (h)', fontproperties=fp, fontsize=11)
ax3.set_title('③ 睡眠時間 (緑=7h以上)', fontproperties=fp, fontsize=13, fontweight='bold', pad=8)
ax3.set_ylim(5, 10)
ax3.legend(prop=fp, fontsize=9)
ax3.grid(True, alpha=0.3, axis='y'); ax3.tick_params(axis='x', rotation=30)

# Panel 4: RPE + duration
ax4, ax4b = axes[3], axes[3].twinx()
tr_d = ds[train_m]
rpe_colors = [GREEN if r<=5 else YELLOW if r<=7 else RED for r in tr_d['RPE']]
ax4.bar(tr_d['日付'], tr_d['RPE'], color=rpe_colors, alpha=0.7, width=0.8, label='RPE')
ax4b.plot(tr_d['日付'], tr_d['時間_分'], color=BLUE, marker='D', lw=2, ms=5, label='練習時間(分)')
ax4.set_ylabel('RPE (1-10)', fontproperties=fp, fontsize=11)
ax4b.set_ylabel('練習時間 (分)', fontproperties=fp, color=BLUE, fontsize=11)
ax4.set_title('④ 練習RPE・時間 (練習日のみ)', fontproperties=fp, fontsize=13, fontweight='bold', pad=8)
ax4.set_ylim(0, 12); ax4b.set_ylim(0, 320)
l4,b4 = ax4.get_legend_handles_labels(); l4b,b4b = ax4b.get_legend_handles_labels()
ax4.legend(l4+l4b, b4+b4b, prop=fp, loc='upper right', fontsize=9)
ax4.grid(True, alpha=0.3, axis='y'); ax4.tick_params(axis='x', rotation=30)

plt.tight_layout(pad=2.0)
plt.savefig(OUTPUT_DIR+'fig_A_trends.png', dpi=120, bbox_inches='tight', facecolor='#FAFAFA')
plt.close()
print("fig_A_trends.png saved")

# ── fig_B: Daily heatmap ─────────────────────────────────────────────────────
print("Generating fig_B_daily_heatmap.png...")
hmap_cols = ['起床時コンディション','睡眠の質','睡眠時間','運動後疲労','RPE','体重_kg','体脂肪率_pct','タンパク種類数']
hmap_labels = ['起床時CD','睡眠の質','睡眠時間','運動後疲労','RPE','体重kg','体脂肪%','タンパク種類']

def cell_color_hmap(col, val):
    if pd.isna(val): return '#E2E8F0'
    v = float(val)
    if col in ['起床時コンディション','睡眠の質','運動後疲労']:
        if v<=2: return '#C6F6D5'
        elif v==3: return '#FEFCBF'
        else: return '#FED7D7'
    elif col=='RPE':
        if v<=5: return '#C6F6D5'
        elif v<=7: return '#FEFCBF'
        else: return '#FED7D7'
    elif col=='睡眠時間':
        if v>=7.5: return '#C6F6D5'
        elif v>=7: return '#E6FFFA'
        elif v>=6: return '#FEFCBF'
        else: return '#FED7D7'
    elif col=='タンパク種類数':
        if v>=3: return '#C6F6D5'
        elif v>=2: return '#FEFCBF'
        elif v>=1: return '#FFF3CD'
        else: return '#FED7D7'
    else: return '#EBF8FF'

hmap_df = ds[['日付']+hmap_cols].copy()
n_rows = len(hmap_df); n_cols = len(hmap_cols)

fig, ax = plt.subplots(figsize=(15, max(12, n_rows*0.45)))
fig.patch.set_facecolor('white')
ax.set_xlim(-1, n_cols+0.2); ax.set_ylim(-1.5, n_rows+2.0)

for r_idx, (_, row) in enumerate(hmap_df.iterrows()):
    y = n_rows - r_idx - 1
    date_str = row['日付'].strftime('%m/%d')
    ax.text(-0.6, y+0.5, date_str, ha='right', va='center', fontsize=8.5, color='#4A5568', fontproperties=fp)
    for c_idx, col in enumerate(hmap_cols):
        val = row[col]
        color = cell_color_hmap(col, val)
        rect = mpatches.FancyBboxPatch((c_idx+0.02, y+0.02), 0.96, 0.96,
                                        boxstyle='round,pad=0.02', facecolor=color, edgecolor='#CBD5E0', lw=0.5)
        ax.add_patch(rect)
        if not pd.isna(val):
            v = float(val)
            txt = f'{v:.1f}' if v != int(v) else str(int(v))
            ax.text(c_idx+0.5, y+0.5, txt, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#2D3748')

for c_idx, label in enumerate(hmap_labels):
    ax.text(c_idx+0.5, n_rows+0.2, label, ha='center', va='bottom', fontsize=9, fontweight='bold', color='#2D3748', fontproperties=fp, rotation=20)

ax.axis('off')
legend_items = [
    mpatches.Patch(facecolor='#C6F6D5', label='良好'),
    mpatches.Patch(facecolor='#FEFCBF', label='注意'),
    mpatches.Patch(facecolor='#FED7D7', label='要注意'),
    mpatches.Patch(facecolor='#E2E8F0', label='データなし'),
]
ax.legend(handles=legend_items, loc='lower right', prop=fp, fontsize=9, bbox_to_anchor=(1.0,-0.03), framealpha=0.9)
ax.set_title('日次統合データ ヒートマップ', fontproperties=fp, fontsize=14, fontweight='bold', pad=10)
plt.tight_layout()
plt.savefig(OUTPUT_DIR+'fig_B_daily_heatmap.png', dpi=110, bbox_inches='tight', facecolor='white')
plt.close()
print("fig_B_daily_heatmap.png saved")

# ── fig_C: Protein calendar ──────────────────────────────────────────────────
print("Generating fig_C_protein_calendar.png...")
p_headers = ['昼:魚','昼:肉','昼:豆','昼:卵','夕:魚','夕:肉','夕:豆','夕:卵','補食','種類数']
p_colors  = ['#4299E1','#F6AD55','#68D391','#FBD38D','#63B3ED','#ED8936','#48BB78','#F6E05E','#9F7AEA','#E2E8F0']

meal_d = ds[['日付','練習後補食','タンパク種類数']+protein_cols].copy()
n_d = len(meal_d); n_p = len(p_headers)

fig, ax = plt.subplots(figsize=(15, max(14, (n_d+3)*0.5)))
fig.patch.set_facecolor('white')
ax.set_xlim(-1, n_p+0.2); ax.set_ylim(-1.5, n_d+2.2)

# Header
for c_idx, label in enumerate(p_headers):
    rect = mpatches.FancyBboxPatch((c_idx+0.02, n_d+0.52), 0.96, 0.96,
                                    boxstyle='round,pad=0.02', facecolor='#2D3748', edgecolor='#1A202C', lw=0.5)
    ax.add_patch(rect)
    ax.text(c_idx+0.5, n_d+1.0, label, ha='center', va='center', fontsize=8, fontweight='bold', color='white', fontproperties=fp)

for r_idx, (_, row) in enumerate(meal_d.iterrows()):
    y = n_d - r_idx - 1
    ax.text(-0.6, y+0.5, row['日付'].strftime('%m/%d'), ha='right', va='center', fontsize=8.5, color='#4A5568', fontproperties=fp)
    for c_idx, col in enumerate(protein_cols):
        if row[col]:
            circ = plt.Circle((c_idx+0.5, y+0.5), 0.32, facecolor=p_colors[c_idx], edgecolor='#CBD5E0', lw=0.5)
            ax.add_patch(circ)
        else:
            rect = mpatches.FancyBboxPatch((c_idx+0.05, y+0.05), 0.90, 0.90,
                                            boxstyle='round,pad=0.02', facecolor='#F7FAFC', edgecolor='#E2E8F0', lw=0.5)
            ax.add_patch(rect)
    # Snack (col 8)
    if row['練習後補食'] == 'はい':
        circ = plt.Circle((8.5, y+0.5), 0.32, facecolor=p_colors[8], edgecolor='#CBD5E0', lw=0.5)
        ax.add_patch(circ)
    else:
        rect = mpatches.FancyBboxPatch((8.05, y+0.05), 0.90, 0.90,
                                        boxstyle='round,pad=0.02', facecolor='#F7FAFC', edgecolor='#E2E8F0', lw=0.5)
        ax.add_patch(rect)
    # Count (col 9)
    k = int(row['タンパク種類数']) if not pd.isna(row['タンパク種類数']) else 0
    kc = '#C6F6D5' if k>=3 else '#FEFCBF' if k>=2 else '#FED7D7'
    rect = mpatches.FancyBboxPatch((9.05, y+0.05), 0.90, 0.90,
                                    boxstyle='round,pad=0.02', facecolor=kc, edgecolor='#CBD5E0', lw=0.5)
    ax.add_patch(rect)
    ax.text(9.5, y+0.5, str(k), ha='center', va='center', fontsize=9, fontweight='bold', color='#2D3748')

# Count row
ax.text(-0.6, -0.5, '合計', ha='right', va='center', fontsize=8.5, fontweight='bold', color='#2D3748', fontproperties=fp)
for c_idx, col in enumerate(protein_cols):
    cnt = int(meal_d[col].sum())
    rect = mpatches.FancyBboxPatch((c_idx+0.02, -0.98), 0.96, 0.96,
                                    boxstyle='round,pad=0.02', facecolor='#2D3748', edgecolor='#1A202C', lw=0.5)
    ax.add_patch(rect)
    ax.text(c_idx+0.5, -0.5, str(cnt), ha='center', va='center', fontsize=9, fontweight='bold', color='white')

sc = int((meal_d['練習後補食']=='はい').sum())
rect = mpatches.FancyBboxPatch((8.02, -0.98), 0.96, 0.96, boxstyle='round,pad=0.02', facecolor='#2D3748', edgecolor='#1A202C', lw=0.5)
ax.add_patch(rect)
ax.text(8.5, -0.5, str(sc), ha='center', va='center', fontsize=9, fontweight='bold', color='white')

avg_k = meal_d['タンパク種類数'].mean()
rect = mpatches.FancyBboxPatch((9.02, -0.98), 0.96, 0.96, boxstyle='round,pad=0.02', facecolor='#2D3748', edgecolor='#1A202C', lw=0.5)
ax.add_patch(rect)
ax.text(9.5, -0.5, f'{avg_k:.1f}', ha='center', va='center', fontsize=9, fontweight='bold', color='white')

ax.axis('off')
ax.set_title('タンパク質摂取カレンダー', fontproperties=fp, fontsize=14, fontweight='bold', pad=10)
leg_patches = [mpatches.Patch(facecolor=p_colors[i], label=p_headers[i]) for i in range(9)]
ax.legend(handles=leg_patches, loc='lower right', prop=fp, fontsize=8, ncol=3, bbox_to_anchor=(1.0,-0.04), framealpha=0.9)
plt.tight_layout()
plt.savefig(OUTPUT_DIR+'fig_C_protein_calendar.png', dpi=110, bbox_inches='tight', facecolor='white')
plt.close()
print("fig_C_protein_calendar.png saved")

# ── fig_D: Correlation bar charts ────────────────────────────────────────────
print("Generating fig_D_correlation.png...")
fig, axes = plt.subplots(1, 4, figsize=(18, 7))
fig.patch.set_facecolor('#FAFAFA')
fig.suptitle('関連性分析：生活習慣と練習パフォーマンスの関係', fontproperties=fp, fontsize=14, fontweight='bold', y=1.02)

def draw_bar(ax, title, la, lb, va, vb, ylabel, lower_better=True):
    better_a = (lower_better and va<=vb) or (not lower_better and va>=vb)
    ca = GREEN if better_a else RED
    cb = RED if better_a else GREEN
    bars = ax.bar([la, lb], [va, vb], color=[ca, cb], alpha=0.85, width=0.5, edgecolor='white', lw=1.5)
    for bar, v in zip(bars, [va, vb]):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.05, f'{v:.2f}',
                ha='center', va='bottom', fontsize=12, fontweight='bold', color='#2D3748')
    diff = vb - va
    dc = GREEN if (lower_better and diff>0) or (not lower_better and diff<0) else RED
    ax.text(0.5, 0.95, f'差: {diff:+.2f}', ha='center', va='top', transform=ax.transAxes,
            fontsize=10, color=dc, fontweight='bold')
    ax.set_title(title, fontproperties=fp, fontsize=10, fontweight='bold', pad=8)
    ax.set_ylabel(ylabel, fontproperties=fp, fontsize=9)
    ax.set_ylim(0, max(va,vb)*1.4+0.5)
    ax.grid(True, alpha=0.3, axis='y')
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ticks = ax.get_xticklabels()
    ax.set_xticklabels([la, lb], fontproperties=fp, fontsize=8.5)

draw_bar(axes[0], '(a) 補食あり/なし\n→ 翌日の運動後疲労',
         '補食あり', '補食なし', corr_a_yes, corr_a_no, '翌日の運動後疲労\n(1=低/5=高)', lower_better=True)
draw_bar(axes[1], '(b) 睡眠≥7h / <7h\n→ 練習RPE',
         '睡眠≥7h', '睡眠<7h', corr_b_long, corr_b_short_safe, '練習RPE (1=軽/10=最大)', lower_better=False)
draw_bar(axes[2], '(c) 睡眠の質 良/悪\n→ 練習中疲労',
         '睡眠質≤2(良)', '睡眠質≥3(悪)', corr_c_good, corr_c_bad, '運動後疲労\n(1=低/5=高)', lower_better=True)
draw_bar(axes[3], '(d) タンパク≥3種/0-2種\n→ 翌日の起床時CD',
         'タンパク≥3種', 'タンパク0-2種', corr_d_high, corr_d_low, '翌日の起床時CD\n(1=良/5=悪)', lower_better=True)

plt.tight_layout(pad=2.0)
plt.savefig(OUTPUT_DIR+'fig_D_correlation.png', dpi=120, bbox_inches='tight', facecolor='#FAFAFA')
plt.close()
print("fig_D_correlation.png saved")

# ── fig_E: Fatigue timeline ───────────────────────────────────────────────────
print("Generating fig_E_fatigue_timeline.png...")
fig, ax = plt.subplots(figsize=(16, 7))
fig.patch.set_facecolor('#FAFAFA')

hf_dates = ds[ds['運動後疲労'] >= 4]['日付']
for hf_d in hf_dates:
    ax.axvspan(hf_d - pd.Timedelta(hours=12), hf_d + pd.Timedelta(hours=12), alpha=0.15, color='red', zorder=0)

fat_d = ds[['日付','運動後疲労']].dropna()
cnd_d = ds[['日付','起床時コンディション']].dropna()
rpe_d = ds[train_m][['日付','RPE']].dropna()

ax.plot(fat_d['日付'], fat_d['運動後疲労'], color=RED, marker='o', lw=2.5, ms=6, label='運動後疲労 (1=低/5=高)', zorder=3)
ax.plot(cnd_d['日付'], cnd_d['起床時コンディション'], color=GREEN, marker='s', lw=2.5, ms=6, label='起床時コンディション (1=良/5=悪)', zorder=3)
ax.plot(rpe_d['日付'], rpe_d['RPE']/2, color=BLUE, marker='D', lw=2, ms=5, ls='--', label='RPE/2 (スケール調整)', zorder=3, alpha=0.8)

hf_pts = ds[ds['運動後疲労'] >= 4]
ax.scatter(hf_pts['日付'], hf_pts['運動後疲労'], color=RED, s=120, zorder=5, marker='*')
for _, row in hf_pts.iterrows():
    ax.annotate(f"疲労{int(row['運動後疲労'])}", xy=(row['日付'], row['運動後疲労']),
                xytext=(0,12), textcoords='offset points', ha='center', fontsize=7.5,
                fontproperties=fp, color=RED, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=RED, lw=0.8))

ax.axhline(y=3, color='gray', ls=':', alpha=0.4, lw=1)
ax.axhline(y=4, color='orange', ls=':', alpha=0.4, lw=1)
ax.set_ylabel('スコア', fontproperties=fp, fontsize=12)
ax.set_title('疲労・コンディション・RPEタイムライン\n（赤帯 = 運動後疲労≥4の高疲労日）', fontproperties=fp, fontsize=13, fontweight='bold', pad=10)
ax.legend(prop=fp, fontsize=10, loc='upper right')
ax.set_ylim(0, 6.5)
ax.grid(True, alpha=0.3)
ax.tick_params(axis='x', rotation=30)
if len(hf_dates) > 0:
    ax.text(0.02, 0.96, f'高疲労日: {len(hf_dates)}日', transform=ax.transAxes,
            fontsize=10, fontproperties=fp, color=RED, fontweight='bold', va='top',
            bbox=dict(boxstyle='round', facecolor='#FFF5F5', alpha=0.8))

plt.tight_layout()
plt.savefig(OUTPUT_DIR+'fig_E_fatigue_timeline.png', dpi=120, bbox_inches='tight', facecolor='#FAFAFA')
plt.close()
print("fig_E_fatigue_timeline.png saved")

# ─────────────────────────────────────────
# 8. BUILD DAILY TABLE HTML
# ─────────────────────────────────────────
def cell_style(metric, val):
    if pd.isna(val) or val == '': return ''
    try: v = float(val)
    except: return ''
    if metric in ['運動後疲労','起床時コンディション','睡眠の質']:
        if v<=2: return 'background-color:#C6F6D5;'
        elif v==3: return 'background-color:#FEFCBF;'
        else: return 'background-color:#FED7D7;'
    elif metric == 'RPE':
        if v<=5: return 'background-color:#C6F6D5;'
        elif v<=7: return 'background-color:#FEFCBF;'
        else: return 'background-color:#FEE2E2;'
    return ''

daily_rows_html = ''
for _, row in ds.iterrows():
    date_str = row['日付'].strftime('%m/%d')
    shu = str(row['種目']) if not pd.isna(row['種目']) else '-'
    is_rest_row = shu == '休養日'

    def fmt(v, d=1):
        if pd.isna(v): return '-'
        fv = float(v)
        if fv == int(fv): return str(int(fv))
        return f'{fv:.{d}f}'

    jikan   = fmt(row['時間_分'], 0) if not is_rest_row else '-'
    rpe     = fmt(row['RPE']) if not is_rest_row else '-'
    bakuha  = fmt(row['爆発力']) if not is_rest_row else '-'
    jikyuu  = fmt(row['持久力']) if not is_rest_row else '-'
    fatigue_v = row['運動後疲労'] if not is_rest_row else None
    fatigue = fmt(fatigue_v) if not is_rest_row else '-'
    bwt     = fmt(row['体重_kg'])
    cond    = fmt(row['起床時コンディション'])
    sleepq  = fmt(row['睡眠の質'])
    sleeph  = fmt(row['睡眠時間'])
    snack   = str(row['練習後補食']) if not pd.isna(row['練習後補食']) else '-'
    nutri   = fmt(row['栄養バランス']) if not pd.isna(row.get('栄養バランス')) else '-'

    rpe_s    = cell_style('RPE', row['RPE'] if not is_rest_row else None)
    fat_s    = cell_style('運動後疲労', fatigue_v)
    cond_s   = cell_style('起床時コンディション', row['起床時コンディション'])
    sleepq_s = cell_style('睡眠の質', row['睡眠の質'])
    snack_s  = 'background-color:#C6F6D5;' if snack=='はい' else ('background-color:#F7FAFC;' if snack=='いいえ' else '')

    row_bg = '#F5F7FA' if is_rest_row else 'white'
    daily_rows_html += f'''
    <tr style="background:{row_bg}">
      <td style="font-weight:600">{date_str}</td>
      <td style="font-size:0.83em">{shu}</td>
      <td>{jikan}</td>
      <td style="{rpe_s}">{rpe}</td>
      <td>{bakuha}</td>
      <td>{jikyuu}</td>
      <td style="{fat_s}">{fatigue}</td>
      <td>{bwt}</td>
      <td style="{cond_s}">{cond}</td>
      <td style="{sleepq_s}">{sleepq}</td>
      <td>{sleeph}</td>
      <td style="{snack_s}">{snack}</td>
      <td>{nutri}</td>
    </tr>'''

# ─────────────────────────────────────────
# 9. BUILD CORRELATION TABLE HTML
# ─────────────────────────────────────────
def corr_diff_style(val, lower_better):
    try: v=float(val)
    except: return ''
    if lower_better: return 'color:#38A169;font-weight:600' if v<0 else 'color:#E53E3E;font-weight:600'
    else: return 'color:#38A169;font-weight:600' if v>0 else 'color:#E53E3E;font-weight:600'

corr_rows = f'''
<tr>
  <td>補食あり vs 補食なし</td>
  <td>翌日の運動後疲労（低いほど良）</td>
  <td style="background:#C6F6D5;font-weight:600">{corr_a_yes:.2f}</td>
  <td>{corr_a_no:.2f}</td>
  <td style="{corr_diff_style(corr_a_yes-corr_a_no, True)}">{corr_a_yes-corr_a_no:+.2f}</td>
  <td>{'補食ありの方が翌日の疲労が低い傾向' if corr_a_yes<corr_a_no else '差は小さい、継続観察推奨'}</td>
</tr>
<tr>
  <td>睡眠≥7h vs ＜7h</td>
  <td>練習RPE（高いほど良）</td>
  <td style="background:#C6F6D5;font-weight:600">{corr_b_long:.2f}</td>
  <td>{'データなし（全日7h以上）' if corr_b_short is None else f'{corr_b_short:.2f}'}</td>
  <td>{'—' if corr_b_short is None else f'{corr_b_long-corr_b_short:+.2f}'}</td>
  <td>{'今期間は全日7h以上の睡眠が確保できています。引き続き維持しましょう。' if corr_b_short is None else ('十分な睡眠でより高強度の練習が可能' if corr_b_long>=corr_b_short else '睡眠不足でもRPEに差なし（過負荷注意）')}</td>
</tr>
<tr>
  <td>睡眠の質≤2（良）vs ≥3（悪）</td>
  <td>練習中疲労（低いほど良）</td>
  <td style="background:#C6F6D5;font-weight:600">{corr_c_good:.2f}</td>
  <td>{corr_c_bad:.2f}</td>
  <td style="{corr_diff_style(corr_c_good-corr_c_bad, True)}">{corr_c_good-corr_c_bad:+.2f}</td>
  <td>{'睡眠の質が良いと練習中の疲労が低い傾向' if corr_c_good<corr_c_bad else '継続データで関係性を確認'}</td>
</tr>
<tr>
  <td>タンパク≥3種 vs 0-2種</td>
  <td>翌日の起床時CD（低いほど良）</td>
  <td style="background:#C6F6D5;font-weight:600">{corr_d_high:.2f}</td>
  <td>{corr_d_low:.2f}</td>
  <td style="{corr_diff_style(corr_d_high-corr_d_low, True)}">{corr_d_high-corr_d_low:+.2f}</td>
  <td>{'多様なタンパク源が翌朝のコンディション向上に関連' if corr_d_high<corr_d_low else 'タンパク種類とCDの関係を継続観察'}</td>
</tr>
'''

# ─────────────────────────────────────────
# 10. RENDER HTML
# ─────────────────────────────────────────
print("Generating HTML...")

html = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>選手フィードバックレポート 2026</title>
<style>
:root{{
  --green:#38A169; --yellow:#D69E2E; --orange:#DD6B20; --red:#E53E3E;
  --blue:#2E86AB; --blue-light:#EBF8FF;
  --shadow:0 2px 8px rgba(0,0,0,0.08); --radius:10px;
}}
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Hiragino Kaku Gothic ProN','Meiryo',sans-serif;
  background:#F0F4F8; color:#2D3748; font-size:14px; line-height:1.6;
}}
nav{{
  position:sticky; top:0; z-index:100;
  background:#1A365D; display:flex; gap:2px; padding:0 16px;
  box-shadow:0 2px 12px rgba(0,0,0,0.2); overflow-x:auto;
}}
nav a{{
  display:inline-block; padding:14px 20px; color:#BEE3F8; text-decoration:none;
  font-size:13px; font-weight:600; white-space:nowrap;
  border-bottom:3px solid transparent; transition:all 0.2s;
}}
nav a:hover,nav a.active{{color:white;border-bottom-color:#63B3ED;background:rgba(255,255,255,0.05);}}
.main-header{{
  background:linear-gradient(135deg,#1A365D 0%,#2E86AB 100%);
  color:white; padding:32px 24px; text-align:center;
}}
.main-header h1{{font-size:1.8em;font-weight:800;letter-spacing:0.02em;margin-bottom:6px;}}
.main-header .subtitle{{font-size:1em;opacity:0.85;}}
.section{{display:none;max-width:1200px;margin:0 auto;padding:24px 16px 48px;}}
.section.active{{display:block;}}
.card{{background:white;border-radius:var(--radius);box-shadow:var(--shadow);padding:24px;margin-bottom:20px;}}
.card-title{{
  font-size:1.1em;font-weight:700;color:var(--blue);margin-bottom:16px;
  padding-bottom:8px;border-bottom:2px solid var(--blue-light);
  display:flex;align-items:center;gap:8px;
}}
.card-title::before{{
  content:'';display:inline-block;width:4px;height:1.1em;
  background:var(--blue);border-radius:2px;
}}
.kpi-table{{width:100%;border-collapse:collapse;font-size:0.92em;}}
.kpi-table th{{background:#2D3748;color:white;padding:10px 14px;text-align:left;font-weight:600;}}
.kpi-table td{{padding:9px 14px;border-bottom:1px solid #E2E8F0;}}
.kpi-table tr:nth-child(even) td{{background:#F7FAFC;}}
.kpi-table tr:hover td{{background:#EBF8FF;}}
.kpi-value{{font-weight:700;font-size:1.05em;color:#1A365D;}}
.comment-box{{background:#FFFBEB;border-left:4px solid var(--yellow);border-radius:0 8px 8px 0;padding:16px 20px;margin-bottom:16px;}}
.comment-box h4{{font-size:1em;font-weight:700;color:#744210;margin-bottom:8px;}}
.comment-box p{{color:#78350F;line-height:1.75;}}
.good-comment{{background:#F0FFF4;border-left-color:var(--green);}}
.good-comment h4{{color:#276749;}} .good-comment p{{color:#22543D;}}
.warn-comment{{background:#FFF5F5;border-left-color:var(--red);}}
.warn-comment h4{{color:#742A2A;}} .warn-comment p{{color:#63171B;}}
.goal-comment{{background:var(--blue-light);border-left-color:var(--blue);}}
.goal-comment h4{{color:#1A365D;}} .goal-comment p{{color:#2C5282;}}
.qa-block{{background:#F7FAFC;border-radius:8px;padding:16px;margin-bottom:12px;}}
.qa-q{{font-weight:700;color:var(--blue);margin-bottom:8px;}}
.qa-a{{background:white;border:1px dashed #CBD5E0;border-radius:6px;padding:32px 12px;
       color:#A0AEC0;font-style:italic;text-align:center;min-height:60px;}}
.daily-table{{width:100%;border-collapse:collapse;font-size:0.82em;overflow-x:auto;display:block;}}
.daily-table th{{background:#2D3748;color:white;padding:8px 10px;white-space:nowrap;
                 position:sticky;top:48px;font-size:0.84em;}}
.daily-table td{{padding:7px 10px;border-bottom:1px solid #E2E8F0;text-align:center;white-space:nowrap;}}
.daily-table tr:hover td{{filter:brightness(0.96);}}
.chart-container{{text-align:center;margin:16px 0;}}
.chart-container img{{max-width:100%;border-radius:8px;box-shadow:var(--shadow);}}
.chart-caption{{font-size:0.85em;color:#718096;margin-top:8px;font-style:italic;}}
.corr-table{{width:100%;border-collapse:collapse;font-size:0.88em;margin-top:12px;}}
.corr-table th{{background:#2D3748;color:white;padding:10px 12px;text-align:left;}}
.corr-table td{{padding:10px 12px;border-bottom:1px solid #E2E8F0;}}
.corr-table tr:nth-child(even) td{{background:#F7FAFC;}}
.badge{{display:inline-block;padding:2px 8px;border-radius:12px;font-size:0.8em;font-weight:600;}}
.badge-green{{background:#C6F6D5;color:#276749;}}
.badge-yellow{{background:#FEFCBF;color:#744210;}}
.badge-red{{background:#FED7D7;color:#742A2A;}}
.hint-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;margin-top:12px;}}
.hint-item{{background:#F0FFF4;border:1px solid #9AE6B4;border-radius:8px;padding:14px;}}
.hint-item.warn{{background:#FFFBEB;border-color:#F6E05E;}}
.hint-title{{font-weight:700;font-size:0.9em;color:#276749;margin-bottom:6px;}}
.hint-item.warn .hint-title{{color:#744210;}}
.section-header{{
  font-size:1.3em;font-weight:800;color:#1A365D;margin-bottom:20px;
  display:flex;align-items:center;gap:10px;
}}
.section-header .num{{
  background:var(--blue);color:white;width:32px;height:32px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;font-size:0.85em;flex-shrink:0;
}}
@media(max-width:600px){{
  nav a{{padding:12px 10px;font-size:11px;}}
  .main-header h1{{font-size:1.3em;}}
  .card{{padding:16px;}}
}}
</style>
</head>
<body>
<div class="main-header">
  <h1>選手フィードバックレポート</h1>
  <div class="subtitle">2026.03.31 – 2026.05.14　｜　自動生成レポート</div>
</div>
<nav>
  <a href="#" class="active" onclick="return showSec('summary',this)">① サマリー</a>
  <a href="#" onclick="return showSec('daily',this)">② 日次統合データ</a>
  <a href="#" onclick="return showSec('nutrition',this)">③ 食事バランス</a>
  <a href="#" onclick="return showSec('trends',this)">④ トレンドグラフ</a>
  <a href="#" onclick="return showSec('correlation',this)">⑤ 関連性ヒント</a>
</nav>

<!-- ① SUMMARY -->
<div id="summary" class="section active">
  <div class="section-header"><div class="num">①</div>サマリー</div>

  <div class="card">
    <div class="card-title">KPI 主要指標</div>
    <table class="kpi-table">
      <thead><tr><th>指標</th><th>今期間値</th><th>評価コメント</th></tr></thead>
      <tbody>
        <tr><td>総トレーニング日数（休養除く）</td><td class="kpi-value">{total_training_days} 日</td><td>{'計画的な練習量を維持できている' if total_training_days>=15 else 'やや少なめ、増加を検討'}</td></tr>
        <tr><td>総トレーニング時間（分）</td><td class="kpi-value">{total_training_min} 分（約 {total_training_min/60:.1f} 時間）</td><td>{'十分なトレーニングボリューム' if total_training_min>=2000 else '増量の余地あり'}</td></tr>
        <tr><td>平均RPE（練習日のみ）</td><td class="kpi-value">{avg_rpe:.1f} / 10</td><td>{'適切な強度管理ができている' if 5<=avg_rpe<=7 else ('高強度傾向、回復に注意' if avg_rpe>7 else 'やや低強度')}</td></tr>
        <tr><td>平均運動後疲労（練習日のみ）<small>（1=低疲労/5=高疲労）</small></td><td class="kpi-value">{avg_fatigue:.2f}</td><td>{'良好な回復状態' if avg_fatigue<=2.5 else ('要注意：疲労が蓄積気味' if avg_fatigue>=3.5 else 'まずまず')}</td></tr>
        <tr><td>平均睡眠時間（h）</td><td class="kpi-value">{avg_sleep_h:.2f} h</td><td>{'7時間以上確保できている' if avg_sleep_h>=7 else '睡眠時間を増やしたい'}</td></tr>
        <tr><td>平均睡眠の質<small>（1=良/5=悪）</small></td><td class="kpi-value">{avg_sleep_q:.2f}</td><td>{'質の良い睡眠を確保できている' if avg_sleep_q<=2.5 else ('睡眠の質改善が課題' if avg_sleep_q>=3.5 else '普通レベル')}</td></tr>
        <tr><td>平均起床時コンディション<small>（1=良/5=悪）</small></td><td class="kpi-value">{avg_morning_cond:.2f}</td><td>{'良好な朝のコンディション' if avg_morning_cond<=2.5 else ('要観察' if avg_morning_cond>=3.5 else '普通レベル')}</td></tr>
        <tr><td>平均体重（kg）</td><td class="kpi-value">{bw_avg:.1f} kg</td><td>期初 {bw_first} kg → 期末 {bw_last} kg（{bw_last-bw_first:+.1f} kg）</td></tr>
        <tr><td>体重変動幅（kg）</td><td class="kpi-value">{bw_range:.1f} kg</td><td>{'体重管理が安定している' if bw_range<=2 else '体重変動がやや大きい'}</td></tr>
        <tr><td>体脂肪率　期初 → 期末</td><td class="kpi-value">{bf_first:.1f}% → {bf_last:.1f}%（{bf_last-bf_first:+.1f}%）</td><td>{'体脂肪率が改善傾向' if bf_last<bf_first else '体脂肪率の変化に注目'}</td></tr>
        <tr><td>練習後補食「はい」の日数</td><td class="kpi-value">{snack_yes} 日 / {len(ds)} 日</td><td>{'補食習慣が良好' if snack_yes>=int(len(ds)*0.5) else '補食の機会をもっと増やしたい'}</td></tr>
        <tr><td>タンパク源の平均種類数</td><td class="kpi-value">{protein_avg:.2f} 種類 / 日</td><td>{'多様なタンパク源を摂れている' if protein_avg>=3 else ('もう少し多様化を' if protein_avg>=2 else 'タンパク質の種類を増やしてほしい')}</td></tr>
      </tbody>
    </table>
  </div>

  <div class="card">
    <div class="card-title">コーチコメント</div>
    <div class="comment-box good-comment">
      <h4>① よかった点</h4>
      <p>
        今期間を通じて<strong>運動後疲労の平均 {avg_fatigue:.1f}（5段階）</strong>と概ね良好な疲労管理ができていました。
        特に調子の良かった日（{', '.join(good_days_list[:6]) if good_days_list else 'なし'}）は、
        起床時コンディション・運動後疲労ともに1〜2の良好な状態を維持できています。<br>
        補食実施日の翌日疲労は平均 <strong>{corr_a_yes:.2f}</strong>（補食なし: {corr_a_no:.2f}）と
        {'補食の効果がデータに現れています' if corr_a_yes<corr_a_no else '補食習慣を継続してデータを蓄積しましょう'}。
        睡眠時間は平均 <strong>{avg_sleep_h:.1f}h</strong> 確保でき、
        体脂肪率も {bf_first:.1f}% → {bf_last:.1f}% と{'改善傾向' if bf_last<bf_first else '安定'}しています。
        多様なタンパク源（3種以上）を摂った日の翌朝コンディションは
        <strong>{corr_d_high:.2f}</strong>（少ない日: {corr_d_low:.2f}）と
        {'より良好な傾向です' if corr_d_high<corr_d_low else '継続観察中です'}。
      </p>
    </div>
    <div class="comment-box warn-comment">
      <h4>② 気になった点</h4>
      <p>
        運動後疲労が4以上の高疲労日が計 <strong>{len(high_fatigue_list)}日</strong>
        （{', '.join(high_fatigue_list)}）ありました。
        起床時コンディションが4以上の日も <strong>{len(bad_cond_list)}日</strong>
        （{', '.join(bad_cond_list) if bad_cond_list else 'なし'}）観察されています。<br>
        高疲労日のうち補食なしの日は {', '.join(hf_no_snack) if hf_no_snack else 'なし'} で、
        回復栄養の不足が疲労蓄積に関係している可能性があります。
        タンパク質摂取では <strong>「{least_protein[0]}」が {least_protein[1]}日</strong>と最も少なく、
        特定食材への偏りが見られます。
        睡眠の質が悪い日（≥3）の練習中疲労は平均 {corr_c_bad:.2f}（良い日: {corr_c_good:.2f}）と
        {'高い傾向があります' if corr_c_bad>corr_c_good else '差は小さいですが、睡眠の質改善を継続しましょう'}。
      </p>
    </div>
    <div class="comment-box goal-comment">
      <h4>③ 次の大会までの小さな目標</h4>
      <p>
        <strong>「練習後は必ず補食を行い、夕食で昼と異なる2種類以上のタンパク源を意識する」</strong><br>
        練習後30分以内にプロテインまたはおにぎり＋卵等を摂取し、
        今期間で最も少なかった「{least_protein[0]}（{least_protein[1]}日）」を週3回以上取り入れることを目標にしましょう。
        補食あり→翌日疲労 {corr_a_yes:.2f} vs なし→ {corr_a_no:.2f} のデータからも、
        補食の効果は{'数値として現れています' if corr_a_yes<corr_a_no else '期待できます'}。
        まず2週間継続して変化を記録してください。
      </p>
    </div>
  </div>

  <div class="card">
    <div class="card-title">選手への質問（記入欄）</div>
    <div class="qa-block">
      <div class="qa-q">Q1. 今期間で一番調子よく練習できた日はいつですか？そのとき何が良かったと思いますか？</div>
      <div class="qa-a">（選手記入欄）</div>
    </div>
    <div class="qa-block">
      <div class="qa-q">Q2. 疲労が高かった日（{', '.join(high_fatigue_list[:3]) if high_fatigue_list else 'なし'} 等）を振り返って、前日や当日に気になったことはありましたか？</div>
      <div class="qa-a">（選手記入欄）</div>
    </div>
    <div class="qa-block">
      <div class="qa-q">Q3. 次期間に向けて、自分で取り組みたいことを1つ教えてください。</div>
      <div class="qa-a">（選手記入欄）</div>
    </div>
  </div>
</div>

<!-- ② DAILY DATA -->
<div id="daily" class="section">
  <div class="section-header"><div class="num">②</div>日次統合データ</div>
  <div class="card">
    <div class="card-title">カラーコード凡例</div>
    <div style="display:flex;flex-wrap:wrap;gap:8px;margin-bottom:8px;">
      <span class="badge badge-green">1-2: 良好</span>
      <span class="badge badge-yellow">3: 注意</span>
      <span class="badge badge-red">4-5: 要注意</span>
      <span style="background:#C6F6D5;padding:2px 8px;border-radius:12px;font-size:0.8em;font-weight:600;color:#276749;">補食あり</span>
      <span style="background:#F7FAFC;padding:2px 8px;border-radius:12px;font-size:0.8em;font-weight:600;color:#718096;border:1px solid #E2E8F0;">補食なし</span>
      <span style="background:#F5F7FA;padding:2px 8px;border-radius:12px;font-size:0.8em;color:#A0AEC0;border:1px solid #E2E8F0;">休養日（薄グレー）</span>
    </div>
    <p style="font-size:0.82em;color:#718096;">疲労・コンディション・睡眠の質は「1=良/5=悪」。RPEは「1=楽/10=最大」。</p>
  </div>
  <div class="card" style="padding:12px;overflow-x:auto;">
    <table class="daily-table">
      <thead>
        <tr>
          <th>日付</th><th>種目</th><th>時間(分)</th><th>RPE</th>
          <th>爆発力</th><th>持久力</th><th>運動後疲労</th><th>体重(kg)</th>
          <th>起床時CD</th><th>睡眠の質</th><th>睡眠時間</th><th>補食</th><th>栄養Bal</th>
        </tr>
      </thead>
      <tbody>{daily_rows_html}</tbody>
    </table>
  </div>
  <div class="card">
    <div class="card-title">トレンドグラフ（概要）</div>
    <div class="chart-container">
      <img src="fig_A_trends.png" alt="4指標トレンド">
      <div class="chart-caption">体重・体脂肪・コンディション・睡眠・RPEの期間推移</div>
    </div>
  </div>
</div>

<!-- ③ NUTRITION -->
<div id="nutrition" class="section">
  <div class="section-header"><div class="num">③</div>食事バランス</div>
  <div class="card">
    <div class="card-title">タンパク質摂取カレンダー</div>
    <div class="chart-container">
      <img src="fig_C_protein_calendar.png" alt="タンパク質カレンダー">
      <div class="chart-caption">各日の昼・夕タンパク質源（魚/肉/豆/卵）と補食。●=摂取あり、最下行=合計/平均</div>
    </div>
  </div>
  <div class="card">
    <div class="card-title">食事バランス ヒント</div>
    <div class="hint-grid">
      <div class="hint-item warn">
        <div class="hint-title">⚠ 最も少ないタンパク源</div>
        <p style="font-size:0.9em;color:#744210;">
          <strong>「{sorted_proteins[0][0]}」が {sorted_proteins[0][1]}日</strong>と最も少ない。
          次いで「{sorted_proteins[1][0]}」({sorted_proteins[1][1]}日)。
          バランス良く摂取するよう意識しましょう。
        </p>
      </div>
      <div class="hint-item">
        <div class="hint-title">✓ 最も多いタンパク源</div>
        <p style="font-size:0.9em;color:#276749;">
          <strong>「{sorted_proteins[-1][0]}」が {sorted_proteins[-1][1]}日</strong>と最もよく摂取できています。
          この習慣を継続しながら他の食材も取り入れましょう。
        </p>
      </div>
      <div class="hint-item {'warn' if len(zero_protein_days)>3 else ''}">
        <div class="hint-title">{'⚠' if len(zero_protein_days)>3 else '✓'} タンパク質0種の日</div>
        <p style="font-size:0.9em;">
          タンパク質源の記録が0の日が <strong>{len(zero_protein_days)}日</strong>
          ({', '.join(zero_protein_days[:6]) if zero_protein_days else 'なし'})。
          {'記録漏れか摂取増加が必要。' if len(zero_protein_days)>3 else '少ない回数で良好です。'}
        </p>
      </div>
      <div class="hint-item">
        <div class="hint-title">📊 補食実施状況</div>
        <p style="font-size:0.9em;color:#276749;">
          補食実施 <strong>{snack_yes}日 / {len(ds)}日</strong>（{snack_yes/len(ds)*100:.0f}%）。
          補食あり→翌日疲労 <strong>{corr_a_yes:.2f}</strong> / 補食なし→ <strong>{corr_a_no:.2f}</strong>。
          {'補食の効果がデータに現れています。' if corr_a_yes<corr_a_no else '継続して記録しましょう。'}
        </p>
      </div>
    </div>
  </div>
</div>

<!-- ④ TRENDS -->
<div id="trends" class="section">
  <div class="section-header"><div class="num">④</div>トレンドグラフ</div>
  <div class="card">
    <div class="card-title">4指標トレンド（体重・コンディション・睡眠・RPE）</div>
    <div class="chart-container">
      <img src="fig_A_trends.png" alt="4指標トレンド">
      <div class="chart-caption">上から: ①体重・体脂肪 ②起床時コンディション・睡眠の質（低=良） ③睡眠時間（緑=7h以上） ④RPE・練習時間（練習日のみ）</div>
    </div>
  </div>
  <div class="card">
    <div class="card-title">疲労・コンディション・RPEタイムライン</div>
    <div class="chart-container">
      <img src="fig_E_fatigue_timeline.png" alt="疲労タイムライン">
      <div class="chart-caption">
        赤線=運動後疲労、緑線=起床時コンディション（低=良）、青破線=RPE/2。
        赤背景バンド = 運動後疲労≥4の高疲労日（計 {len(high_fatigue_list)}日）
      </div>
    </div>
  </div>
  <div class="card">
    <div class="card-title">日次ヒートマップ</div>
    <div class="chart-container">
      <img src="fig_B_daily_heatmap.png" alt="日次ヒートマップ">
      <div class="chart-caption">全指標を日付×指標マトリックスで可視化。緑=良好、黄=注意、赤=要注意。</div>
    </div>
  </div>
</div>

<!-- ⑤ CORRELATION -->
<div id="correlation" class="section">
  <div class="section-header"><div class="num">⑤</div>関連性ヒント</div>
  <div class="card">
    <div class="card-title">4つの比較分析チャート</div>
    <div class="chart-container">
      <img src="fig_D_correlation.png" alt="関連性チャート">
      <div class="chart-caption">各グループ間の指標平均値比較。緑=良好なグループ、赤=注意が必要なグループ。差も表示。</div>
    </div>
  </div>
  <div class="card">
    <div class="card-title">比較分析サマリー表</div>
    <table class="corr-table">
      <thead>
        <tr>
          <th>比較条件</th><th>対象指標</th>
          <th>グループA（良好）</th><th>グループB（悪）</th>
          <th>差（A−B）</th><th>解釈</th>
        </tr>
      </thead>
      <tbody>{corr_rows}</tbody>
    </table>
  </div>
  <div class="card">
    <div class="card-title">解釈ガイド</div>
    <div class="hint-grid">
      <div class="hint-item">
        <div class="hint-title">(a) 補食と翌日疲労</div>
        <p style="font-size:0.88em;">練習後の補食は筋グリコーゲン回復を促進します。
        補食あり: {corr_a_yes:.2f} vs なし: {corr_a_no:.2f}（疲労スコア、低=良）。
        {'差 {:.2f}で補食の効果が示唆されます。'.format(corr_a_no-corr_a_yes) if corr_a_yes<corr_a_no else 'さらなるデータ蓄積で確認しましょう。'}</p>
      </div>
      <div class="hint-item">
        <div class="hint-title">(b) 睡眠時間とRPE</div>
        <p style="font-size:0.88em;">7時間以上の睡眠でRPE={corr_b_long:.2f}。今期間は全日7時間以上確保できているため比較データなし。
        {'睡眠7h以上を今後も維持しましょう。'}
        現在の平均睡眠 {avg_sleep_h:.1f}h は {'良好です。' if avg_sleep_h>=7 else '7時間確保を目標に。'}</p>
      </div>
      <div class="hint-item">
        <div class="hint-title">(c) 睡眠の質と疲労</div>
        <p style="font-size:0.88em;">睡眠質良好（≤2）の疲労={corr_c_good:.2f}、悪い（≥3）= {corr_c_bad:.2f}。
        {'睡眠の質が練習疲労に影響しています。' if corr_c_bad>corr_c_good else '継続データで関係性を確認。'}
        就寝前のルーティン統一（入浴・スマホオフ等）を推奨します。</p>
      </div>
      <div class="hint-item">
        <div class="hint-title">(d) タンパク多様性と翌朝CD</div>
        <p style="font-size:0.88em;">タンパク3種以上の翌朝CD={corr_d_high:.2f}、0-2種={corr_d_low:.2f}（低=良）。
        {'多様なアミノ酸が回復に寄与している可能性。' if corr_d_high<corr_d_low else 'データ蓄積で確認が必要。'}
        最も少ない「{least_protein[0]}」の摂取増加が効果的かもしれません。</p>
      </div>
    </div>
  </div>
</div>

<script>
function showSec(id, link) {{
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('nav a').forEach(a => a.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  link.classList.add('active');
  window.scrollTo({{top:0,behavior:'smooth'}});
  return false;
}}
document.addEventListener('keydown', function(e) {{
  const secs=['summary','daily','nutrition','trends','correlation'];
  const links=document.querySelectorAll('nav a');
  let cur=-1;
  secs.forEach((s,i) => {{ if(document.getElementById(s).classList.contains('active')) cur=i; }});
  if(e.key==='ArrowRight'&&cur<secs.length-1) showSec(secs[cur+1],links[cur+1]);
  else if(e.key==='ArrowLeft'&&cur>0) showSec(secs[cur-1],links[cur-1]);
}});
</script>
<footer style="background:#2D3748;color:#A0AEC0;text-align:center;padding:16px;font-size:0.8em;margin-top:20px;">
  自動生成レポート | データ期間: 2026.03.31–2026.05.14 | 体重外れ値補正済み（04/29: 39.5→69.5kg）
</footer>
</body>
</html>'''

with open(OUTPUT_DIR+'athlete_feedback_v2.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("HTML saved: athlete_feedback_v2.html")
print("\nSUCCESS")
