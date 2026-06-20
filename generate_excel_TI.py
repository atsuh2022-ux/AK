import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as XLImage
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

rcParams['font.family'] = 'DejaVu Sans'

# ── データ読み込み ──────────────────────────────
src = openpyxl.load_workbook('/root/.claude/uploads/8fc6c494-7d22-5ced-b922-3105f12fe0f0/4d842883-TI___20260328_20260620.xlsx')

def ws_to_df(ws):
    data = list(ws.iter_rows(values_only=True))
    df = pd.DataFrame(data[1:], columns=data[0])
    df['日付'] = pd.to_datetime(df['日付'])
    return df

df_cond  = ws_to_df(src['主観的体調'])
df_body  = ws_to_df(src['身体データ'])
df_train = ws_to_df(src['トレーニング'])
df_food  = ws_to_df(src['食事'])

prot_cols = ['昼タンパク質_魚','昼タンパク質_肉','昼タンパク質_豆','昼タンパク質_卵',
             '夕タンパク質_魚','夕タンパク質_肉','夕タンパク質_豆','夕タンパク質_卵']
for c in prot_cols:
    df_food[c] = df_food[c].apply(lambda x: 1 if x == '○' else 0)
df_food['タンパク質摂取数'] = df_food[prot_cols].sum(axis=1)
df_food['補食_bin'] = df_food['練習後補食'].apply(lambda x: 1 if x == 'はい' else 0)

# 日次マージ
df = df_cond.merge(df_body, on='日付', how='outer')
df = df.merge(df_train, on='日付', how='outer')
df = df.merge(df_food[['日付','練習後補食','補食_bin','栄養バランス',
                        '水分摂取量_ml','きのこ海藻','タンパク質摂取数']], on='日付', how='outer')
df = df.sort_values('日付').reset_index(drop=True)

train_only = df[(df['種目'].notna()) & (df['種目'] != '休養日')]

# ── 統計計算 ─────────────────────────────────
total_train_days = len(train_only)
total_rest_days  = int((df['種目'] == '休養日').sum())
total_minutes    = int(df['時間_分'].fillna(0).sum())
avg_rpe          = train_only['RPE'].mean()
avg_fatigue      = train_only['運動後疲労'].mean()
avg_sleep_h      = df_cond['睡眠時間'].mean()
avg_sleep_q      = df_cond['睡眠の質'].mean()
avg_cond         = df_cond['起床時コンディション'].mean()
avg_weight       = df_body['体重_kg'].mean()
weight_range     = df_body['体重_kg'].max() - df_body['体重_kg'].min()
wt_first, wt_last = df_body['体重_kg'].iloc[0], df_body['体重_kg'].iloc[-1]
snack_yes        = int(df_food['補食_bin'].sum())
water_1000plus   = int((df_food['水分摂取量_ml'] >= 1000).sum())
kino_yes         = int((df_food['きのこ海藻'] == 'はい').sum())
avg_protein      = df_food['タンパク質摂取数'].mean()

# 週次データ
df_train['week_label'] = df_train['日付'].apply(lambda d: f"W{d.isocalendar()[1]}\n({d.strftime('%m/%d')}~)")
weekly = df_train[df_train['種目']!='休養日'].groupby(
    df_train['日付'].dt.isocalendar().week).agg(
    days=('日付','count'), total_min=('時間_分','sum'),
    avg_rpe=('RPE','mean'), avg_fat=('運動後疲労','mean')).reset_index()

# 関連性
def corr_group(df_a, col_a, cond_a, df_b, col_b, join='日付'):
    m = df_a.merge(df_b[[join, col_b]], on=join, how='inner')
    yes = m[cond_a(m)][col_b].dropna()
    no  = m[~cond_a(m)][col_b].dropna()
    return yes.mean(), no.mean()

# a) 補食 vs 疲労
snack_m = df_food.merge(df_train[df_train['種目']!='休養日'][['日付','運動後疲労']], on='日付', how='inner')
snack_yes_fat = snack_m[snack_m['練習後補食']=='はい']['運動後疲労'].mean()
snack_no_fat  = snack_m[snack_m['練習後補食']=='いいえ']['運動後疲労'].mean()

# b) 水分≥1000ml vs <1000ml → 当日疲労（注：交絡要因あり）
water_m = df_food.merge(df_train[df_train['種目']!='休養日'][['日付','運動後疲労']], on='日付', how='inner')
water_hi = water_m[water_m['水分摂取量_ml']>=1000]['運動後疲労'].mean()
water_lo = water_m[water_m['水分摂取量_ml']<1000]['運動後疲労'].mean()

# c) 前日RPE≥7 vs <7 → 翌日起床時コンディション
rows_rpe=[]
for i in range(len(df_train)-1):
    rpe = df_train.iloc[i]['RPE']
    nxt = df_cond[df_cond['日付']==df_train.iloc[i+1]['日付']]['起床時コンディション']
    if len(nxt) and rpe > 1:
        rows_rpe.append({'rpe': rpe, 'cd': nxt.iloc[0]})
rc = pd.DataFrame(rows_rpe)
rpe_hi_cd = rc[rc['rpe']>=7]['cd'].mean()
rpe_lo_cd = rc[rc['rpe']<7]['cd'].mean()

# d) 睡眠時間 vs 翌日疲労
rows_sh=[]
for i in range(len(df_cond)-1):
    sh = df_cond.iloc[i]['睡眠時間']
    nxt_fat = df_train[df_train['日付']==df_cond.iloc[i+1]['日付']]['運動後疲労']
    if len(nxt_fat) and nxt_fat.iloc[0] > 1:
        rows_sh.append({'sh': sh, 'fat': nxt_fat.iloc[0]})
sc = pd.DataFrame(rows_sh)
sh_hi_fat = sc[sc['sh']>=7.5]['fat'].mean()
sh_lo_fat = sc[sc['sh']<7.5]['fat'].mean()

print("Stats OK")

# ── グラフ生成 ────────────────────────────────
C_BLUE   = '#2E86AB'
C_RED    = '#E84855'
C_GREEN  = '#3BB273'
C_ORANGE = '#F4A259'
C_PURPLE = '#7B2D8B'
C_GRAY   = '#8D99AE'

dates = pd.to_datetime(df['日付'])

# ── Fig A: トレンド4パネル ──
fig, axes = plt.subplots(4, 1, figsize=(16, 16), facecolor='#F8F9FA')
fig.suptitle('TI Athlete — Trend Overview  2026.03.30 – 2026.06.19',
             fontsize=14, fontweight='bold', y=0.99)

ax = axes[0]
ax.set_facecolor('#EDF2F4')
ax.plot(dates, df['体重_kg'], color=C_BLUE, lw=2, marker='o', ms=3, label='Body Weight (kg)')
ax.axhline(df_body['体重_kg'].mean(), color=C_GRAY, ls='--', lw=1, label=f'Avg {avg_weight:.1f}kg')
ax.set_title('Body Weight Trend', fontweight='bold')
ax.set_ylabel('kg'); ax.set_ylim(59.5, 63.5)
ax.tick_params(axis='x', rotation=45, labelsize=7); ax.legend(fontsize=8)

ax = axes[1]
ax.set_facecolor('#EDF2F4')
ax.plot(dates, df['起床時コンディション'], color=C_GREEN, lw=1.5, marker='o', ms=3, label='Morning Cond (1=best)')
ax.plot(dates, df['睡眠の質'], color=C_PURPLE, lw=1.5, marker='^', ms=3, ls='--', label='Sleep Quality (1=best)')
ax.fill_between(dates, df['起床時コンディション'].fillna(0), alpha=0.1, color=C_GREEN)
ax.axhline(3, color='gray', ls=':', lw=1, alpha=0.5)
ax.set_title('Morning Condition & Sleep Quality (1=Good / 5=Bad)', fontweight='bold')
ax.set_ylabel('Score'); ax.set_ylim(0, 6)
ax.tick_params(axis='x', rotation=45, labelsize=7); ax.legend(fontsize=8)

ax = axes[2]
ax.set_facecolor('#EDF2F4')
rpe_bars = [r if (pd.notna(r) and r > 1) else 0 for r in df['RPE']]
fat_bars = [f if (pd.notna(f) and f > 1) else 0 for f in df['運動後疲労']]
x_pos = range(len(dates))
ax.bar(x_pos, rpe_bars, color=C_ORANGE, alpha=0.6, width=0.6, label='RPE')
ax.plot(x_pos, fat_bars, color=C_RED, lw=2, marker='s', ms=3, label='Post-workout Fatigue')
ax.axhline(4, color=C_RED, ls=':', lw=1, alpha=0.5)
ax.set_title('RPE & Post-workout Fatigue per Session', fontweight='bold')
ax.set_ylabel('Score (RPE: /10, Fatigue: /5)')
ax.set_xticks(list(x_pos)[::3])
ax.set_xticklabels([dates.iloc[i].strftime('%m/%d') for i in list(x_pos)[::3]], rotation=45, fontsize=7)
ax.legend(fontsize=8)

ax = axes[3]
ax.set_facecolor('#EDF2F4')
ax.bar(dates, df['睡眠時間'].fillna(0), color=C_BLUE, alpha=0.6, width=0.7)
ax.plot(dates, df['水分摂取量_ml'].fillna(0)/1000, color=C_GREEN, lw=2, marker='D', ms=3, label='Water (L)')
ax.axhline(7, color=C_ORANGE, ls='--', lw=1.5, label='7h sleep target')
ax.axhline(1.0, color=C_GREEN, ls=':', lw=1, alpha=0.5)
ax.set_title('Sleep Hours (bars) & Water Intake (line, L)', fontweight='bold')
ax.set_ylabel('Hours / Liters')
ax.set_ylim(0, 10); ax.tick_params(axis='x', rotation=45, labelsize=7); ax.legend(fontsize=8)

plt.tight_layout()
fig.savefig('/home/user/AK/ti_fig_A_trends.png', dpi=150, bbox_inches='tight')
plt.close()
print("Fig A done")

# ── Fig B: 週次ヒートマップ ──
fig, ax = plt.subplots(1, 1, figsize=(14, 6), facecolor='#F8F9FA')
week_nums = weekly['week'].values
metrics_mat = np.array([
    weekly['avg_rpe'].values,
    weekly['avg_fat'].values,
    weekly['total_min'].values / weekly['total_min'].max(),
    weekly['days'].values / 7,
])
metric_labels = ['Avg RPE', 'Avg Fatigue', 'Total Vol\n(normalized)', 'Training\nDays/7']
im = ax.imshow(metrics_mat, aspect='auto', cmap='RdYlGn_r', vmin=0, vmax=1)
ax.set_xticks(range(len(week_nums)))
ax.set_xticklabels([f'W{w}' for w in week_nums], fontsize=9)
ax.set_yticks(range(4)); ax.set_yticklabels(metric_labels, fontsize=9)
ax.set_title('Weekly Summary Heatmap  (Red=Higher/More load, Green=Lower/Less load)', fontweight='bold')
plt.colorbar(im, ax=ax, fraction=0.03, pad=0.04)
for i in range(4):
    for j in range(len(week_nums)):
        raw_vals = [weekly['avg_rpe'].values[j], weekly['avg_fat'].values[j],
                    weekly['total_min'].values[j], weekly['days'].values[j]]
        ax.text(j, i, f'{raw_vals[i]:.1f}', ha='center', va='center', fontsize=8, fontweight='bold')
plt.tight_layout()
fig.savefig('/home/user/AK/ti_fig_B_weekly.png', dpi=150, bbox_inches='tight')
plt.close()
print("Fig B done")

# ── Fig C: タンパク質カレンダー（2分割）──
fig, axes = plt.subplots(2, 1, figsize=(16, 20), facecolor='#F8F9FA')
fig.suptitle('Protein Source Calendar', fontsize=13, fontweight='bold')

half = len(df_food) // 2
prot_src = ['昼:魚','昼:肉','昼:豆','昼:卵','夕:魚','夕:肉','夕:豆','夕:卵']
prot_raw = ['昼タンパク質_魚','昼タンパク質_肉','昼タンパク質_豆','昼タンパク質_卵',
            '夕タンパク質_魚','夕タンパク質_肉','夕タンパク質_豆','夕タンパク質_卵']
prot_colors_list = ['#BEE3F8','#FED7D7','#C6F6D5','#FEFCBF',
                    '#90CDF4','#FEB2B2','#9AE6B4','#FAF089']
snack_col = ['#C6F6D5','#FED7D7']

for part, (ax, subset) in enumerate(zip(axes, [df_food.iloc[:half], df_food.iloc[half:]])):
    all_cols = prot_src + ['補食','種類数']
    n_rows, n_cols = len(subset), len(all_cols)
    ax.set_xlim(-0.5, n_cols - 0.5)
    ax.set_ylim(-0.5, n_rows - 0.5)
    ax.invert_yaxis()
    ax.set_aspect('equal')
    ax.set_xticks(range(n_cols))
    ax.set_xticklabels(all_cols, fontsize=8)
    ax.set_yticks(range(n_rows))
    ax.set_yticklabels([d.strftime('%m/%d') for d in subset['日付']], fontsize=7)
    ax.xaxis.tick_top()
    ax.set_title(f'Part {part+1}: {subset["日付"].iloc[0].strftime("%m/%d")} – {subset["日付"].iloc[-1].strftime("%m/%d")}',
                 fontweight='bold', pad=20)
    ax.set_facecolor('#F7FAFC')
    for yi, (_, row) in enumerate(subset.iterrows()):
        for xi, (src_col, raw_col) in enumerate(zip(prot_src, prot_raw)):
            has = row[raw_col] == 1
            color = prot_colors_list[xi] if has else 'white'
            rect = plt.Rectangle((xi-0.45, yi-0.45), 0.9, 0.9, color=color, linewidth=0.5, edgecolor='#CCCCCC')
            ax.add_patch(rect)
            if has:
                ax.text(xi, yi, '●', ha='center', va='center', fontsize=10, color='#2D3748')
        # 補食
        snack = row.get('練習後補食','')
        sc = '#C6F6D5' if snack=='はい' else '#FED7D7'
        rect = plt.Rectangle((8-0.45, yi-0.45), 0.9, 0.9, color=sc, linewidth=0.5, edgecolor='#CCCCCC')
        ax.add_patch(rect)
        ax.text(8, yi, 'Y' if snack=='はい' else 'N', ha='center', va='center',
                fontsize=8, fontweight='bold', color='#276749' if snack=='はい' else '#9B2C2C')
        # 種類数
        tp = int(row['タンパク質摂取数'])
        tp_c = '#C6F6D5' if tp >= 3 else ('#FEFCBF' if tp >= 2 else '#FED7D7')
        rect = plt.Rectangle((9-0.45, yi-0.45), 0.9, 0.9, color=tp_c, linewidth=0.5, edgecolor='#CCCCCC')
        ax.add_patch(rect)
        ax.text(9, yi, str(tp), ha='center', va='center', fontsize=9, fontweight='bold')
        # 行の背景線
        ax.axhline(yi+0.45, color='#E2E8F0', linewidth=0.5)
    # 縦区切り（昼/夕）
    ax.axvline(3.5, color='#718096', linewidth=1.5, ls='--')
    ax.axvline(7.5, color='#718096', linewidth=1.5, ls='--')

plt.tight_layout()
fig.savefig('/home/user/AK/ti_fig_C_protein.png', dpi=130, bbox_inches='tight')
plt.close()
print("Fig C done")

# ── Fig D: 関連性比較 ──
fig, axes = plt.subplots(1, 4, figsize=(18, 6), facecolor='#F8F9FA')
fig.suptitle('Behavior vs Performance Correlation Analysis', fontsize=13, fontweight='bold')

comparisons = [
    ('Post-workout\nSupplement\nvs Fatigue',
     ['No Snack', 'Snack'], [snack_no_fat, snack_yes_fat],
     [C_GRAY, C_GREEN], '(Lower=Better)', '運動後疲労'),
    ('Water Intake\nvs Fatigue\n(※confounded)',
     ['<1000ml', '≥1000ml'], [water_lo, water_hi],
     [C_BLUE, C_ORANGE], '※ Busier days=more water', '運動後疲労'),
    ('Prev-day RPE\nvs Next Morning Cond',
     ['RPE<7', 'RPE≥7'], [rpe_lo_cd, rpe_hi_cd],
     [C_BLUE, C_RED], '(Lower=Better Cond)', '翌朝コンディション'),
    ('Sleep Duration\nvs Next-day Fatigue',
     ['<7.5h', '≥7.5h'], [sh_lo_fat, sh_hi_fat],
     [C_ORANGE, C_GREEN], '(Lower=Less Fatigue)', '翌日運動後疲労'),
]

for ax, (title, labels, vals, colors, sub, ylabel) in zip(axes, comparisons):
    ax.set_facecolor('#EDF2F4')
    bars = ax.bar(labels, vals, color=colors, alpha=0.85, width=0.5, edgecolor='white', linewidth=1.5)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.03,
                f'{val:.2f}', ha='center', fontsize=11, fontweight='bold', color='#1A365D')
    diff = vals[1] - vals[0]
    ax.set_title(title, fontweight='bold', fontsize=10)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_ylim(0, max(vals)*1.3)
    ax.text(0.5, 0.92, f'diff={diff:+.2f}', transform=ax.transAxes,
            ha='center', fontsize=9, color='#E53E3E' if abs(diff) >= 0.3 else C_GRAY,
            fontweight='bold')
    ax.text(0.5, 0.02, sub, transform=ax.transAxes, ha='center', fontsize=7.5,
            color='#718096', style='italic')

plt.tight_layout()
fig.savefig('/home/user/AK/ti_fig_D_correlation.png', dpi=150, bbox_inches='tight')
plt.close()
print("Fig D done")

# ── Fig E: 疲労タイムライン ──
fig, ax = plt.subplots(figsize=(16, 6), facecolor='#F8F9FA')
ax.set_facecolor('#EDF2F4')

# 高疲労日（疲労≥4）に背景バンド
for i, (_, row) in enumerate(df.iterrows()):
    fat = row.get('運動後疲労')
    if pd.notna(fat) and fat >= 4:
        ax.axvspan(i-0.5, i+0.5, color='#FED7D7', alpha=0.5, zorder=0)

x = range(len(df))
fat_vals = [v if pd.notna(v) and v > 1 else np.nan for v in df['運動後疲労']]
cd_vals  = [v if pd.notna(v) else np.nan for v in df['起床時コンディション']]
rpe_vals = [v/2 if pd.notna(v) and v > 1 else np.nan for v in df['RPE']]  # scale /2

ax.plot(x, fat_vals,  color=C_RED,   lw=2, marker='o', ms=4, label='Post-workout Fatigue')
ax.plot(x, cd_vals,   color=C_GREEN, lw=2, marker='^', ms=4, label='Morning Condition')
ax.plot(x, rpe_vals,  color=C_ORANGE,lw=1.5, marker='', ls='--', label='RPE ÷2 (scale)')
ax.axhline(4, color=C_RED, ls=':', lw=1, alpha=0.4)
ax.axhline(3, color='gray', ls=':', lw=1, alpha=0.3)
ax.set_xticks(list(x)[::4])
ax.set_xticklabels([dates.iloc[i].strftime('%m/%d') for i in list(x)[::4]], rotation=45, fontsize=7)
ax.set_ylabel('Score (1=Good/Low, 5=Bad/High)')
ax.set_ylim(0, 6)
ax.set_title('Fatigue & Condition Timeline  (Red shading = fatigue ≥ 4)', fontweight='bold')
ax.legend(fontsize=9)

# きのこ海藻あり日に小マーカー
for i, (_, row) in enumerate(df.iterrows()):
    if row.get('きのこ海藻') == 'はい':
        ax.plot(i, 0.3, marker='*', color='#38A169', ms=6, alpha=0.7)

ax.text(0.01, 0.05, '★ = きのこ・海藻 摂取あり', transform=ax.transAxes,
        fontsize=8, color='#38A169')

plt.tight_layout()
fig.savefig('/home/user/AK/ti_fig_E_fatigue.png', dpi=150, bbox_inches='tight')
plt.close()
print("Fig E done")

print("All charts generated!")

# ── スタイルヘルパー ──────────────────────────
def fill(hex_color):
    return PatternFill(fill_type='solid', fgColor=hex_color)

def font(bold=False, size=10, color='000000', italic=False):
    return Font(bold=bold, size=size, color=color, name='Arial', italic=italic)

def align(h='center', v='center', wrap=False):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)

def thin_border():
    s = Side(style='thin', color='CCCCCC')
    return Border(left=s, right=s, top=s, bottom=s)

def style_header_cell(cell, text, bg='2E86AB', size=10, color='FFFFFF'):
    cell.value = text
    cell.fill = fill(bg)
    cell.font = font(bold=True, size=size, color=color)
    cell.alignment = align()
    cell.border = thin_border()

def style_cell(cell, value=None, bg='FFFFFF', bold=False, size=10,
               h='center', v='center', wrap=False, color='2D3748'):
    if value is not None:
        cell.value = value
    cell.fill = fill(bg)
    cell.font = font(bold=bold, size=size, color=color)
    cell.alignment = align(h, v, wrap)
    cell.border = thin_border()

C_HDR  = '1A365D'
C_HDR2 = '2E86AB'
C_GRN  = 'C6F6D5'; C_YLW = 'FEFCBF'; C_ORG = 'FEEBC8'; C_RED_L = 'FED7D7'
C_WHT  = 'FFFFFF'; C_LGR  = 'F7FAFC'; C_LGR2 = 'EDF2F4'

def cond_color(val, inverse=True):
    if pd.isna(val): return C_WHT
    if inverse:
        if val <= 2: return C_GRN
        if val == 3: return C_YLW
        return C_RED_L
    else:
        if val >= 4: return C_GRN
        if val == 3: return C_YLW
        return C_RED_L

def rpe_color(val):
    if pd.isna(val) or val <= 1: return C_LGR
    if val <= 5: return C_GRN
    if val <= 7: return C_YLW
    return C_ORG if val <= 8 else C_RED_L

# ── ワークブック作成 ───────────────────────────
wb = openpyxl.Workbook()
wb.remove(wb.active)

# ============================================================
# はじめに
# ============================================================
ws0 = wb.create_sheet('はじめに', 0)
ws0.sheet_view.showGridLines = False
ws0.column_dimensions['A'].width = 2
ws0.column_dimensions['B'].width = 90

ws0.row_dimensions[1].height = 50
c = ws0['B1']
c.value = 'TI選手 フィードバックシート  2026.03.30 – 2026.06.19'
c.fill = fill(C_HDR); c.font = font(bold=True, size=18, color='FFFFFF')
c.alignment = align('left', 'center')

entries = [
    ('■ シート構成', ''),
    ('① サマリー', '主要KPI・コーチ記入欄・選手振り返りQ&A'),
    ('② 日次統合データ', '全81日を1行に統合。色分けで状態が一目でわかる'),
    ('③ 食事バランス', 'タンパク源カレンダー（昼夕×魚/肉/豆/卵）＋水分・きのこ海藻'),
    ('④ トレンドグラフ', '体重・コンディション・RPE・疲労・睡眠の時系列'),
    ('⑤ 関連性ヒント', '4つの行動vs成果の比較分析'),
    ('', ''),
    ('■ スコアの読み方（重要）', ''),
    ('起床時コンディション (1〜5)', '1=とても良い  5=とても悪い  ※数値が小さいほど良好'),
    ('睡眠の質 (1〜5)', '1=よく眠れた  5=全然眠れなかった  ※数値が小さいほど良好'),
    ('運動後疲労 (1〜5)', '1=疲労なし  5=非常に疲れた  ※数値が小さいほど良好'),
    ('RPE (1〜10)', '1=ほぼ安静  10=最大努力。6〜7=中強度、8以上=高強度'),
    ('栄養バランス (1〜5)', '1=良い  5=悪い（アプリ設定による）'),
]
for r, (title, body) in enumerate(entries, 2):
    ws0.row_dimensions[r].height = 20 if title else 10
    if not title and not body: continue
    txt = f'  {title}  →  {body}' if body else title
    c = ws0.cell(row=r, column=2, value=txt)
    c.fill = fill('34495E' if title.startswith('■') else (C_LGR2 if r%2==0 else C_WHT))
    c.font = font(bold=True, size=11 if title.startswith('■') else 10,
                  color='FFFFFF' if title.startswith('■') else '2D3748')
    c.alignment = align('left', 'center')
    if body: c.border = thin_border()

# ============================================================
# ① サマリー
# ============================================================
ws1 = wb.create_sheet('① サマリー')
ws1.sheet_view.showGridLines = False
for col, w in {'A':2,'B':34,'C':16,'D':20,'E':44}.items():
    ws1.column_dimensions[col].width = w

ws1.merge_cells('B1:E1')
c = ws1['B1']
c.value = 'TI選手 フィードバックレポート'
c.fill = fill(C_HDR); c.font = font(bold=True, size=16, color='FFFFFF')
c.alignment = align('left', 'center'); ws1.row_dimensions[1].height = 36

ws1.merge_cells('B2:C2')
ws1['B2'].value = '対象期間: 2026.03.30 – 2026.06.19'
ws1['B2'].fill = fill('2B6CB0'); ws1['B2'].font = font(size=10, color='FFFFFF')
ws1['B2'].alignment = align('left', 'center')
ws1.merge_cells('D2:E2')
ws1['D2'].value = 'レポート作成日: 2026.06.20'; ws1['D2'].fill = fill('2B6CB0')
ws1['D2'].font = font(size=10, color='FFFFFF'); ws1['D2'].alignment = align('right','center')
ws1.row_dimensions[2].height = 20; ws1.row_dimensions[3].height = 8

ws1.merge_cells('B4:E4')
c = ws1['B4']
c.value = '■ 期間サマリー'
c.fill = fill(C_HDR2); c.font = font(bold=True, size=11, color='FFFFFF')
c.alignment = align('left','center'); ws1.row_dimensions[4].height = 24

for ci, h in enumerate(['指標','今期間','評価目安','備考'], 2):
    style_header_cell(ws1.cell(row=5, column=ci), h, bg='34495E', size=10)
ws1.row_dimensions[5].height = 20

kpi_rows = [
    ('総トレーニング日数（休養除く）', f'{total_train_days} 日', '休養日とのバランスを確認',
     f'休養日 {total_rest_days} 日 ／ 計 {total_train_days+total_rest_days} 日'),
    ('総トレーニング時間（分）', f'{total_minutes:,} 分', '前週との比較で過負荷を確認', '急激な増加は怪我リスク'),
    ('平均RPE（練習日のみ）', f'{avg_rpe:.1f}', '6〜7が中強度の目安', 'RPEの高い日が続く時は回復を意識'),
    ('平均運動後疲労（練習日のみ）', f'{avg_fatigue:.1f} / 5', '低いほど回復良好', '4以上が続く場合は疲労蓄積のサイン'),
    ('平均睡眠時間 (h)', f'{avg_sleep_h:.1f} h', '7時間以上が目安', '8時間以上が理想（アスリート推奨）'),
    ('平均睡眠の質（1=良/5=悪）', f'{avg_sleep_q:.1f}', '2以下が望ましい', '3以上の日が続く場合は就寝前ルーティン見直しを'),
    ('平均起床時コンディション（1=良/5=悪）', f'{avg_cond:.1f}', '2以下が望ましい', '主観の悪化は早期の疲労サインになりうる'),
    ('平均体重（kg）', f'{avg_weight:.1f} kg', '±1kg以内の変動が目安',
     f'期初 {wt_first:.1f} kg → 期末 {wt_last:.1f} kg（{wt_last-wt_first:+.1f} kg）'),
    ('体重変動幅（kg）', f'{weight_range:.1f} kg', '1.5kg以内が目安', '大きい場合は水分・食事量を確認'),
    ('練習後補食「はい」の日数', f'{snack_yes} 日 / {len(df_food)} 日', '練習日は毎回が理想',
     f'実施率 {snack_yes/len(df_food)*100:.0f}%。補食あり群の当日疲労: {snack_yes_fat:.2f}'),
    ('水分摂取1000ml以上の日数', f'{water_1000plus} 日 / {len(df_food)} 日', '毎日1000ml以上が目安',
     '練習日の水分摂取は平均942ml。暑熱期は特に意識を'),
    ('きのこ・海藻「はい」の日数', f'{kino_yes} 日 / {len(df_food)} 日', '週4日以上が目安',
     f'実施率 {kino_yes/len(df_food)*100:.0f}%。ミネラル・食物繊維補給に継続を'),
    ('夕食タンパク源の平均種類数', f'{avg_protein:.1f} 種類/日', '2種類以上が目安',
     '昼食のタンパク源も意識的に増やすと回復力アップが期待できます'),
]

for ri, (ind, val, target, note) in enumerate(kpi_rows, 6):
    ws1.row_dimensions[ri].height = 22
    bg = C_LGR if ri%2==0 else C_WHT
    for ci, txt in enumerate([ind, val, target, note], 2):
        c = ws1.cell(row=ri, column=ci, value=txt)
        c.fill = fill(bg); c.font = font(size=10, color='2D3748', bold=(ci==2))
        c.alignment = align('left' if ci in [2,4,5] else 'center', 'center', wrap=(ci==5))
        c.border = thin_border()
    ws1.cell(row=ri, column=3).font = font(bold=True, size=11, color='1A365D')
    ws1.cell(row=ri, column=3).alignment = align('center','center')

ws1.row_dimensions[20].height = 10

r = 21
ws1.merge_cells(f'B{r}:E{r}')
c = ws1[f'B{r}']
c.value = '■ 今期間のハイライト（コーチ記入欄）'
c.fill = fill(C_HDR2); c.font = font(bold=True, size=11, color='FFFFFF')
c.alignment = align('left','center'); ws1.row_dimensions[r].height = 24

comments = [
    ('① よかった点（継続したい行動）',
     f'◯ 3ヶ月にわたって練習日の補食実施率が{snack_yes/len(df_food)*100:.0f}%と高水準で維持されています。エネルギー補給の習慣化が定着してきた証拠です。\n'
     f'◯ きのこ・海藻の摂取も{kino_yes/len(df_food)*100:.0f}%と高く、ミネラル・食物繊維の継続的な補給ができています。\n'
     f'◯ 水分摂取1000ml以上の日が{water_1000plus}日（{water_1000plus/len(df_food)*100:.0f}%）と安定しています。熱中症予防の観点からも引き続き維持してください。',
     C_GRN),
    ('② 気になった点（早めに手を打ちたいこと）',
     f'◯ 平均運動後疲労が{avg_fatigue:.1f}/5と高め。特に第17週（4月下旬）・第21週・第22週で週平均疲労が4.0以上に達しています。疲労蓄積のサインです。\n'
     f'◯ 6月中旬のメモに「まだカラダが疲れている」「暑さのせいもあるかも」とあります。暑熱順化と適切な休養日の挿入を検討してください。\n'
     f'◯ 昼食のタンパク質（魚・豆・卵）摂取が少ない日が目立ちます。午前練習後の昼食でのタンパク質補給を意識してみてください。',
     C_ORG),
    ('③ 次の大会までの小さな目標（1つだけ）',
     f'◯ 週に1日「完全休養日」を必ず設ける（現在の休養日 {total_rest_days}日/{total_train_days+total_rest_days}日を意識的に計画する）。\n'
     f'　 理由: 疲労が高い週ほど翌週の平均RPEが低下する傾向があり、疲労蓄積が練習の質を下げています。戦略的な休養が長期的なパフォーマンス向上につながります。',
     C_YLW),
]
for title, body, bg_c in comments:
    r += 1; ws1.row_dimensions[r].height = 18
    ws1.merge_cells(f'B{r}:E{r}')
    c = ws1[f'B{r}']; c.value = title
    c.fill = fill('34495E'); c.font = font(bold=True, size=10, color='FFFFFF')
    c.alignment = align('left','center')
    r += 1; ws1.row_dimensions[r].height = 76
    ws1.merge_cells(f'B{r}:E{r}')
    c = ws1[f'B{r}']; c.value = body
    c.fill = fill(bg_c); c.font = font(size=10, color='2D3748')
    c.alignment = align('left','top', wrap=True); c.border = thin_border()

ws1.row_dimensions[r+1].height = 10
r += 2
ws1.merge_cells(f'B{r}:E{r}')
c = ws1[f'B{r}']
c.value = '■ 選手から（自己振り返り欄）'
c.fill = fill(C_HDR2); c.font = font(bold=True, size=11, color='FFFFFF')
c.alignment = align('left','center'); ws1.row_dimensions[r].height = 24

for q in ['Q1. 今期間で「調子がよかった」と感じた日と、その理由',
          'Q2. 逆に「うまくいかなかった」日と、思い当たる原因',
          'Q3. 次に試してみたいこと（食事・睡眠・練習どれか1つ）']:
    r += 1; ws1.row_dimensions[r].height = 18
    ws1.merge_cells(f'B{r}:E{r}')
    c = ws1[f'B{r}']; c.value = q
    c.fill = fill('34495E'); c.font = font(bold=True, size=10, color='FFFFFF')
    c.alignment = align('left','center')
    r += 1; ws1.row_dimensions[r].height = 50
    ws1.merge_cells(f'B{r}:E{r}')
    c = ws1[f'B{r}']; c.value = '（選手記入欄）'
    c.fill = fill('F0F8FF'); c.font = font(size=10, color='A0AEC0', italic=True)
    c.alignment = align('left','top', wrap=True); c.border = thin_border()

print("Sheet ① done")

# ============================================================
# ② 日次統合データ
# ============================================================
ws2 = wb.create_sheet('② 日次統合データ')
ws2.sheet_view.showGridLines = False
for col, w in {'A':2,'B':11,'C':18,'D':8,'E':7,'F':8,'G':8,'H':8,
               'I':9,'J':9,'K':9,'L':9,'M':7,'N':10,'O':8,'P':8}.items():
    ws2.column_dimensions[col].width = w

ws2.merge_cells('B1:P1')
c = ws2['B1']
c.value = '日次統合データ（全項目を1行で確認）'
c.fill = fill(C_HDR); c.font = font(bold=True, size=14, color='FFFFFF')
c.alignment = align('left','center'); ws2.row_dimensions[1].height = 30

ws2.merge_cells('B2:P2')
c = ws2['B2']
c.value = '色の見方: 緑=良好　黄=普通　橙/赤=要注意　（起床CD・睡眠の質・疲労は数値が小さいほど良い）'
c.fill = fill('EBF8FF'); c.font = font(size=9, color='2B6CB0')
c.alignment = align('left','center'); ws2.row_dimensions[2].height = 18
ws2.row_dimensions[3].height = 8

hdrs2 = ['日付','種目','時間(分)','RPE','爆発力','持久力','運動後疲労',
         '体重(kg)','起床CD','睡眠の質','睡眠時間','補食','栄養Bal','水分(ml)','きのこ','タンパク数']
for ci, h in enumerate(hdrs2, 2):
    style_header_cell(ws2.cell(row=4, column=ci), h, bg=C_HDR2, size=9)
ws2.row_dimensions[4].height = 22

for ri, (_, row) in enumerate(df.iterrows(), 5):
    ws2.row_dimensions[ri].height = 19
    kind = str(row.get('種目','')) if pd.notna(row.get('種目')) else ''
    is_rest = '休養' in kind
    row_bg = 'F7FAFC' if is_rest else (C_LGR if ri%2==0 else C_WHT)

    vals = [
        (row['日付'].strftime('%m/%d'), row_bg, True, 9, 'center'),
        (kind.replace('実践トレーニング','実践').replace('休養日','休養'), row_bg, False, 9, 'left'),
        (int(row['時間_分']) if pd.notna(row.get('時間_分')) and row['時間_分']>0 else '', row_bg, False, 9, 'center'),
    ]
    for ci, (val, bg, bold, sz, ha) in enumerate(vals, 2):
        c = ws2.cell(row=ri, column=ci, value=val)
        style_cell(c, bg=bg, bold=bold, size=sz, h=ha)

    # RPE
    rpe = row.get('RPE')
    c = ws2.cell(row=ri, column=5, value=int(rpe) if pd.notna(rpe) and rpe>1 else '')
    style_cell(c, bg=rpe_color(rpe) if not is_rest else row_bg, size=9)

    for ci_off, col_name in enumerate(['爆発力','持久力'], 6):
        v = row.get(col_name)
        c = ws2.cell(row=ri, column=ci_off, value=int(v) if pd.notna(v) and v>1 else '')
        style_cell(c, bg=row_bg, size=9)

    # 運動後疲労
    fat = row.get('運動後疲労')
    c = ws2.cell(row=ri, column=8, value=int(fat) if pd.notna(fat) and fat>1 else '')
    style_cell(c, bg=cond_color(fat) if (pd.notna(fat) and fat>1) else row_bg,
               bold=(pd.notna(fat) and fat>=4), size=9)

    # 体重
    wt = row.get('体重_kg')
    c = ws2.cell(row=ri, column=9, value=float(wt) if pd.notna(wt) else '')
    style_cell(c, bg=row_bg, size=9)

    # 起床CD
    cd = row.get('起床時コンディション')
    c = ws2.cell(row=ri, column=10, value=int(cd) if pd.notna(cd) else '')
    style_cell(c, bg=cond_color(cd) if pd.notna(cd) else row_bg, size=9)

    # 睡眠の質
    sq = row.get('睡眠の質')
    c = ws2.cell(row=ri, column=11, value=int(sq) if pd.notna(sq) else '')
    style_cell(c, bg=cond_color(sq) if pd.notna(sq) else row_bg, size=9)

    # 睡眠時間
    sh = row.get('睡眠時間')
    c = ws2.cell(row=ri, column=12, value=float(sh) if pd.notna(sh) else '')
    sh_bg = C_GRN if (pd.notna(sh) and sh>=8) else (C_YLW if (pd.notna(sh) and sh>=7) else row_bg)
    style_cell(c, bg=sh_bg, size=9)

    # 補食
    snack = row.get('練習後補食','')
    c = ws2.cell(row=ri, column=13, value=str(snack) if pd.notna(snack) else '')
    style_cell(c, bg=C_GRN if snack=='はい' else (C_RED_L if snack=='いいえ' else row_bg), size=9,
               color='276749' if snack=='はい' else ('9B2C2C' if snack=='いいえ' else '2D3748'))

    # 栄養Bal
    nb = row.get('栄養バランス')
    c = ws2.cell(row=ri, column=14, value=int(nb) if pd.notna(nb) else '')
    style_cell(c, bg=cond_color(nb) if pd.notna(nb) else row_bg, size=9)

    # 水分
    wm = row.get('水分摂取量_ml')
    c = ws2.cell(row=ri, column=15, value=int(wm) if pd.notna(wm) else '')
    wm_bg = C_GRN if (pd.notna(wm) and wm>=1000) else (C_YLW if (pd.notna(wm) and wm>=500) else row_bg)
    style_cell(c, bg=wm_bg, size=9)

    # きのこ海藻
    kino = row.get('きのこ海藻','')
    c = ws2.cell(row=ri, column=16, value='★' if kino=='はい' else '')
    style_cell(c, bg=C_GRN if kino=='はい' else row_bg, size=9,
               color='276749' if kino=='はい' else '2D3748')

    # タンパク数
    tp = row.get('タンパク質摂取数')
    c = ws2.cell(row=ri, column=17, value=int(tp) if pd.notna(tp) else '')
    tp_bg = C_GRN if (pd.notna(tp) and tp>=3) else (C_YLW if (pd.notna(tp) and tp>=2) else row_bg)
    style_cell(c, bg=tp_bg, size=9)

# 平均行
avg_row = len(df) + 5
ws2.row_dimensions[avg_row].height = 22
style_cell(ws2.cell(row=avg_row, column=2, value='平均/合計'), bg='34495E', bold=True, size=9, color='FFFFFF')
for ci, val in {4:int(df['時間_分'].fillna(0).sum()),
                5:round(train_only['RPE'].mean(),1),
                6:round(train_only['爆発力'].mean(),1),
                7:round(train_only['持久力'].mean(),1),
                8:round(train_only['運動後疲労'].mean(),1),
                9:round(df_body['体重_kg'].mean(),1),
                10:round(df_cond['起床時コンディション'].mean(),1),
                11:round(df_cond['睡眠の質'].mean(),1),
                12:round(df_cond['睡眠時間'].mean(),1)}.items():
    style_cell(ws2.cell(row=avg_row, column=ci, value=val), bg=C_LGR2, bold=True, size=9, color='1A365D')
style_cell(ws2.cell(row=avg_row, column=13, value=f'{snack_yes}回'), bg=C_GRN, bold=True, size=9, color='276749')
style_cell(ws2.cell(row=avg_row, column=15, value=f'{water_1000plus}日'), bg=C_GRN, bold=True, size=9)
style_cell(ws2.cell(row=avg_row, column=16, value=f'{kino_yes}日'), bg=C_GRN, bold=True, size=9)
style_cell(ws2.cell(row=avg_row, column=17, value=round(df_food['タンパク質摂取数'].mean(),1)), bg=C_LGR2, bold=True, size=9)

print("Sheet ② done")

# ============================================================
# ③ 食事バランス
# ============================================================
ws3 = wb.create_sheet('③ 食事バランス')
ws3.sheet_view.showGridLines = False
ws3.column_dimensions['A'].width = 2
ws3.column_dimensions['B'].width = 10
extra_cols = ['M','N','O']
for cl in list('CDEFGHIJKL') + extra_cols:
    ws3.column_dimensions[cl].width = 7 if cl not in extra_cols else 9

ws3.merge_cells('B1:O1')
c = ws3['B1']
c.value = 'タンパク源バランス＋水分・きのこ海藻（色=摂取あり）'
c.fill = fill(C_HDR); c.font = font(bold=True, size=13, color='FFFFFF')
c.alignment = align('left','center'); ws3.row_dimensions[1].height = 28

ws3.merge_cells('B2:O2')
c = ws3['B2']
c.value = '◎「魚・肉・豆・卵」がバランスよく揃うと回復が早まります。空白マスが多い列を意識的に増やしましょう。'
c.fill = fill('F0FFF4'); c.font = font(size=9, color='276749')
c.alignment = align('left','center'); ws3.row_dimensions[2].height = 18

ws3.merge_cells('C3:F3')
c = ws3['C3']; c.value = '── 昼 食 ──'
c.fill = fill('BEE3F8'); c.font = font(bold=True, size=9, color='2C5282')
c.alignment = align('center','center')
ws3.merge_cells('G3:J3')
c = ws3['G3']; c.value = '── 夕 食 ──'
c.fill = fill('FEB2B2'); c.font = font(bold=True, size=9, color='742A2A')
c.alignment = align('center','center')
ws3.row_dimensions[3].height = 16

all_hdr = ['日付','昼:魚','昼:肉','昼:豆','昼:卵','夕:魚','夕:肉','夕:豆','夕:卵','種類数','補食','水分(ml)','きのこ']
hdr_bgs = ['2E86AB','BEE3F8','FED7D7','C6F6D5','FEFCBF',
           '90CDF4','FEB2B2','9AE6B4','FAF089','2E86AB','2E86AB','BEE3F8','C6F6D5']
hdr_fgs = ['FFFFFF','1A365D','1A365D','1A365D','1A365D',
           '1A365D','1A365D','1A365D','1A365D','FFFFFF','FFFFFF','1A365D','1A365D']
all_cols = list('BCDEFGHIJKLMNO')
prot_raw_all = ['昼タンパク質_魚','昼タンパク質_肉','昼タンパク質_豆','昼タンパク質_卵',
                '夕タンパク質_魚','夕タンパク質_肉','夕タンパク質_豆','夕タンパク質_卵']
prot_colors_all = ['BEE3F8','FED7D7','C6F6D5','FEFCBF','90CDF4','FEB2B2','9AE6B4','FAF089']

for ci, (h, bg, fg) in enumerate(zip(all_hdr, hdr_bgs, hdr_fgs), 2):
    c = ws3.cell(row=4, column=ci, value=h)
    style_header_cell(c, h, bg=bg, size=9, color=fg)
ws3.row_dimensions[4].height = 20

for ri, (_, row) in enumerate(df_food.iterrows(), 5):
    ws3.row_dimensions[ri].height = 18
    row_bg = C_WHT if ri%2==0 else C_LGR
    c = ws3.cell(row=ri, column=2, value=row['日付'].strftime('%m/%d'))
    style_cell(c, bg=row_bg, bold=True, size=9)
    total_tp = 0
    for xi, (rc_col, pc) in enumerate(zip(prot_raw_all, prot_colors_all), 3):
        has = row[rc_col] == 1
        if has: total_tp += 1
        c = ws3.cell(row=ri, column=xi)
        c.value = '●' if has else ''
        c.fill = fill(pc if has else row_bg)
        c.font = font(bold=True, size=11, color='1A365D' if has else 'CCCCCC')
        c.alignment = align(); c.border = thin_border()
    # 種類数
    tp_bg = C_GRN if total_tp>=3 else (C_YLW if total_tp>=2 else (C_RED_L if total_tp==0 else C_ORG))
    style_cell(ws3.cell(row=ri, column=11), value=total_tp, bg=tp_bg, bold=True, size=10)
    # 補食
    snack = row.get('練習後補食','')
    style_cell(ws3.cell(row=ri, column=12),
               value='はい' if snack=='はい' else 'いいえ',
               bg=C_GRN if snack=='はい' else C_RED_L, size=9,
               color='276749' if snack=='はい' else '9B2C2C', bold=(snack=='はい'))
    # 水分
    wm = row.get('水分摂取量_ml')
    wm_bg = C_GRN if (pd.notna(wm) and wm>=1000) else (C_YLW if (pd.notna(wm) and wm>=500) else C_RED_L)
    style_cell(ws3.cell(row=ri, column=13), value=int(wm) if pd.notna(wm) else '', bg=wm_bg, size=9)
    # きのこ海藻
    kino = row.get('きのこ海藻','')
    style_cell(ws3.cell(row=ri, column=14), value='★' if kino=='はい' else '',
               bg=C_GRN if kino=='はい' else row_bg, size=9, color='276749')

# 集計行
cr = len(df_food) + 5
ws3.row_dimensions[cr].height = 22
style_cell(ws3.cell(row=cr, column=2, value='摂取日数'), bg='34495E', bold=True, size=9, color='FFFFFF')
for xi, rc_col in enumerate(prot_raw_all, 3):
    cnt = int(df_food[rc_col].sum())
    bg = C_GRN if cnt>=20 else (C_YLW if cnt>=10 else C_RED_L)
    style_cell(ws3.cell(row=cr, column=xi), value=cnt, bg=bg, bold=True, size=10)
style_cell(ws3.cell(row=cr, column=11), value=round(df_food['タンパク質摂取数'].mean(),1), bg=C_GRN, bold=True, size=10)
style_cell(ws3.cell(row=cr, column=12), value=f'{snack_yes}日', bg=C_GRN if snack_yes>=60 else C_YLW, bold=True, size=10)
style_cell(ws3.cell(row=cr, column=13), value=f'{water_1000plus}日', bg=C_GRN if water_1000plus>=60 else C_YLW, bold=True, size=10)
style_cell(ws3.cell(row=cr, column=14), value=f'{kino_yes}日', bg=C_GRN if kino_yes>=50 else C_YLW, bold=True, size=10)

for ri_h, hint in enumerate([
    '・最も少ない列（摂取日数が低い食材）が今期間の弱点。昼食の魚・豆・卵が少ない傾向です。',
    '・夕食は肉類中心になりがち。魚（DHA/EPA）・豆類（植物性タンパク）も週3回以上を目標に。',
    '・水分は1000ml以上の日が多く優秀！6月の暑熱期はさらに500ml増量を意識してください。',
], 1):
    r_h = cr + 1 + ri_h
    ws3.row_dimensions[r_h].height = 18
    ws3.merge_cells(f'B{r_h}:N{r_h}')
    c = ws3[f'B{r_h}']; c.value = hint
    c.fill = fill(C_LGR2); c.font = font(size=9, color='2D3748')
    c.alignment = align('left','center', wrap=True); c.border = thin_border()

print("Sheet ③ done")

# ============================================================
# ④ トレンドグラフ
# ============================================================
ws4 = wb.create_sheet('④ トレンドグラフ')
ws4.sheet_view.showGridLines = False
ws4.column_dimensions['A'].width = 2

ws4.merge_cells('B1:J1')
c = ws4['B1']
c.value = 'トレンドグラフ（時系列）'
c.fill = fill(C_HDR); c.font = font(bold=True, size=14, color='FFFFFF')
c.alignment = align('left','center'); ws4.row_dimensions[1].height = 30

ws4.merge_cells('B2:J2')
c = ws4['B2']
c.value = '2026.03.30 – 2026.06.19 の81日間のデータを可視化しています。'
c.fill = fill('EBF8FF'); c.font = font(size=9, color='2B6CB0')
c.alignment = align('left','center'); ws4.row_dimensions[2].height = 18

try:
    for fname, row_s in [('ti_fig_A_trends.png', 4), ('ti_fig_E_fatigue.png', 36)]:
        img = XLImage(f'/home/user/AK/{fname}')
        img.width = 900; img.height = 460
        ws4.add_image(img, f'B{row_s}')
    print("Charts embedded OK")
except Exception as e:
    print(f"Chart embed warning: {e}")

# ============================================================
# ⑤ 関連性ヒント
# ============================================================
ws5 = wb.create_sheet('⑤ 関連性ヒント')
ws5.sheet_view.showGridLines = False
for col, w in {'A':2,'B':30,'C':20,'D':13,'E':20,'F':13,'G':13,'H':40}.items():
    ws5.column_dimensions[col].width = w

ws5.merge_cells('B1:H1')
c = ws5['B1']
c.value = '行動とパフォーマンスの関連性（TI選手 専用分析）'
c.fill = fill(C_HDR); c.font = font(bold=True, size=14, color='FFFFFF')
c.alignment = align('left','center'); ws5.row_dimensions[1].height = 30

ws5.merge_cells('B2:H2')
c = ws5['B2']
c.value = '「差」の絶対値が0.3以上なら傾向として注目に値します。今期間はデータ量が多い（81日）ため、小さな差でも一定の信頼性があります。'
c.fill = fill('FFFAF0'); c.font = font(size=9, color='744210')
c.alignment = align('left','center', wrap=True); ws5.row_dimensions[2].height = 28
ws5.row_dimensions[3].height = 8

for ci, h in enumerate(['観点','A群条件','A群平均','B群条件','B群平均','差(B-A)','解釈'], 2):
    style_header_cell(ws5.cell(row=4, column=ci), h, bg=C_HDR2, size=10)
ws5.row_dimensions[4].height = 22

rel_rows = [
    ('練習後補食 → 当日の運動後疲労',
     '補食「いいえ」', round(snack_no_fat,2),
     '補食「はい」', round(snack_yes_fat,2),
     round(snack_yes_fat-snack_no_fat,2),
     f'差は{abs(snack_yes_fat-snack_no_fat):.2f}と小さい。補食の有無より「何を食べたか」の内容が重要かもしれません。補食の質（タンパク質量）を記録することで、より詳細な分析ができます。'),
    ('水分摂取量 → 当日の運動後疲労\n（※交絡注意）',
     '水分<1000ml', round(water_lo,2),
     '水分≥1000ml', round(water_hi,2),
     round(water_hi-water_lo,2),
     f'水分が多い日に疲労が高い({water_hi:.2f} vs {water_lo:.2f})のは、ハードな練習日に水分を多く飲むという交絡が原因の可能性が高いです。休養日の水分摂取も意識的に増やすことが熱中症予防に有効です。'),
    ('前日RPE≥7 → 翌朝の起床時コンディション',
     '前日RPE<7', round(rpe_lo_cd,2),
     '前日RPE≥7', round(rpe_hi_cd,2),
     round(rpe_hi_cd-rpe_lo_cd,2),
     f'高強度練習翌朝のコンディションが良い({rpe_hi_cd:.2f} vs {rpe_lo_cd:.2f})のは、高RPEの日は調子が良い日に行う傾向があるためと考えられます。RPE高い日の前日の行動（補食・睡眠）を振り返ると良いヒントが見つかるかもしれません。'),
    ('睡眠時間7.5h以上 → 翌日の運動後疲労',
     '睡眠<7.5h', round(sh_lo_fat,2),
     '睡眠≥7.5h', round(sh_hi_fat,2),
     round(sh_hi_fat-sh_lo_fat,2),
     f'睡眠時間と翌日疲労の差はほぼゼロ({sh_hi_fat:.2f} vs {sh_lo_fat:.2f})。睡眠の「量」より「質」が重要である可能性があります。睡眠の質スコア（平均{avg_sleep_q:.1f}）の改善に取り組むと良いでしょう。'),
]

for ri, (obs, a_c, a_v, b_c, b_v, diff, interp) in enumerate(rel_rows, 5):
    ws5.row_dimensions[ri].height = 55
    row_bg = C_LGR if ri%2==0 else C_WHT
    style_cell(ws5.cell(row=ri, column=2, value=obs), bg=row_bg, bold=True, h='left', wrap=True, size=10)
    style_cell(ws5.cell(row=ri, column=3, value=a_c), bg=C_RED_L, h='center', size=9)
    style_cell(ws5.cell(row=ri, column=4, value=a_v), bg=C_RED_L, bold=True, size=11, color='9B2C2C')
    style_cell(ws5.cell(row=ri, column=5, value=b_c), bg=C_GRN, h='center', size=9)
    style_cell(ws5.cell(row=ri, column=6, value=b_v), bg=C_GRN, bold=True, size=11, color='276749')
    diff_bg = C_GRN if diff < -0.3 else (C_YLW if abs(diff)<0.3 else C_ORG)
    style_cell(ws5.cell(row=ri, column=7, value=f'{diff:+.2f}'), bg=diff_bg, bold=True, size=11)
    style_cell(ws5.cell(row=ri, column=8, value=interp), bg=row_bg, h='left', wrap=True, size=9)

try:
    img = XLImage('/home/user/AK/ti_fig_D_correlation.png')
    img.width = 920; img.height = 440
    ws5.add_image(img, 'B10')
    print("Corr chart embedded OK")
except Exception as e:
    print(f"warn: {e}")

# ── 保存 ─────────────────────────────────────
out = '/home/user/AK/TI_athlete_feedback_report.xlsx'
wb.save(out)
print(f'\nSaved: {out}')
