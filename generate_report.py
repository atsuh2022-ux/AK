import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from matplotlib import rcParams
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Japanese font setup
rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# ===== Color palette =====
C_BLUE   = '#2E86AB'
C_RED    = '#E84855'
C_GREEN  = '#3BB273'
C_ORANGE = '#F4A259'
C_PURPLE = '#7B2D8B'
C_GRAY   = '#8D99AE'
C_LIGHT  = '#EDF2F4'

# ===== Load data =====
import openpyxl
wb = openpyxl.load_workbook('/root/.claude/uploads/28f25c68-9581-4298-bce8-a857c17aebfc/2c710f9e-I___20260309_20260522.xlsx')

def sheet_to_df(ws):
    data = list(ws.iter_rows(values_only=True))
    df = pd.DataFrame(data[1:], columns=data[0])
    df['日付'] = pd.to_datetime(df['日付'])
    return df

df_cond  = sheet_to_df(wb['主観的体調'])
df_body  = sheet_to_df(wb['身体データ'])
df_train = sheet_to_df(wb['トレーニング'])
df_food  = sheet_to_df(wb['食事'])

# Fix body weight outlier (39.5 -> 69.5 on 2026-04-29)
df_body.loc[df_body['体重_kg'] < 50, '体重_kg'] = 69.5

# Training: aggregate per day (sum time, max RPE for main session)
df_train_daily = df_train.groupby('日付').agg(
    総時間=('時間_分', 'sum'),
    maxRPE=('RPE', 'max'),
    種目リスト=('種目', lambda x: '+'.join(x.unique())),
    爆発力=('爆発力', 'max'),
    持久力=('持久力', 'max'),
    運動後疲労=('運動後疲労', 'max'),
).reset_index()

# Nutrition: count protein sources per day
protein_cols = ['昼タンパク質_魚','昼タンパク質_肉','昼タンパク質_豆','昼タンパク質_卵',
                '夕タンパク質_魚','夕タンパク質_肉','夕タンパク質_豆','夕タンパク質_卵']
for c in protein_cols:
    df_food[c] = df_food[c].apply(lambda x: 1 if x == '○' else 0)
df_food['タンパク質摂取数'] = df_food[protein_cols].sum(axis=1)
df_food['練習後補食_bin'] = df_food['練習後補食'].apply(lambda x: 1 if x == 'はい' else 0)

# Merge all on date
df_all = df_cond.merge(df_body, on='日付', how='outer')
df_all = df_all.merge(df_train_daily, on='日付', how='outer')
df_all = df_all.merge(df_food[['日付','練習後補食_bin','食欲','栄養バランス','タンパク質摂取数']], on='日付', how='outer')
df_all = df_all.sort_values('日付').reset_index(drop=True)

dates = df_all['日付']
date_labels = [d.strftime('%m/%d') for d in dates]

# ===== Helper: label bars with value =====
def autolabel(ax, bars, fmt='{:.0f}'):
    for bar in bars:
        h = bar.get_height()
        if h > 0:
            ax.text(bar.get_x() + bar.get_width()/2., h+0.05, fmt.format(h),
                    ha='center', va='bottom', fontsize=7)

# ============================================================
# FIGURE 1: Overview dashboard (3x2 grid)
# ============================================================
fig1, axes = plt.subplots(3, 2, figsize=(16, 18))
fig1.suptitle('Athlete Feedback Summary\n100m / 400m Track & Field  |  2026.03.31 - 2026.05.14',
              fontsize=16, fontweight='bold', y=0.98)
fig1.patch.set_facecolor('#F8F9FA')

# --- [0,0] Body weight & body fat ---
ax = axes[0, 0]
ax2 = ax.twinx()
ax.set_facecolor(C_LIGHT)
ax.plot(dates, df_all['体重_kg'], color=C_BLUE, lw=2, marker='o', ms=5, label='Body Weight (kg)')
ax2.plot(dates, df_all['体脂肪率_pct'], color=C_RED, lw=2, marker='s', ms=5, ls='--', label='Body Fat (%)')
ax.set_title('Body Weight & Body Fat Trend', fontweight='bold', fontsize=12)
ax.set_ylabel('Weight (kg)', color=C_BLUE)
ax2.set_ylabel('Body Fat (%)', color=C_RED)
ax.tick_params(axis='x', rotation=45, labelsize=7)
ax.set_ylim(67, 72)
ax2.set_ylim(11, 16)
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1+lines2, labels1+labels2, loc='lower left', fontsize=8)
ax.yaxis.label.set_color(C_BLUE)
ax2.yaxis.label.set_color(C_RED)

# --- [0,1] Subjective morning condition & sleep quality ---
ax = axes[0, 1]
ax.set_facecolor(C_LIGHT)
ax.plot(dates, df_all['起床時コンディション'], color=C_GREEN, lw=2, marker='o', ms=5, label='Morning Condition')
ax.plot(dates, df_all['睡眠の質'], color=C_PURPLE, lw=2, marker='^', ms=5, ls='--', label='Sleep Quality')
ax.fill_between(dates, df_all['起床時コンディション'].fillna(0), alpha=0.1, color=C_GREEN)
ax.set_title('Morning Condition & Sleep Quality (1-5)', fontweight='bold', fontsize=12)
ax.set_ylabel('Score (1=worst, 5=best)')
ax.set_ylim(0, 6)
ax.axhline(3, color='gray', ls=':', lw=1, alpha=0.5)
ax.tick_params(axis='x', rotation=45, labelsize=7)
ax.legend(fontsize=8)

# --- [1,0] Sleep hours ---
ax = axes[1, 0]
ax.set_facecolor(C_LIGHT)
bars = ax.bar(dates, df_all['睡眠時間'].fillna(0), color=C_BLUE, alpha=0.7, width=0.7)
ax.axhline(7, color=C_ORANGE, ls='--', lw=1.5, label='7h target')
ax.axhline(8, color=C_GREEN, ls='--', lw=1.5, label='8h ideal')
ax.set_title('Sleep Duration (hours)', fontweight='bold', fontsize=12)
ax.set_ylabel('Hours')
ax.set_ylim(5, 9.5)
ax.tick_params(axis='x', rotation=45, labelsize=7)
ax.legend(fontsize=8)

# --- [1,1] Training load (RPE x duration) ---
ax = axes[1, 1]
ax.set_facecolor(C_LIGHT)
# Color by training type
colors_map = {'実践トレーニング': C_ORANGE, 'ウエイトトレーニング': C_BLUE,
              '休養日': C_GRAY, '実践トレーニング+ウエイトトレーニング': C_RED}
load = (df_all['maxRPE'].fillna(1) * df_all['総時間'].fillna(0))
bar_colors = [colors_map.get(str(t), C_GRAY) for t in df_all['種目リスト'].fillna('休養日')]
bars = ax.bar(dates, load, color=bar_colors, alpha=0.85, width=0.7)
ax.set_title('Training Load  (RPE × Duration [min])', fontweight='bold', fontsize=12)
ax.set_ylabel('Load Index')
ax.tick_params(axis='x', rotation=45, labelsize=7)
patches = [mpatches.Patch(color=v, label=k) for k,v in colors_map.items()]
ax.legend(handles=patches, fontsize=7, loc='upper right')

# --- [2,0] Fatigue comparison ---
ax = axes[2, 0]
ax.set_facecolor(C_LIGHT)
ax.plot(dates, df_all['練習後疲労度'], color=C_RED, lw=2, marker='o', ms=5, label='Post-training Fatigue')
ax.plot(dates, df_all['運動後疲労'].fillna(np.nan), color=C_ORANGE, lw=2, marker='s', ms=5, ls='--', label='Training Log Fatigue')
ax.set_title('Fatigue Comparison (Subjective vs Training Log)', fontweight='bold', fontsize=12)
ax.set_ylabel('Score (1-5)')
ax.set_ylim(0, 6)
ax.axhline(3, color='gray', ls=':', lw=1, alpha=0.5)
ax.tick_params(axis='x', rotation=45, labelsize=7)
ax.legend(fontsize=8)

# --- [2,1] Nutrition ---
ax = axes[2, 1]
ax.set_facecolor(C_LIGHT)
bars1 = ax.bar(dates, df_all['タンパク質摂取数'].fillna(0), color=C_GREEN, alpha=0.7, width=0.7, label='Protein Sources (#)')
ax2 = ax.twinx()
ax2.plot(dates, df_all['栄養バランス'].fillna(np.nan), color=C_PURPLE, lw=2, marker='D', ms=5, label='Nutrition Balance')
ax2.plot(dates, df_all['食欲'].fillna(np.nan), color=C_ORANGE, lw=1.5, marker='v', ms=4, ls='--', label='Appetite')
ax.set_title('Nutrition: Protein Sources & Balance Score', fontweight='bold', fontsize=12)
ax.set_ylabel('# Protein Sources', color=C_GREEN)
ax2.set_ylabel('Score (1-5)', color=C_PURPLE)
ax.set_ylim(0, 7)
ax2.set_ylim(0, 6)
ax.tick_params(axis='x', rotation=45, labelsize=7)
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1+lines2, labels1+labels2, fontsize=7, loc='upper right')

plt.tight_layout(rect=[0, 0, 1, 0.97])
fig1.savefig('/home/user/AK/report_fig1_overview.png', dpi=150, bbox_inches='tight')
plt.close(fig1)
print("Fig1 saved")

# ============================================================
# FIGURE 2: Correlation / Relationship Analysis
# ============================================================
fig2, axes = plt.subplots(2, 3, figsize=(18, 11))
fig2.suptitle('Cross-Variable Relationship Analysis\n100m / 400m Track & Field',
              fontsize=14, fontweight='bold', y=0.98)
fig2.patch.set_facecolor('#F8F9FA')

# --- Scatter 1: Sleep quality vs Morning condition ---
ax = axes[0, 0]
ax.set_facecolor(C_LIGHT)
x = df_all['睡眠の質'].dropna()
y = df_all.loc[x.index, '起床時コンディション'].dropna()
common = x.index.intersection(y.index)
ax.scatter(x[common], y[common], color=C_PURPLE, s=80, alpha=0.7, edgecolors='white', lw=0.5)
m, b = np.polyfit(x[common], y[common], 1)
xr = np.linspace(x.min(), x.max(), 100)
ax.plot(xr, m*xr+b, color=C_RED, lw=2, ls='--')
corr = np.corrcoef(x[common], y[common])[0,1]
ax.set_title(f'Sleep Quality → Morning Condition\nr = {corr:.2f}', fontweight='bold')
ax.set_xlabel('Sleep Quality (1-5)')
ax.set_ylabel('Morning Condition (1-5)')
ax.set_xlim(0.5, 5.5); ax.set_ylim(0.5, 5.5)

# --- Scatter 2: Training RPE vs next-day morning condition ---
ax = axes[0, 1]
ax.set_facecolor(C_LIGHT)
rpe_vals, next_cond = [], []
for i in range(len(df_all)-1):
    rpe = df_all.loc[i, 'maxRPE']
    cond_next = df_all.loc[i+1, '起床時コンディション']
    if pd.notna(rpe) and pd.notna(cond_next) and rpe > 1:
        rpe_vals.append(rpe)
        next_cond.append(cond_next)
if len(rpe_vals) > 3:
    ax.scatter(rpe_vals, next_cond, color=C_ORANGE, s=80, alpha=0.7, edgecolors='white', lw=0.5)
    m, b = np.polyfit(rpe_vals, next_cond, 1)
    xr = np.linspace(min(rpe_vals), max(rpe_vals), 100)
    ax.plot(xr, m*xr+b, color=C_RED, lw=2, ls='--')
    corr = np.corrcoef(rpe_vals, next_cond)[0,1]
    ax.set_title(f'Training RPE → Next-day Morning Condition\nr = {corr:.2f}', fontweight='bold')
else:
    ax.set_title('Training RPE → Next-day Morning Condition', fontweight='bold')
ax.set_xlabel('RPE (1-10)')
ax.set_ylabel('Next-day Morning Condition (1-5)')

# --- Scatter 3: Sleep hours vs post-training fatigue ---
ax = axes[0, 2]
ax.set_facecolor(C_LIGHT)
x = df_all['睡眠時間'].dropna()
y = df_all.loc[x.index, '練習後疲労度'].dropna()
common = x.index.intersection(y.index)
ax.scatter(x[common], y[common], color=C_BLUE, s=80, alpha=0.7, edgecolors='white', lw=0.5)
m, b = np.polyfit(x[common], y[common], 1)
xr = np.linspace(x.min()-0.1, x.max()+0.1, 100)
ax.plot(xr, m*xr+b, color=C_RED, lw=2, ls='--')
corr = np.corrcoef(x[common], y[common])[0,1]
ax.set_title(f'Sleep Hours → Post-training Fatigue\nr = {corr:.2f}', fontweight='bold')
ax.set_xlabel('Sleep Hours')
ax.set_ylabel('Post-training Fatigue (1-5)')

# --- Bar 4: Training type breakdown ---
ax = axes[1, 0]
ax.set_facecolor(C_LIGHT)
type_counts = df_train['種目'].value_counts()
colors_pie = [C_ORANGE, C_BLUE, C_GRAY, C_RED][:len(type_counts)]
bars = ax.bar(range(len(type_counts)), type_counts.values, color=colors_pie, alpha=0.85)
ax.set_xticks(range(len(type_counts)))
ax.set_xticklabels(type_counts.index, fontsize=9)
ax.set_title('Training Type Distribution', fontweight='bold')
ax.set_ylabel('Sessions')
for bar, val in zip(bars, type_counts.values):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.1, str(val),
            ha='center', fontweight='bold', fontsize=10)

# --- Bar 5: Avg scores by training type ---
ax = axes[1, 1]
ax.set_facecolor(C_LIGHT)
main_types = ['実践トレーニング', 'ウエイトトレーニング']
metrics = ['爆発力', '持久力', '運動後疲労']
x_pos = np.arange(len(metrics))
width = 0.35
for i, ttype in enumerate(main_types):
    sub = df_train[df_train['種目'] == ttype]
    means = [sub[m].mean() for m in metrics]
    bars = ax.bar(x_pos + i*width, means, width, alpha=0.85,
                  label=ttype, color=[C_ORANGE, C_BLUE][i])
ax.set_xticks(x_pos + width/2)
ax.set_xticklabels(['Explosive\nPower', 'Endurance', 'Post-workout\nFatigue'], fontsize=9)
ax.set_title('Avg Scores by Training Type', fontweight='bold')
ax.set_ylabel('Score (1-5)')
ax.set_ylim(0, 5.5)
ax.legend(fontsize=8)

# --- Scatter 6: Post-workout supplement vs next-day condition ---
ax = axes[1, 2]
ax.set_facecolor(C_LIGHT)
merged = df_food.merge(df_cond[['日付','起床時コンディション']], on='日付', how='inner')
yes_cond = merged[merged['練習後補食_bin'] == 1]['起床時コンディション'].dropna()
no_cond  = merged[merged['練習後補食_bin'] == 0]['起床時コンディション'].dropna()
bp_data = [yes_cond.values, no_cond.values]
bp = ax.boxplot(bp_data, patch_artist=True, widths=0.5,
                boxprops=dict(facecolor=C_GREEN, alpha=0.7),
                medianprops=dict(color=C_RED, lw=2))
bp['boxes'][1].set_facecolor(C_GRAY)
ax.set_xticklabels(['Post-workout\nSupplement: YES', 'Post-workout\nSupplement: NO'], fontsize=9)
ax.set_title('Post-workout Supplement\nvs Morning Condition', fontweight='bold')
ax.set_ylabel('Morning Condition (1-5)')
ax.set_ylim(0, 6)
# Add mean markers
for i, d in enumerate([yes_cond, no_cond], 1):
    ax.plot(i, d.mean(), 'D', color=C_RED, ms=10, zorder=5)
    ax.text(i+0.15, d.mean(), f'mean={d.mean():.1f}', va='center', fontsize=9, color=C_RED)

plt.tight_layout(rect=[0, 0, 1, 0.96])
fig2.savefig('/home/user/AK/report_fig2_correlations.png', dpi=150, bbox_inches='tight')
plt.close(fig2)
print("Fig2 saved")

# ============================================================
# FIGURE 3: Weekly summary heatmap + radar
# ============================================================
fig3, axes = plt.subplots(1, 2, figsize=(16, 7))
fig3.suptitle('Training Quality & Condition Radar / Heatmap\n100m / 400m Track & Field',
              fontsize=14, fontweight='bold')
fig3.patch.set_facecolor('#F8F9FA')

# --- Heatmap: week x metric ---
ax = axes[0]
df_all['week'] = df_all['日付'].dt.isocalendar().week
week_groups = df_all.groupby('week').agg(
    Condition=('起床時コンディション', 'mean'),
    SleepQuality=('睡眠の質', 'mean'),
    SleepHours=('睡眠時間', 'mean'),
    Fatigue=('練習後疲労度', 'mean'),
    Nutrition=('栄養バランス', 'mean'),
    ProteinCount=('タンパク質摂取数', 'mean'),
).round(2)

# Normalize for heatmap (0-1)
heat_data = week_groups.copy()
for col in heat_data.columns:
    col_min, col_max = heat_data[col].min(), heat_data[col].max()
    if col_max > col_min:
        heat_data[col] = (heat_data[col] - col_min) / (col_max - col_min)

col_labels = ['Morning\nCondition', 'Sleep\nQuality', 'Sleep\nHours',
              'Post-train\nFatigue', 'Nutrition\nBalance', 'Protein\nCount']
week_labels = [f'W{w}' for w in week_groups.index]

im = ax.imshow(heat_data.values.T, aspect='auto', cmap='RdYlGn', vmin=0, vmax=1)
ax.set_xticks(range(len(week_labels)))
ax.set_xticklabels(week_labels)
ax.set_yticks(range(len(col_labels)))
ax.set_yticklabels(col_labels, fontsize=9)
ax.set_title('Weekly Average Heatmap\n(Green=Better, Red=Worse)', fontweight='bold')
plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

# Add values
for i in range(len(week_labels)):
    for j in range(len(col_labels)):
        val = week_groups.iloc[i, j]
        ax.text(i, j, f'{val:.1f}', ha='center', va='center', fontsize=8, fontweight='bold',
                color='black')

# --- Radar chart: first half vs second half ---
ax = axes[1]
ax.remove()
ax_r = fig3.add_subplot(1, 2, 2, projection='polar')

categories = ['Morning\nCondition', 'Sleep\nQuality', 'Sleep\nHours', 'Nutrition', 'Protein\nCount']
n = len(categories)
angles = [n_i / float(n) * 2 * np.pi for n_i in range(n)]
angles += angles[:1]

mid = len(df_all) // 2
def get_radar_vals(subset):
    return [
        subset['起床時コンディション'].mean() / 5,
        subset['睡眠の質'].mean() / 5,
        (subset['睡眠時間'].mean() - 5) / 4,
        subset['栄養バランス'].mean() / 5,
        subset['タンパク質摂取数'].mean() / 4,
    ]

vals1 = get_radar_vals(df_all.iloc[:mid])
vals2 = get_radar_vals(df_all.iloc[mid:])
vals1 += vals1[:1]
vals2 += vals2[:1]

ax_r.plot(angles, vals1, 'o-', lw=2, color=C_BLUE, label='1st Half (Mar-Apr)')
ax_r.fill(angles, vals1, alpha=0.15, color=C_BLUE)
ax_r.plot(angles, vals2, 's-', lw=2, color=C_RED, label='2nd Half (May)')
ax_r.fill(angles, vals2, alpha=0.15, color=C_RED)
ax_r.set_thetagrids([a*180/np.pi for a in angles[:-1]], categories, fontsize=9)
ax_r.set_ylim(0, 1)
ax_r.set_title('1st Half vs 2nd Half Comparison\n(Normalized 0-1)', fontweight='bold', pad=15)
ax_r.legend(loc='upper right', bbox_to_anchor=(1.3, 1.15), fontsize=9)

plt.tight_layout()
fig3.savefig('/home/user/AK/report_fig3_weekly.png', dpi=150, bbox_inches='tight')
plt.close(fig3)
print("Fig3 saved")

# ============================================================
# FIGURE 4: Training details - RPE, explosive, endurance
# ============================================================
fig4, axes = plt.subplots(2, 2, figsize=(16, 11))
fig4.suptitle('Training Details & Performance Indicators\n100m / 400m Track & Field',
              fontsize=14, fontweight='bold')
fig4.patch.set_facecolor('#F8F9FA')

# --- [0,0] RPE over time ---
ax = axes[0, 0]
ax.set_facecolor(C_LIGHT)
train_dates = df_train['日付']
ax.bar(train_dates, df_train['RPE'], color=[colors_map.get(t, C_GRAY) for t in df_train['種目']],
       alpha=0.8, width=0.7)
ax.set_title('RPE per Session (by training type)', fontweight='bold')
ax.set_ylabel('RPE (1-10)')
ax.set_ylim(0, 11)
ax.tick_params(axis='x', rotation=45, labelsize=7)
patches = [mpatches.Patch(color=v, label=k) for k,v in colors_map.items()]
ax.legend(handles=patches, fontsize=7)

# --- [0,1] Explosive vs endurance by training type ---
ax = axes[0, 1]
ax.set_facecolor(C_LIGHT)
practice = df_train[df_train['種目'] == '実践トレーニング']
weight   = df_train[df_train['種目'] == 'ウエイトトレーニング']
ax.scatter(practice['爆発力'], practice['持久力'], color=C_ORANGE, s=100, alpha=0.7,
           label='Practice', zorder=3, edgecolors='white')
ax.scatter(weight['爆発力'], weight['持久力'], color=C_BLUE, s=100, alpha=0.7,
           label='Weight Training', zorder=3, marker='s', edgecolors='white')
ax.set_title('Explosive Power vs Endurance per Session', fontweight='bold')
ax.set_xlabel('Explosive Power (1-5)')
ax.set_ylabel('Endurance (1-5)')
ax.set_xlim(0.5, 5.5); ax.set_ylim(0.5, 5.5)
ax.axhline(3, ls=':', color=C_GRAY); ax.axvline(3, ls=':', color=C_GRAY)
ax.legend(fontsize=9)

# --- [1,0] Post-workout supplement & protein vs appetite ---
ax = axes[1, 0]
ax.set_facecolor(C_LIGHT)
# Rolling 7-day avg of appetite and condition
df_all_sorted = df_all.set_index('日付').sort_index()
roll_cond = df_all_sorted['起床時コンディション'].rolling('7D', min_periods=1).mean()
roll_fat  = df_all_sorted['練習後疲労度'].rolling('7D', min_periods=1).mean()
roll_nutr = df_all_sorted['タンパク質摂取数'].rolling('7D', min_periods=1).mean()

ax.plot(roll_cond.index, roll_cond.values, color=C_GREEN, lw=2.5, label='7D avg: Morning Condition')
ax.plot(roll_fat.index, roll_fat.values, color=C_RED, lw=2.5, ls='--', label='7D avg: Post-train Fatigue')
ax2 = ax.twinx()
ax2.bar(roll_nutr.index, roll_nutr.values, color=C_ORANGE, alpha=0.3, width=0.8, label='7D avg: Protein Count')
ax.set_title('7-Day Rolling Average: Condition & Fatigue\n+ Protein Intake', fontweight='bold')
ax.set_ylabel('Condition / Fatigue Score')
ax2.set_ylabel('Protein Count (avg)')
ax.tick_params(axis='x', rotation=45, labelsize=7)
ax.set_ylim(0, 6)
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1+lines2, labels1+labels2, fontsize=7)

# --- [1,1] Summary stat table ---
ax = axes[1, 1]
ax.axis('off')
ax.set_facecolor(C_LIGHT)

summary_data = {
    'Metric': ['Body Weight (kg)', 'Body Fat (%)', 'Morning Condition (1-5)',
               'Sleep Hours (h)', 'Sleep Quality (1-5)', 'Post-train Fatigue (1-5)',
               'Nutrition Balance (1-5)', 'Protein Sources/day'],
    'Min': [df_all['体重_kg'].min(), df_all['体脂肪率_pct'].min(),
            df_all['起床時コンディション'].min(), df_all['睡眠時間'].min(),
            df_all['睡眠の質'].min(), df_all['練習後疲労度'].min(),
            df_all['栄養バランス'].min(), df_all['タンパク質摂取数'].min()],
    'Max': [df_all['体重_kg'].max(), df_all['体脂肪率_pct'].max(),
            df_all['起床時コンディション'].max(), df_all['睡眠時間'].max(),
            df_all['睡眠の質'].max(), df_all['練習後疲労度'].max(),
            df_all['栄養バランス'].max(), df_all['タンパク質摂取数'].max()],
    'Avg': [df_all['体重_kg'].mean(), df_all['体脂肪率_pct'].mean(),
            df_all['起床時コンディション'].mean(), df_all['睡眠時間'].mean(),
            df_all['睡眠の質'].mean(), df_all['練習後疲労度'].mean(),
            df_all['栄養バランス'].mean(), df_all['タンパク質摂取数'].mean()],
}
sdf = pd.DataFrame(summary_data)
table = ax.table(
    cellText=[[r, f'{mn:.1f}', f'{mx:.1f}', f'{av:.1f}']
              for r, mn, mx, av in zip(sdf['Metric'], sdf['Min'], sdf['Max'], sdf['Avg'])],
    colLabels=['Metric', 'Min', 'Max', 'Avg'],
    cellLoc='center', loc='center',
    bbox=[0, 0, 1, 1]
)
table.auto_set_font_size(False)
table.set_fontsize(9)
for (row, col), cell in table.get_celld().items():
    cell.set_edgecolor('#CCCCCC')
    if row == 0:
        cell.set_facecolor(C_BLUE)
        cell.set_text_props(color='white', fontweight='bold')
    elif row % 2 == 0:
        cell.set_facecolor('#F0F4F8')
    else:
        cell.set_facecolor('white')
ax.set_title('Summary Statistics', fontweight='bold', pad=10)

plt.tight_layout()
fig4.savefig('/home/user/AK/report_fig4_training.png', dpi=150, bbox_inches='tight')
plt.close(fig4)
print("Fig4 saved")

print("All figures generated successfully!")
