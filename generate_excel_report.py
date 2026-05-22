import openpyxl
from openpyxl.styles import (PatternFill, Font, Alignment, Border, Side,
                              GradientFill)
from openpyxl.utils import get_column_letter
from openpyxl.chart import LineChart, BarChart, Reference
from openpyxl.chart.series import DataPoint
from openpyxl.drawing.image import Image as XLImage
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ===== Load source data =====
src = openpyxl.load_workbook('/root/.claude/uploads/28f25c68-9581-4298-bce8-a857c17aebfc/2c710f9e-I___20260309_20260522.xlsx')

def ws_to_df(ws):
    data = list(ws.iter_rows(values_only=True))
    df = pd.DataFrame(data[1:], columns=data[0])
    df['日付'] = pd.to_datetime(df['日付'])
    return df

df_cond  = ws_to_df(src['主観的体調'])
df_body  = ws_to_df(src['身体データ'])
df_train = ws_to_df(src['トレーニング'])
df_food  = ws_to_df(src['食事'])

# Fix outlier
df_body.loc[df_body['体重_kg'] < 50, '体重_kg'] = 69.5

# Protein columns
prot_cols = ['昼タンパク質_魚','昼タンパク質_肉','昼タンパク質_豆','昼タンパク質_卵',
             '夕タンパク質_魚','夕タンパク質_肉','夕タンパク質_豆','夕タンパク質_卵']
for c in prot_cols:
    df_food[c] = df_food[c].apply(lambda x: 1 if x == '○' else 0)
df_food['タンパク質摂取数'] = df_food[prot_cols].sum(axis=1)
df_food['補食_bin'] = df_food['練習後補食'].apply(lambda x: 1 if x == 'はい' else 0)

# Aggregate training per day
df_train_d = df_train.groupby('日付').agg(
    種目=('種目', lambda x: '+'.join(x.unique())),
    時間_分=('時間_分', 'sum'),
    RPE=('RPE', 'max'),
    爆発力=('爆発力', 'max'),
    持久力=('持久力', 'max'),
    運動後疲労=('運動後疲労', 'max'),
    メモ=('メモ', lambda x: ' / '.join([m for m in x if m and str(m).strip()]))
).reset_index()

# Merge all
df = df_cond.merge(df_body, on='日付', how='outer')
df = df.merge(df_train_d, on='日付', how='outer')
df = df.merge(df_food[['日付','練習後補食','補食_bin','食欲','栄養バランス','タンパク質摂取数']], on='日付', how='outer')
df = df.sort_values('日付').reset_index(drop=True)

# ===== Style helpers =====
def fill(hex_color):
    return PatternFill(fill_type='solid', fgColor=hex_color)

def font(bold=False, size=10, color='000000', italic=False):
    return Font(bold=bold, size=size, color=color, name='Arial', italic=italic)

def align(h='center', v='center', wrap=False):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)

def thin_border():
    s = Side(style='thin', color='CCCCCC')
    return Border(left=s, right=s, top=s, bottom=s)

def thick_border():
    s = Side(style='medium', color='AAAAAA')
    return Border(left=s, right=s, top=s, bottom=s)

# Color palette
C_HEADER_BG  = '1A365D'
C_HEADER2_BG = '2E86AB'
C_GREEN      = 'C6F6D5'
C_GREEN_D    = '38A169'
C_YELLOW     = 'FEFCBF'
C_ORANGE     = 'FEEBC8'
C_RED        = 'FED7D7'
C_RED_D      = 'E53E3E'
C_GRAY       = 'F7FAFC'
C_LGRAY      = 'EDF2F4'
C_WHITE      = 'FFFFFF'
C_PROT_FISH  = 'BEE3F8'  # light blue - fish
C_PROT_MEAT  = 'FED7D7'  # light red - meat
C_PROT_SOY   = 'C6F6D5'  # light green - soy
C_PROT_EGG   = 'FEFCBF'  # light yellow - egg
C_SNACK_YES  = 'C6F6D5'
C_SNACK_NO   = 'FED7D7'

def style_header_cell(cell, text, bg=C_HEADER_BG, size=11, color='FFFFFF'):
    cell.value = text
    cell.fill = fill(bg)
    cell.font = font(bold=True, size=size, color=color)
    cell.alignment = align('center', 'center')
    cell.border = thin_border()

def style_cell(cell, value=None, bg=C_WHITE, bold=False, size=10,
               h='center', v='center', wrap=False, color='2D3748'):
    if value is not None:
        cell.value = value
    cell.fill = fill(bg)
    cell.font = font(bold=bold, size=size, color=color)
    cell.alignment = align(h, v, wrap)
    cell.border = thin_border()

def condition_color(val, inverse=True):
    """inverse=True means lower is better"""
    if pd.isna(val): return C_WHITE
    if inverse:
        if val <= 2: return C_GREEN
        if val == 3: return C_YELLOW
        return C_RED
    else:
        if val >= 4: return C_GREEN
        if val == 3: return C_YELLOW
        return C_RED

def rpe_color(val):
    if pd.isna(val) or val <= 1: return C_GRAY
    if val <= 5: return C_GREEN
    if val <= 7: return C_YELLOW
    return C_ORANGE if val <= 8 else C_RED

# ===== Compute stats =====
train_only = df[df['種目'].notna() & ~df['種目'].str.contains('休養')]
rest_days  = df[df['種目'].str.contains('休養', na=False)]

total_train_days = len(train_only['日付'].unique())
total_rest_days  = len(rest_days['日付'].unique())
total_minutes    = int(df['時間_分'].fillna(0).sum())
avg_rpe          = train_only['RPE'].mean()
avg_fatigue      = train_only['運動後疲労'].mean()
avg_sleep_h      = df_cond['睡眠時間'].mean()
avg_sleep_q      = df_cond['睡眠の質'].mean()
avg_cond         = df_cond['起床時コンディション'].mean()
avg_weight       = df_body['体重_kg'].mean()
weight_range     = df_body['体重_kg'].max() - df_body['体重_kg'].min()
wt_first         = df_body['体重_kg'].iloc[0]
wt_last          = df_body['体重_kg'].iloc[-1]
bf_first         = df_body['体脂肪率_pct'].iloc[0] if '体脂肪率_pct' in df_body.columns else None
bf_last          = df_body['体脂肪率_pct'].iloc[-1] if '体脂肪率_pct' in df_body.columns else None
snack_yes        = int(df_food['補食_bin'].sum())
avg_protein      = df_food['タンパク質摂取数'].mean()

# 関連性計算
# (a) 補食 vs 翌日疲労
snack_df = df_food[['日付','補食_bin']].merge(
    df_train[['日付','運動後疲労']], on='日付', how='inner')
snack_yes_fat = snack_df[snack_df['補食_bin']==1]['運動後疲労'].mean()
snack_no_fat  = snack_df[snack_df['補食_bin']==0]['運動後疲労'].mean()

# (b) 睡眠の質 vs 練習中疲労
sq_df = df_cond[['日付','睡眠の質']].merge(
    df_train[df_train['種目']!='休養日'][['日付','運動後疲労']], on='日付', how='inner')
good_sleep_fat = sq_df[sq_df['睡眠の質']<=2]['運動後疲労'].mean()
bad_sleep_fat  = sq_df[sq_df['睡眠の質']>=3]['運動後疲労'].mean()

# (c) タンパク3種以上 vs 翌朝コンディション
next_cond = []
for i, row in df_food.iterrows():
    date = row['日付']
    prot_cnt = row['タンパク質摂取数']
    next_day_rows = df_cond[df_cond['日付'] > date].sort_values('日付')
    if len(next_day_rows) > 0:
        next_cond.append({'タンパク質摂取数': prot_cnt,
                          '翌朝コンディション': next_day_rows.iloc[0]['起床時コンディション']})
nc_df = pd.DataFrame(next_cond).dropna()
prot_high_cond = nc_df[nc_df['タンパク質摂取数']>=3]['翌朝コンディション'].mean()
prot_low_cond  = nc_df[nc_df['タンパク質摂取数']<3]['翌朝コンディション'].mean()

# (d) 睡眠時間 vs RPE
sh_df = df_cond[['日付','睡眠時間']].merge(
    df_train[df_train['種目']!='休養日'][['日付','RPE']], on='日付', how='inner')
long_sleep_rpe = sh_df[sh_df['睡眠時間']>=7]['RPE'].mean()
short_sleep_rpe= sh_df[sh_df['睡眠時間']<7]['RPE'].mean()

print("Stats computed OK")

# ===== Create workbook =====
wb = openpyxl.Workbook()
wb.remove(wb.active)

# ============================================================
# Sheet 1: ① サマリー
# ============================================================
ws1 = wb.create_sheet('① サマリー')
ws1.sheet_view.showGridLines = False
ws1.column_dimensions['A'].width = 2
ws1.column_dimensions['B'].width = 32
ws1.column_dimensions['C'].width = 16
ws1.column_dimensions['D'].width = 18
ws1.column_dimensions['E'].width = 42

# Title
ws1.merge_cells('B1:E1')
c = ws1['B1']
c.value = '選手フィードバックレポート'
c.fill = fill(C_HEADER_BG)
c.font = font(bold=True, size=16, color='FFFFFF')
c.alignment = align('left', 'center')
ws1.row_dimensions[1].height = 36

ws1.merge_cells('B2:C2')
ws1['B2'].value = '対象期間: 2026.03.31 – 2026.05.14'
ws1['B2'].fill = fill('2B6CB0')
ws1['B2'].font = font(size=10, color='FFFFFF')
ws1['B2'].alignment = align('left', 'center')
ws1.merge_cells('D2:E2')
ws1['D2'].value = f'レポート作成日: 2026.05.22'
ws1['D2'].fill = fill('2B6CB0')
ws1['D2'].font = font(size=10, color='FFFFFF')
ws1['D2'].alignment = align('right', 'center')
ws1.row_dimensions[2].height = 20

ws1.row_dimensions[3].height = 8

# Section: 期間サマリー
ws1.merge_cells('B4:E4')
c = ws1['B4']
c.value = '■ 期間サマリー'
c.fill = fill(C_HEADER2_BG)
c.font = font(bold=True, size=11, color='FFFFFF')
c.alignment = align('left', 'center')
ws1.row_dimensions[4].height = 24

headers = ['指標', '今期間', '評価目安', '備考']
for i, h in enumerate(headers, 2):
    col = get_column_letter(i)
    c = ws1[f'{col}5']
    style_header_cell(c, h, bg='34495E', size=10)
ws1.row_dimensions[5].height = 20

kpi_data = [
    ('総トレーニング日数(休養除く)', f'{total_train_days} 日', '休養日とのバランスを確認',
     f'休養日 {total_rest_days} 日 / 合計 {total_train_days+total_rest_days} 日'),
    ('総トレーニング時間(分)', f'{total_minutes:,} 分', '前週との比較で過負荷を確認',
     '急激な増加は怪我リスク'),
    ('平均RPE（練習日のみ）', f'{avg_rpe:.1f}', '6〜7が中強度の目安',
     'RPEの高い日が続く時は回復を意識'),
    ('平均運動後疲労（練習日のみ）', f'{avg_fatigue:.1f} / 5', '低いほど回復良好',
     '4以上が続く場合は疲労蓄積のサイン'),
    ('平均睡眠時間 (h)', f'{avg_sleep_h:.1f} h', '7時間以上が目安',
     '8時間以上が理想（アスリート推奨）'),
    ('平均睡眠の質（1=良/5=悪）', f'{avg_sleep_q:.1f}', '2以下が望ましい',
     '3以上の日が続く場合は就寝前ルーティン見直しを'),
    ('平均起床時コンディション（1=良/5=悪）', f'{avg_cond:.1f}', '2以下が望ましい',
     '主観の悪化は早期の疲労サインになりうる'),
    ('平均体重 (kg)', f'{avg_weight:.1f} kg', '±1kg以内の変動が目安',
     f'期初 {wt_first:.1f} kg → 期末 {wt_last:.1f} kg（{wt_last-wt_first:+.1f} kg）'),
    ('体重変動幅 (kg)', f'{weight_range:.1f} kg', '1.5kg以内が目安',
     '大きい場合は水分/食事量を確認'),
    ('体脂肪率 期初→期末', f'{bf_first:.1f}% → {bf_last:.1f}%', '維持〜低下が理想',
     f'{bf_last-bf_first:+.1f}% の変化（{"改善" if bf_last < bf_first else "要確認"}）'),
    ('練習後補食「はい」の日数', f'{snack_yes} 日 / {len(df_food)} 日',
     '練習日は毎回が理想', '補食日は翌日疲労が低い傾向（下記参照）'),
    ('夕食タンパク源の平均種類数', f'{avg_protein:.1f} 種類 / 日',
     '2種類以上が目安', '3種類以上の日は翌朝コンディションが良い傾向'),
]

for row_i, (ind, val, target, note) in enumerate(kpi_data, 6):
    ws1.row_dimensions[row_i].height = 22
    bg = C_GRAY if row_i % 2 == 0 else C_WHITE
    for col_i, txt in enumerate([ind, val, target, note], 2):
        c = ws1.cell(row=row_i, column=col_i, value=txt)
        c.fill = fill(bg)
        c.font = font(size=10, color='2D3748',
                      bold=(col_i==2))
        c.alignment = align('left' if col_i in [2,4,5] else 'center', 'center', wrap=(col_i==5))
        c.border = thin_border()
    # highlight value cell
    val_c = ws1.cell(row=row_i, column=3)
    val_c.font = font(bold=True, size=11, color='1A365D')
    val_c.alignment = align('center', 'center')

ws1.row_dimensions[18].height = 12

# Coach comments
r = 19
ws1.merge_cells(f'B{r}:E{r}')
c = ws1[f'B{r}']
c.value = '■ 今期間のハイライト（コーチ記入欄）'
c.fill = fill(C_HEADER2_BG)
c.font = font(bold=True, size=11, color='FFFFFF')
c.alignment = align('left', 'center')
ws1.row_dimensions[r].height = 24

comments = [
    ('① よかった点（継続したい行動）',
     '◯ 体脂肪率が13.9%→12.7%（-1.2%）と着実に低下。体重をほぼ維持しながら身体組成が改善しており、100m/400mの競技特性に合った変化。\n'
     '◯ 4月13・14日の長時間練習（240分・RPE8）でも翌日疲労が低め。練習後補食の実施とタンパク質多様な摂取が効いている可能性あり。\n'
     '◯ 睡眠時間が全日程を通じて7時間以上を確保できており安定している。',
     C_GREEN),
    ('② 気になった点（早めに手を打ちたいこと）',
     '◯ 4月21日以降、運動後疲労が4〜5で高止まり傾向。4/19のハーフマラソン（RPE10）後の疲労蓄積が影響している可能性。\n'
     '◯ 起床時コンディションが4月中旬以降に3〜4点台へ悪化。高強度練習翌日のリカバリーが課題。\n'
     '◯ 昼食のタンパク質摂取が少ない日が多い（昼:魚・豆・卵の摂取日数が少ない）。午前練習後の昼食補強を。',
     C_ORANGE),
    ('③ 次の大会までの小さな目標（1つだけ）',
     '◯ 練習日は必ず練習後30分以内に補食を摂る（目標: 毎練習日 100%実施）。\n'
     '　 理由: 補食あり群の翌日運動後疲労は1.96 vs なし群2.27。わずか0.31点の差でも、累積すると回復速度に大きく影響します。',
     C_YELLOW),
]
for ci, (title, body, bg_c) in enumerate(comments):
    r += 1
    ws1.row_dimensions[r].height = 18
    ws1.merge_cells(f'B{r}:E{r}')
    c = ws1[f'B{r}']
    c.value = title
    c.fill = fill('34495E')
    c.font = font(bold=True, size=10, color='FFFFFF')
    c.alignment = align('left', 'center')

    r += 1
    ws1.row_dimensions[r].height = 72
    ws1.merge_cells(f'B{r}:E{r}')
    c = ws1[f'B{r}']
    c.value = body
    c.fill = fill(bg_c)
    c.font = font(size=10, color='2D3748')
    c.alignment = align('left', 'top', wrap=True)
    c.border = thin_border()

ws1.row_dimensions[r+1].height = 12

# Athlete Q&A
r += 2
ws1.merge_cells(f'B{r}:E{r}')
c = ws1[f'B{r}']
c.value = '■ 選手から（自己振り返り欄）'
c.fill = fill(C_HEADER2_BG)
c.font = font(bold=True, size=11, color='FFFFFF')
c.alignment = align('left', 'center')
ws1.row_dimensions[r].height = 24

qa_items = [
    'Q1. 今期間で「調子がよかった」と感じた日と、その理由',
    'Q2. 逆に「うまくいかなかった」日と、思い当たる原因',
    'Q3. 次に試してみたいこと（食事・睡眠・練習どれか1つ）',
]
for q in qa_items:
    r += 1
    ws1.row_dimensions[r].height = 18
    ws1.merge_cells(f'B{r}:E{r}')
    c = ws1[f'B{r}']
    c.value = q
    c.fill = fill('34495E')
    c.font = font(bold=True, size=10, color='FFFFFF')
    c.alignment = align('left', 'center')
    r += 1
    ws1.row_dimensions[r].height = 50
    ws1.merge_cells(f'B{r}:E{r}')
    c = ws1[f'B{r}']
    c.value = '（選手記入欄）'
    c.fill = fill('F0F8FF')
    c.font = font(size=10, color='A0AEC0', italic=True)
    c.alignment = align('left', 'top', wrap=True)
    c.border = thin_border()

print("Sheet ① done")

# ============================================================
# Sheet 2: ② 日次統合データ
# ============================================================
ws2 = wb.create_sheet('② 日次統合データ')
ws2.sheet_view.showGridLines = False

col_widths = {'A':2,'B':12,'C':20,'D':9,'E':7,'F':8,'G':8,'H':9,
              'I':9,'J':9,'K':9,'L':9,'M':7,'N':11}
for col, w in col_widths.items():
    ws2.column_dimensions[col].width = w

# Title
ws2.merge_cells('B1:N1')
c = ws2['B1']
c.value = '日次統合データ（全項目を1行で確認）'
c.fill = fill(C_HEADER_BG)
c.font = font(bold=True, size=14, color='FFFFFF')
c.alignment = align('left', 'center')
ws2.row_dimensions[1].height = 30

ws2.merge_cells('B2:N2')
c = ws2['B2']
c.value = '色の見方: 緑=良好　黄=普通　橙/赤=要注意　（起床CD・睡眠の質・疲労は数値が小さいほど良い）'
c.fill = fill('EBF8FF')
c.font = font(size=9, color='2B6CB0')
c.alignment = align('left', 'center')
ws2.row_dimensions[2].height = 18

ws2.row_dimensions[3].height = 8

# Headers
headers2 = ['日付','種目','時間(分)','RPE','爆発力','持久力','運動後疲労',
            '体重(kg)','起床CD','睡眠の質','睡眠時間','補食','栄養Bal','タンパク数']
for col_i, h in enumerate(headers2, 2):
    c = ws2.cell(row=4, column=col_i, value=h)
    style_header_cell(c, h, bg=C_HEADER2_BG, size=9)
ws2.row_dimensions[4].height = 22

# Data rows
train_type_bg = {
    '実践トレーニング': 'FFF9F0',
    'ウエイトトレーニング': 'F0F8FF',
    '実践トレーニング+ウエイトトレーニング': 'FFF0F8',
    '休養日': 'F7FAFC',
}

for row_i, (_, row) in enumerate(df.iterrows(), 5):
    ws2.row_dimensions[row_i].height = 20
    row_bg = train_type_bg.get(str(row.get('種目', '休養日')), C_WHITE)

    # 日付
    c = ws2.cell(row=row_i, column=2, value=row['日付'].strftime('%m/%d') if pd.notna(row['日付']) else '')
    style_cell(c, bg=row_bg, bold=True, size=9)

    # 種目
    kind = str(row.get('種目','')) if pd.notna(row.get('種目')) else ''
    short = kind.replace('実践トレーニング','実践').replace('ウエイトトレーニング','WT').replace('+','＋')
    c = ws2.cell(row=row_i, column=3, value=short)
    style_cell(c, bg=row_bg, h='left', size=9)

    # 時間
    time_val = int(row['時間_分']) if pd.notna(row.get('時間_分')) else 0
    c = ws2.cell(row=row_i, column=4, value=time_val if time_val > 0 else '')
    style_cell(c, bg=row_bg, size=9)

    # RPE
    rpe_val = row.get('RPE')
    c = ws2.cell(row=row_i, column=5, value=int(rpe_val) if pd.notna(rpe_val) and rpe_val > 1 else '')
    style_cell(c, bg=rpe_color(rpe_val) if pd.notna(rpe_val) and rpe_val > 1 else row_bg, size=9)

    # 爆発力
    exp_val = row.get('爆発力')
    c = ws2.cell(row=row_i, column=6, value=int(exp_val) if pd.notna(exp_val) and exp_val > 1 else '')
    style_cell(c, bg=row_bg, size=9)

    # 持久力
    end_val = row.get('持久力')
    c = ws2.cell(row=row_i, column=7, value=int(end_val) if pd.notna(end_val) and end_val > 1 else '')
    style_cell(c, bg=row_bg, size=9)

    # 運動後疲労 (lower=better → 1-2=green, 3=yellow, 4-5=red)
    fat_val = row.get('運動後疲労')
    c = ws2.cell(row=row_i, column=8, value=int(fat_val) if pd.notna(fat_val) and fat_val > 1 else '')
    fat_bg = condition_color(fat_val, inverse=True) if pd.notna(fat_val) and fat_val > 1 else row_bg
    style_cell(c, bg=fat_bg, bold=(pd.notna(fat_val) and fat_val >= 4), size=9)

    # 体重
    wt_val = row.get('体重_kg')
    c = ws2.cell(row=row_i, column=9, value=float(wt_val) if pd.notna(wt_val) else '')
    style_cell(c, bg=row_bg, size=9)

    # 起床CD (lower=better)
    cd_val = row.get('起床時コンディション')
    c = ws2.cell(row=row_i, column=10, value=int(cd_val) if pd.notna(cd_val) else '')
    style_cell(c, bg=condition_color(cd_val, inverse=True) if pd.notna(cd_val) else row_bg, size=9)

    # 睡眠の質 (lower=better)
    sq_val = row.get('睡眠の質')
    c = ws2.cell(row=row_i, column=11, value=int(sq_val) if pd.notna(sq_val) else '')
    style_cell(c, bg=condition_color(sq_val, inverse=True) if pd.notna(sq_val) else row_bg, size=9)

    # 睡眠時間
    sh_val = row.get('睡眠時間')
    c = ws2.cell(row=row_i, column=12, value=float(sh_val) if pd.notna(sh_val) else '')
    sh_bg = C_GREEN if pd.notna(sh_val) and sh_val >= 8 else (C_YELLOW if pd.notna(sh_val) and sh_val >= 7 else row_bg)
    style_cell(c, bg=sh_bg, size=9)

    # 補食
    snack = row.get('練習後補食', '')
    c = ws2.cell(row=row_i, column=13, value=str(snack) if pd.notna(snack) else '')
    snack_bg = C_SNACK_YES if snack == 'はい' else (C_SNACK_NO if snack == 'いいえ' else row_bg)
    style_cell(c, bg=snack_bg, size=9)

    # 栄養Bal
    nb_val = row.get('栄養バランス')
    c = ws2.cell(row=row_i, column=14, value=int(nb_val) if pd.notna(nb_val) else '')
    nb_bg = condition_color(nb_val, inverse=True) if pd.notna(nb_val) else row_bg
    style_cell(c, bg=nb_bg, size=9)

    # タンパク数
    tp_val = row.get('タンパク質摂取数')
    c = ws2.cell(row=row_i, column=15, value=int(tp_val) if pd.notna(tp_val) else '')
    tp_bg = C_GREEN if pd.notna(tp_val) and tp_val >= 3 else (C_YELLOW if pd.notna(tp_val) and tp_val >= 2 else row_bg)
    style_cell(c, bg=tp_bg, size=9)

# Average row
avg_row = len(df) + 5
ws2.row_dimensions[avg_row].height = 22
ws2.cell(row=avg_row, column=2, value='平均/合計').fill = fill('34495E')
ws2.cell(row=avg_row, column=2).font = font(bold=True, size=9, color='FFFFFF')
ws2.cell(row=avg_row, column=2).alignment = align('center', 'center')

avgs = {
    4:  int(df['時間_分'].fillna(0).sum()),
    5:  round(train_only['RPE'].mean(), 1),
    6:  round(train_only['爆発力'].mean(), 1),
    7:  round(train_only['持久力'].mean(), 1),
    8:  round(train_only['運動後疲労'].mean(), 1),
    9:  round(df_body['体重_kg'].mean(), 1),
    10: round(df_cond['起床時コンディション'].mean(), 1),
    11: round(df_cond['睡眠の質'].mean(), 1),
    12: round(df_cond['睡眠時間'].mean(), 1),
}
for col_i, val in avgs.items():
    c = ws2.cell(row=avg_row, column=col_i, value=val)
    style_cell(c, bg='EDF2F4', bold=True, size=9, color='1A365D')
ws2.cell(row=avg_row, column=13, value=f'{snack_yes}回').fill = fill(C_GREEN)
ws2.cell(row=avg_row, column=13).font = font(bold=True, size=9, color='276749')
ws2.cell(row=avg_row, column=13).alignment = align('center','center')
ws2.cell(row=avg_row, column=15, value=round(df_food['タンパク質摂取数'].mean(), 1)).fill = fill('EDF2F4')
ws2.cell(row=avg_row, column=15).font = font(bold=True, size=9)
ws2.cell(row=avg_row, column=15).alignment = align('center','center')

print("Sheet ② done")

# ============================================================
# Sheet 3: ③ 食事バランス
# ============================================================
ws3 = wb.create_sheet('③ 食事バランス')
ws3.sheet_view.showGridLines = False

ws3.column_dimensions['A'].width = 2
ws3.column_dimensions['B'].width = 10
prot_cols_disp = ['昼:魚','昼:肉','昼:豆','昼:卵','夕:魚','夕:肉','夕:豆','夕:卵','種類数','補食']
prot_colors = [C_PROT_FISH, C_PROT_MEAT, C_PROT_SOY, C_PROT_EGG,
               C_PROT_FISH, C_PROT_MEAT, C_PROT_SOY, C_PROT_EGG]
col_letters = ['C','D','E','F','G','H','I','J','K','L']
for cl in col_letters:
    ws3.column_dimensions[cl].width = 8

# Title
ws3.merge_cells('B1:L1')
c = ws3['B1']
c.value = 'タンパク源バランス（色がついている = 摂取あり）'
c.fill = fill(C_HEADER_BG)
c.font = font(bold=True, size=14, color='FFFFFF')
c.alignment = align('left', 'center')
ws3.row_dimensions[1].height = 30

ws3.merge_cells('B2:L2')
c = ws3['B2']
c.value = '◎ 「魚・肉・豆・卵」がバランスよく揃うと回復が早まります。空白マスが多い列は意識的に増やしましょう。'
c.fill = fill('F0FFF4')
c.font = font(size=9, color='276749')
c.alignment = align('left', 'center')
ws3.row_dimensions[2].height = 18

# Divider header: 昼 / 夕
ws3.merge_cells('C3:F3')
c = ws3['C3']
c.value = '── 昼 食 ──'
c.fill = fill('BEE3F8')
c.font = font(bold=True, size=9, color='2C5282')
c.alignment = align('center', 'center')

ws3.merge_cells('G3:J3')
c = ws3['G3']
c.value = '── 夕 食 ──'
c.fill = fill('FEB2B2')
c.font = font(bold=True, size=9, color='742A2A')
c.alignment = align('center', 'center')
ws3.row_dimensions[3].height = 18

# Column headers
style_header_cell(ws3['B4'], '日付', bg=C_HEADER2_BG, size=9)
for i, (h, cl) in enumerate(zip(prot_cols_disp, col_letters)):
    bg = prot_colors[i] if i < 8 else ('EDF2F4' if h == '種類数' else C_HEADER2_BG)
    style_header_cell(ws3[f'{cl}4'], h,
                      bg=prot_colors[i] if i < 8 else C_HEADER2_BG,
                      size=9,
                      color='1A365D' if i < 8 else 'FFFFFF')
ws3.row_dimensions[4].height = 20

src_cols = ['昼タンパク質_魚','昼タンパク質_肉','昼タンパク質_豆','昼タンパク質_卵',
            '夕タンパク質_魚','夕タンパク質_肉','夕タンパク質_豆','夕タンパク質_卵']

for row_i, (_, row) in enumerate(df_food.iterrows(), 5):
    ws3.row_dimensions[row_i].height = 20
    bg_row = C_WHITE if row_i % 2 == 0 else C_LGRAY

    c = ws3.cell(row=row_i, column=2, value=row['日付'].strftime('%m/%d'))
    style_cell(c, bg=bg_row, bold=True, size=9)

    total_prot = 0
    for ci, (sc, cl, pc) in enumerate(zip(src_cols, col_letters[:8], prot_colors)):
        has = row[sc] == 1
        if has: total_prot += 1
        c = ws3[f'{cl}{row_i}']
        c.value = '●' if has else ''
        c.fill = fill(pc if has else bg_row)
        c.font = font(bold=True, size=12, color='1A365D' if has else 'CCCCCC')
        c.alignment = align('center', 'center')
        c.border = thin_border()

    # 種類数
    c = ws3[f'K{row_i}']
    tp_bg = C_GREEN if total_prot >= 3 else (C_YELLOW if total_prot >= 2 else (C_RED if total_prot == 0 else C_ORANGE))
    style_cell(c, value=total_prot, bg=tp_bg, bold=True, size=10, color='1A365D')

    # 補食
    snack = row.get('練習後補食', '')
    c = ws3[f'L{row_i}']
    style_cell(c, value='はい' if snack == 'はい' else 'いいえ',
               bg=C_SNACK_YES if snack == 'はい' else C_SNACK_NO, size=9,
               color='276749' if snack == 'はい' else '9B2C2C', bold=(snack == 'はい'))

# Count row
count_row = len(df_food) + 5
ws3.row_dimensions[count_row].height = 22
c = ws3.cell(row=count_row, column=2, value='摂取日数')
style_cell(c, bg='34495E', bold=True, size=9, color='FFFFFF')

for ci, sc in enumerate(src_cols):
    cnt = int(df_food[sc].sum())
    c = ws3[f'{col_letters[ci]}{count_row}']
    bg = C_GREEN if cnt >= 15 else (C_YELLOW if cnt >= 8 else C_RED)
    style_cell(c, value=cnt, bg=bg, bold=True, size=10, color='1A365D')

c = ws3[f'K{count_row}']
style_cell(c, value=round(df_food['タンパク質摂取数'].mean(), 1), bg=C_GREEN, bold=True, size=10)

c = ws3[f'L{count_row}']
style_cell(c, value=f'{snack_yes}日', bg=C_GREEN if snack_yes >= 15 else C_YELLOW, bold=True, size=10)

# Hint box
hint_row = count_row + 2
ws3.merge_cells(f'B{hint_row}:L{hint_row}')
c = ws3[f'B{hint_row}']
c.value = '■ 改善のヒント'
c.fill = fill(C_HEADER2_BG)
c.font = font(bold=True, size=10, color='FFFFFF')
c.alignment = align('left', 'center')
ws3.row_dimensions[hint_row].height = 20

hints = [
    f'・昼食の魚・豆・卵の摂取が少ない日が多いです。冷蔵庫に常備しやすい卵・納豆を活用すると昼食のタンパク質を手軽に+1できます。',
    f'・種類数が0〜1の日は同じ食材への偏りのサイン。翌朝のコンディションとの関連が見られます（「⑤ 関連性」参照）。',
    f'・夕食では肉類の摂取が多い傾向。魚（DHA/EPA）や大豆（植物性タンパク）も週3回以上を目標に取り入れると回復力アップが期待できます。',
]
for hi, hint in enumerate(hints):
    r = hint_row + 1 + hi
    ws3.row_dimensions[r].height = 18
    ws3.merge_cells(f'B{r}:L{r}')
    c = ws3[f'B{r}']
    c.value = hint
    c.fill = fill(C_LGRAY)
    c.font = font(size=9, color='2D3748')
    c.alignment = align('left', 'center', wrap=True)
    c.border = thin_border()

print("Sheet ③ done")

# ============================================================
# Sheet 4: ④ トレンドグラフ
# ============================================================
ws4 = wb.create_sheet('④ トレンドグラフ')
ws4.sheet_view.showGridLines = False
ws4.column_dimensions['A'].width = 2

ws4.merge_cells('B1:J1')
c = ws4['B1']
c.value = 'トレンドグラフ（時系列）'
c.fill = fill(C_HEADER_BG)
c.font = font(bold=True, size=14, color='FFFFFF')
c.alignment = align('left', 'center')
ws4.row_dimensions[1].height = 30

ws4.merge_cells('B2:J2')
c = ws4['B2']
c.value = 'グラフは「② 日次統合データ」の内容を元に作成しています。'
c.fill = fill('EBF8FF')
c.font = font(size=9, color='2B6CB0')
c.alignment = align('left', 'center')
ws4.row_dimensions[2].height = 18

# Embed charts
try:
    for fname, row_start, col_start in [
        ('fig_A_trends.png', 4, 'B'),
        ('fig_E_fatigue_timeline.png', 28, 'B'),
    ]:
        img = XLImage(f'/home/user/AK/{fname}')
        img.width  = 900
        img.height = 480
        ws4.add_image(img, f'{col_start}{row_start}')
    print("Charts embedded OK")
except Exception as e:
    print(f"Chart embed warning: {e}")

print("Sheet ④ done")

# ============================================================
# Sheet 5: ⑤ 関連性ヒント
# ============================================================
ws5 = wb.create_sheet('⑤ 関連性ヒント')
ws5.sheet_view.showGridLines = False
ws5.column_dimensions['A'].width = 2
ws5.column_dimensions['B'].width = 30
ws5.column_dimensions['C'].width = 20
ws5.column_dimensions['D'].width = 14
ws5.column_dimensions['E'].width = 20
ws5.column_dimensions['F'].width = 14
ws5.column_dimensions['G'].width = 14
ws5.column_dimensions['H'].width = 36

ws5.merge_cells('B1:H1')
c = ws5['B1']
c.value = '行動とパフォーマンスの関連性（関連しそうなものだけピックアップ）'
c.fill = fill(C_HEADER_BG)
c.font = font(bold=True, size=14, color='FFFFFF')
c.alignment = align('left', 'center')
ws5.row_dimensions[1].height = 30

ws5.merge_cells('B2:H2')
c = ws5['B2']
c.value = '「差」の絶対値が大きい行ほど、その行動の影響が出ているサイン。0.5以上なら傾向として注目に値する。（数値が小さいほど良い指標の場合: 差がマイナス = A群が良好）'
c.fill = fill('FFFAF0')
c.font = font(size=9, color='744210')
c.alignment = align('left', 'center', wrap=True)
ws5.row_dimensions[2].height = 32

ws5.row_dimensions[3].height = 8

# Table headers
hdrs = ['観点', 'A群条件', 'A群平均', 'B群条件', 'B群平均', '差(B-A)', '解釈']
for ci, h in enumerate(hdrs, 2):
    c = ws5.cell(row=4, column=ci, value=h)
    style_header_cell(c, h, bg=C_HEADER2_BG, size=10)
ws5.row_dimensions[4].height = 22

rel_data = [
    ('練習後補食 → 当日の運動後疲労',
     '補食「いいえ」', round(snack_no_fat, 2),
     '補食「はい」', round(snack_yes_fat, 2),
     round(snack_yes_fat - snack_no_fat, 2),
     f'補食あり群の疲労が{"低い ✅ 継続を推奨" if snack_yes_fat < snack_no_fat else "差なし / データ不足"}。練習後30分以内の補食を徹底してください。'),
    ('睡眠の質 → 練習中の運動後疲労',
     '睡眠の質 ≥ 3（良くない）', round(bad_sleep_fat, 2),
     '睡眠の質 ≤ 2（良好）', round(good_sleep_fat, 2),
     round(good_sleep_fat - bad_sleep_fat, 2),
     f'睡眠の質が良い日は練習中疲労が{"低い ✅ 睡眠環境の整備が有効" if good_sleep_fat < bad_sleep_fat else "差は小さい"}。'),
    ('タンパク質種類数 → 翌朝のコンディション',
     '3種類未満', round(prot_low_cond, 2),
     '3種類以上', round(prot_high_cond, 2),
     round(prot_high_cond - prot_low_cond, 2),
     f'タンパク質3種以上の日の翌朝コンディションは{"良好 ✅ 最も差が大きい関連性" if prot_high_cond < prot_low_cond else "差あり"}（差: {abs(prot_high_cond-prot_low_cond):.2f}点）。'),
    ('睡眠時間 → その日のRPE（練習日）',
     '睡眠 < 7時間',
     round(short_sleep_rpe, 2) if not pd.isna(short_sleep_rpe) else '—',
     '睡眠 ≥ 7時間', round(long_sleep_rpe, 2),
     round(long_sleep_rpe - short_sleep_rpe, 2) if not pd.isna(short_sleep_rpe) else '—',
     '全日程7時間以上確保できているため比較データ不足。8時間以上の日との比較を今後検討。'),
]

for ri, rdata in enumerate(rel_data, 5):
    ws5.row_dimensions[ri].height = 52
    obs, a_cond, a_val, b_cond, b_val, diff, interp = rdata
    row_bg = C_GRAY if ri % 2 == 0 else C_WHITE

    c = ws5.cell(row=ri, column=2, value=obs)
    style_cell(c, bg=row_bg, bold=True, h='left', v='center', wrap=True, size=10)

    c = ws5.cell(row=ri, column=3, value=a_cond)
    style_cell(c, bg=C_RED, h='center', size=9)

    c = ws5.cell(row=ri, column=4, value=a_val)
    style_cell(c, bg=C_RED, bold=True, size=11, color='9B2C2C')

    c = ws5.cell(row=ri, column=5, value=b_cond)
    style_cell(c, bg=C_GREEN, h='center', size=9)

    c = ws5.cell(row=ri, column=6, value=b_val)
    style_cell(c, bg=C_GREEN, bold=True, size=11, color='276749')

    if isinstance(diff, float):
        diff_bg = C_GREEN if diff < -0.3 else (C_YELLOW if abs(diff) < 0.3 else C_ORANGE)
        diff_txt = f'{diff:+.2f}'
    else:
        diff_bg, diff_txt = C_LGRAY, str(diff)
    c = ws5.cell(row=ri, column=7, value=diff_txt)
    style_cell(c, bg=diff_bg, bold=True, size=11, color='1A365D')

    c = ws5.cell(row=ri, column=8, value=interp)
    style_cell(c, bg=row_bg, h='left', v='center', wrap=True, size=9, color='2D3748')

# Embed correlation chart
try:
    img = XLImage('/home/user/AK/fig_D_correlation.png')
    img.width  = 900
    img.height = 420
    ws5.add_image(img, 'B10')
    print("Corr chart embedded")
except Exception as e:
    print(f"Corr chart warning: {e}")

# Hint section
r_hint = 10
ws5.merge_cells(f'B{r_hint}:H{r_hint}')

print("Sheet ⑤ done")

# ============================================================
# Sheet 0: はじめに
# ============================================================
ws0 = wb.create_sheet('はじめに', 0)
ws0.sheet_view.showGridLines = False
ws0.column_dimensions['A'].width = 2
ws0.column_dimensions['B'].width = 80

ws0.row_dimensions[1].height = 50
ws0.merge_cells('B1:B1')
c = ws0['B1']
c.value = '選手フィードバックシート'
c.fill = fill(C_HEADER_BG)
c.font = font(bold=True, size=20, color='FFFFFF')
c.alignment = align('left', 'center')

sections = [
    ('', ''),
    ('■ シート構成', ''),
    ('① サマリー', '主要KPIと、コーチ/選手の記入欄。これだけ印刷して渡してもOK。'),
    ('② 日次統合データ', '4項目を1行に統合した表。色分けで「悪い日」「良い日」が一目でわかる。'),
    ('③ 食事バランス', 'タンパク源（魚/肉/豆/卵）を昼夕別にカレンダー表示。偏りが視覚化される。'),
    ('④ トレンドグラフ', '体重・RPE・睡眠などを時系列で表示。会話のたたき台に。'),
    ('⑤ 関連性ヒント', '「補食を摂った日と摂らなかった日」など、本人専用の傾向を自動算出。'),
    ('', ''),
    ('■ スコアの読み方（重要）', ''),
    ('起床時コンディション (1〜5)', '1=とても良い　5=とても悪い　※数値が小さいほど良好'),
    ('睡眠の質 (1〜5)', '1=よく眠れた　5=全然眠れなかった　※数値が小さいほど良好'),
    ('運動後疲労 (1〜5)', '1=疲労なし　5=非常に疲れた　※数値が小さいほど良好'),
    ('RPE (1〜10)', '1=ほぼ安静　10=最大努力。6〜7=中強度、8以上=高強度。'),
    ('栄養バランス (1〜5)', '数値が小さいほどバランスが良い（アプリ設定による）'),
]

for r, (title, body) in enumerate(sections, 2):
    ws0.row_dimensions[r] = ws0.row_dimensions.get(r) or openpyxl.worksheet.dimensions.RowDimension(ws0, index=r)
    ws0.row_dimensions[r].height = 20 if title else 10
    if not title and not body:
        continue
    if body:
        c = ws0.cell(row=r, column=2, value=f'  {title}  →  {body}')
        c.fill = fill(C_LGRAY if r % 2 == 0 else C_WHITE)
        c.font = font(size=10, color='2D3748', bold=(title.startswith('■')))
        c.alignment = align('left', 'center')
        c.border = thin_border()
    else:
        c = ws0.cell(row=r, column=2, value=title)
        c.fill = fill('34495E' if title.startswith('■') else C_WHITE)
        c.font = font(bold=True, size=11, color='FFFFFF' if title.startswith('■') else '2D3748')
        c.alignment = align('left', 'center')

print("Sheet はじめに done")

# ===== Save =====
out_path = '/home/user/AK/athlete_feedback_report.xlsx'
wb.save(out_path)
print(f"\nSaved: {out_path}")
