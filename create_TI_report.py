#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TI選手 フィードバックシート生成スクリプト
"""

import pandas as pd
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import (
    PatternFill, Font, Alignment, Border, Side, numbers
)
from openpyxl.utils import get_column_letter
from openpyxl.styles.numbers import FORMAT_DATE_DATETIME
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 1. データ読み込み
# ============================================================
SRC = '/root/.claude/uploads/476d747b-4301-41ab-8685-3ec73b06cbab/376c8a5f-TI___20260328_20260523.xlsx'
OUT = '/home/user/AK/TI_選手_フィードバックシート_20260523.xlsx'

xl = pd.ExcelFile(SRC)
df_cond  = xl.parse('主観的体調')   # 起床時コンディション, 睡眠の質, 睡眠時間
df_body  = xl.parse('身体データ')   # 体重_kg
df_train = xl.parse('トレーニング') # 種目, 時間_分, RPE, 爆発力, 持久力, 運動後疲労, メモ
df_food  = xl.parse('食事')        # 練習後補食, 栄養バランス, 水分摂取量_ml, きのこ海藻, タンパク質*8, メモ

# 日付を date 型に統一
for df in [df_cond, df_body, df_train, df_food]:
    df['日付'] = pd.to_datetime(df['日付']).dt.date

# ============================================================
# 2. 統計計算
# ============================================================
total_days   = len(df_train)
train_days   = (df_train['種目'] == '実践トレーニング').sum()
rest_days    = (df_train['種目'] == '休養日').sum()
total_min    = df_train.loc[df_train['種目'] == '実践トレーニング', '時間_分'].sum()

tr = df_train[df_train['種目'] == '実践トレーニング'].copy()
avg_rpe      = tr['RPE'].mean()
avg_fatigue  = tr['運動後疲労'].mean()

avg_sleep_h  = df_cond['睡眠時間'].mean()
avg_sleep_q  = df_cond['睡眠の質'].mean()
avg_morning  = df_cond['起床時コンディション'].mean()

bw_valid     = df_body['体重_kg'].dropna()
avg_weight   = bw_valid.mean()
weight_range = bw_valid.max() - bw_valid.min()

avg_fluid    = df_food['水分摂取量_ml'].mean()
fluid_1000   = (df_food['水分摂取量_ml'] >= 1000).sum()
snack_yes    = (df_food['練習後補食'] == 'はい').sum()
mushroom_yes = (df_food['きのこ海藻'] == 'はい').sum()

prot_cols = ['昼タンパク質_魚','昼タンパク質_肉','昼タンパク質_豆','昼タンパク質_卵',
             '夕タンパク質_魚','夕タンパク質_肉','夕タンパク質_豆','夕タンパク質_卵']
lunch_cols = ['昼タンパク質_魚','昼タンパク質_肉','昼タンパク質_豆','昼タンパク質_卵']
dinner_cols= ['夕タンパク質_魚','夕タンパク質_肉','夕タンパク質_豆','夕タンパク質_卵']

def count_circles(row, cols):
    return sum(1 for c in cols if str(row.get(c,'')) == '○')

df_food['prot_total'] = df_food.apply(lambda r: count_circles(r, prot_cols), axis=1)
df_food['prot_lunch'] = df_food.apply(lambda r: count_circles(r, lunch_cols), axis=1)
df_food['prot_dinner']= df_food.apply(lambda r: count_circles(r, dinner_cols), axis=1)

avg_prot_total = df_food['prot_total'].mean()
avg_prot_lunch = df_food['prot_lunch'].mean()
avg_prot_dinner= df_food['prot_dinner'].mean()

print("=" * 50)
print("【TI選手 期間統計】2026-03-30 〜 2026-05-22 (53日間)")
print("=" * 50)
print(f"総日数:              {total_days} 日")
print(f"トレーニング日数:    {train_days} 日")
print(f"休養日数:            {rest_days} 日")
print(f"総トレーニング時間:  {total_min} 分")
print(f"平均RPE(練習日):     {avg_rpe:.3f}")
print(f"平均運動後疲労:      {avg_fatigue:.3f}")
print(f"平均睡眠時間:        {avg_sleep_h:.3f} h")
print(f"平均睡眠の質:        {avg_sleep_q:.3f}")
print(f"平均起床時CD:        {avg_morning:.3f}")
print(f"平均体重:            {avg_weight:.3f} kg")
print(f"体重変動幅:          {weight_range:.3f} kg")
print(f"平均水分摂取量:      {avg_fluid:.3f} ml")
print(f"水分1000ml以上の日:  {fluid_1000} 日")
print(f"練習後補食「はい」:  {snack_yes} 日")
print(f"きのこ海藻「はい」:  {mushroom_yes} 日")
print(f"タンパク質平均種類(昼夕計): {avg_prot_total:.3f}")
print(f"タンパク質平均種類(昼):     {avg_prot_lunch:.3f}")
print(f"タンパク質平均種類(夕):     {avg_prot_dinner:.3f}")

# ============================================================
# 3. 関連性ヒント計算
# ============================================================
# 結合データフレームを作成
df_all = df_train.merge(df_food, on='日付', how='left') \
                 .merge(df_cond, on='日付', how='left') \
                 .merge(df_body, on='日付', how='left')
df_all_sorted = df_all.sort_values('日付').reset_index(drop=True)

# (A) 練習後補食 → 翌日の運動後疲労
df_tr_only = df_all_sorted[df_all_sorted['種目'] == '実践トレーニング'].copy()
df_tr_only['翌日疲労'] = df_tr_only['運動後疲労'].shift(-1)
# 翌日が練習日のみ
df_tr_only2 = df_tr_only.iloc[:-1]  # 最終行除外

snack_no_next  = df_tr_only2.loc[df_tr_only2['練習後補食'] == 'いいえ', '翌日疲労'].mean()
snack_yes_next = df_tr_only2.loc[df_tr_only2['練習後補食'] == 'はい',  '翌日疲労'].mean()

# (B) 睡眠時間 vs RPE(練習日)
sleep_lt7  = df_tr_only.loc[df_tr_only['睡眠時間'] < 7,  'RPE'].mean()
sleep_ge7  = df_tr_only.loc[df_tr_only['睡眠時間'] >= 7, 'RPE'].mean()

# (C) 睡眠の質 vs 運動後疲労(練習日)
sq_bad  = df_tr_only.loc[df_tr_only['睡眠の質'] >= 3, '運動後疲労'].mean()
sq_good = df_tr_only.loc[df_tr_only['睡眠の質'] <= 2, '運動後疲労'].mean()

# (D) 水分量 vs 運動後疲労(練習日)
fluid_lt  = df_tr_only.loc[df_tr_only['水分摂取量_ml'] < 1000, '運動後疲労'].mean()
fluid_ge  = df_tr_only.loc[df_tr_only['水分摂取量_ml'] >= 1000,'運動後疲労'].mean()

# (E) タンパク質種類 → 翌日RPE
df_food_sorted = df_food.sort_values('日付').reset_index(drop=True)
df_food_sorted['next_date'] = df_food_sorted['日付'].shift(-1)

# merge next day RPE
df_tr_date = df_tr_only[['日付','RPE']].rename(columns={'日付':'next_date','RPE':'next_RPE'})
df_food_next = df_food_sorted.merge(df_tr_date, on='next_date', how='left')
df_food_next = df_food_next.dropna(subset=['next_RPE'])

prot_low_rpe  = df_food_next.loc[df_food_next['prot_total'] <= 2, 'next_RPE'].mean()
prot_high_rpe = df_food_next.loc[df_food_next['prot_total'] >= 3, 'next_RPE'].mean()

print("\n【関連性ヒント】")
print(f"補食いいえ→翌日疲労: {snack_no_next:.3f}  補食はい→翌日疲労: {snack_yes_next:.3f}  差: {snack_yes_next - snack_no_next:.3f}")
print(f"睡眠<7h RPE: {sleep_lt7:.3f}  睡眠≥7h RPE: {sleep_ge7:.3f}  差: {sleep_ge7 - sleep_lt7:.3f}")
print(f"睡眠の質≥3 疲労: {sq_bad:.3f}  睡眠の質≤2 疲労: {sq_good:.3f}  差: {sq_good - sq_bad:.3f}")
print(f"水分<1000 疲労: {fluid_lt:.3f}  水分≥1000 疲労: {fluid_ge:.3f}  差: {fluid_ge - fluid_lt:.3f}")
print(f"タンパク1〜2種 翌日RPE: {prot_low_rpe:.3f}  3種以上 翌日RPE: {prot_high_rpe:.3f}  差: {prot_high_rpe - prot_low_rpe:.3f}")

# ============================================================
# 4. Excelファイル作成
# ============================================================
wb = Workbook()
wb.remove(wb.active)  # default sheet削除

# カラー定義
C_HEADER_BG  = "1F4E79"   # 濃紺
C_HEADER_FG  = "FFFFFF"
C_SECTION_BG = "D6E4F0"   # 薄青
C_GREEN_BG   = "E2EFDA"   # 薄緑
C_ORANGE_BG  = "FCE4D6"   # 薄橙
C_RED_BG     = "FFD7D7"   # 薄赤
C_YELLOW_BG  = "FFF2CC"   # 薄黄
C_GRAY_BG    = "F2F2F2"   # 薄グレー
C_WHITE      = "FFFFFF"
C_TITLE_BG   = "2E75B6"   # 中青

def fill(hex_color):
    return PatternFill(fill_type="solid", fgColor=hex_color)

def font(bold=False, size=11, color="000000", italic=False):
    return Font(bold=bold, size=size, color=color, italic=italic)

def align(h='left', v='center', wrap=False):
    return Alignment(horizontal=h, vertical=v, wrap_text=wrap)

def border_thin():
    s = Side(style='thin', color='AAAAAA')
    return Border(left=s, right=s, top=s, bottom=s)

def border_medium():
    s = Side(style='medium', color='555555')
    return Border(left=s, right=s, top=s, bottom=s)

def set_cell(ws, row, col, value, fnt=None, aln=None, brd=None, fll=None):
    c = ws.cell(row=row, column=col, value=value)
    if fnt: c.font = fnt
    if aln: c.alignment = aln
    if brd: c.border = brd
    if fll: c.fill = fll
    return c

def merge_and_set(ws, row1, col1, row2, col2, value, fnt=None, aln=None, brd=None, fll=None):
    ws.merge_cells(start_row=row1, start_column=col1, end_row=row2, end_column=col2)
    c = ws.cell(row=row1, column=col1, value=value)
    if fnt: c.font = fnt
    if aln: c.alignment = aln
    if brd: c.border = brd
    if fll: c.fill = fll
    return c

# ============================================================
# Sheet 1: はじめに
# ============================================================
ws1 = wb.create_sheet('はじめに')
ws1.column_dimensions['A'].width = 4
ws1.column_dimensions['B'].width = 80

intro_rows = [
    (1, ''),
    (2, '選手フィードバックシート テンプレート'),
    (3, ''),
    (4, '■ シート構成'),
    (5, '① サマリー       … 主要KPIと、コーチ/選手の記入欄。これだけ印刷して渡してもOK。'),
    (6, '② 日次統合データ … 4項目を1行に統合した表。色分けで「悪い日」「良い日」が一目でわかる。'),
    (7, '③ 食事バランス   … タンパク源(魚/肉/豆/卵)を昼夕別にカレンダー表示。偏りが視覚化される。'),
    (8, '④ トレンドグラフ … 体重・RPE・睡眠などを時系列で表示。会話のたたき台に。'),
    (9, '⑤ 関連性ヒント   … 「補食を摂った日と摂らなかった日」など、本人専用の傾向を自動算出。'),
    (10, 'データ_xxxx      … アプリから出力した元データ。ここを貼り替えれば全体が更新される。'),
    (11, ''),
    (12, '■ 使い方(更新手順)'),
    (13, '1. アプリから新しい期間のCSV/Excelを書き出す。'),
    (14, '2. 各「データ_xxxx」シートのデータ部分を新しい期間のデータに貼り替える(ヘッダー行は残す)。'),
    (15, '3. ① サマリー の「対象期間」「レポート作成日」を更新する。'),
    (16, '4. ① サマリー と ⑤ 関連性ヒント を見ながら、コーチ記入欄にコメントを入れる。'),
    (17, '5. 選手と一緒に「② 日次統合データ」「③ 食事バランス」を眺めて対話する。'),
    (18, ''),
    (19, '■ フィードバック設計の考え方'),
    (20, '・「データを見せる」のではなく「気づきと次の1アクション」につなげる。'),
    (21, '・指摘より、よかった日(緑)を起点に「何が違ったか」を本人と一緒に発見する。'),
    (22, '・改善提案は1期間につき1つだけ。複数同時はまず続かない。'),
    (23, '・週次で確認し、月次で振り返るリズムが続けやすい。'),
    (24, ''),
    (25, '■ スコアの読み方(参考)'),
    (26, '・RPE(1〜10): 主観的運動強度。6〜7=中強度、8以上=高強度。'),
    (27, '・運動後疲労(1〜5): 5に近いほど疲労が強い。'),
    (28, '・睡眠の質・起床時コンディション: 数値が小さいほど良好(本データでの傾向)。'),
    (29, '・栄養バランス: 入力規則に依存。アプリ仕様に合わせて読み替え。'),
]

for row_num, text in intro_rows:
    c = ws1.cell(row=row_num, column=2, value=text)
    if text.startswith('■'):
        c.font = Font(bold=True, size=11, color=C_HEADER_BG)
    elif text == '選手フィードバックシート テンプレート':
        c.font = Font(bold=True, size=14, color=C_TITLE_BG)
    else:
        c.font = Font(size=10)
    c.alignment = Alignment(vertical='center')
    ws1.row_dimensions[row_num].height = 18

ws1.sheet_view.showGridLines = False

# ============================================================
# Sheet 2: ① サマリー
# ============================================================
ws2 = wb.create_sheet('① サマリー')
ws2.sheet_view.showGridLines = False
ws2.column_dimensions['A'].width = 4
ws2.column_dimensions['B'].width = 34
ws2.column_dimensions['C'].width = 18
ws2.column_dimensions['D'].width = 22
ws2.column_dimensions['E'].width = 38
ws2.column_dimensions['F'].width = 16

# Title
ws2.row_dimensions[1].height = 10
ws2.row_dimensions[2].height = 30
merge_and_set(ws2, 2, 2, 2, 6,
    'TI選手 フィードバックレポート',
    fnt=Font(bold=True, size=18, color=C_WHITE),
    aln=align('center'),
    fll=fill(C_TITLE_BG))
ws2.row_dimensions[3].height = 8

# Info row
ws2.row_dimensions[4].height = 22
set_cell(ws2, 4, 2, '選手名', fnt=font(bold=True), aln=align('right'))
set_cell(ws2, 4, 3, 'TI選手', fnt=font(bold=True, size=12), aln=align('left'))
set_cell(ws2, 4, 5, '対象期間', fnt=font(bold=True), aln=align('right'))
set_cell(ws2, 4, 6, '2026/03/30 〜 2026/05/22', fnt=font(), aln=align('left'))
ws2.row_dimensions[5].height = 20
set_cell(ws2, 5, 5, 'レポート作成日', fnt=font(bold=True), aln=align('right'))
set_cell(ws2, 5, 6, '2026/05/23', fnt=font(), aln=align('left'))
ws2.row_dimensions[6].height = 10

# Section header - KPI
ws2.row_dimensions[7].height = 22
merge_and_set(ws2, 7, 2, 7, 6, '■ 期間サマリー',
    fnt=Font(bold=True, size=12, color=C_WHITE),
    aln=align('left'),
    fll=fill(C_HEADER_BG))

# Column headers
ws2.row_dimensions[8].height = 20
headers = ['指標', '今期間', '評価目安', '', '備考', '']
hcols   = [2, 3, 4, 5, 5, 6]
for i, (h, c) in enumerate(zip(headers, hcols)):
    if h:
        cell = ws2.cell(row=8, column=c, value=h)
        cell.font = Font(bold=True, size=10, color=C_WHITE)
        cell.fill = fill("2E75B6")
        cell.alignment = align('center')
        cell.border = border_thin()

ws2.merge_cells(start_row=8, start_column=5, end_row=8, end_column=6)

# KPI データ定義
# (label, value_str, target_str, note, is_good)
# is_good: True=緑, False=橙, None=白
kpi_rows = [
    ('総トレーニング日数(休養除く)',    f'{train_days}日',    '休養日とのバランスを確認',    '',                                               None),
    ('総トレーニング時間(分)',           f'{total_min}分',     '前週との比較で過負荷を確認',  '急激な増加は怪我リスク',                         None),
    ('平均RPE(練習日のみ)',              f'{avg_rpe:.2f}',     '6〜7が中強度の目安',          'RPEの高い日が続く時は、回復についても意識！',     6.0 <= avg_rpe <= 7.5),
    ('平均運動後疲労(練習日のみ)',       f'{avg_fatigue:.2f}', '低いほど回復良好',            '5に近いと疲労蓄積',                              avg_fatigue <= 3.0),
    ('平均睡眠時間(h)',                  f'{avg_sleep_h:.2f}', '7時間以上が目安',             '6〜7時間切る日が続くと注意（「関連性」参照）',   avg_sleep_h >= 7.0),
    ('平均睡眠の質(1=良/5=悪)',          f'{avg_sleep_q:.2f}', '2以下が望ましい',             '高い日は前夜の行動を振り返る（食事、スマホ等）', avg_sleep_q <= 2.5),
    ('平均起床時コンディション(1=良/5=悪)', f'{avg_morning:.2f}','2以下が望ましい',           '主観の悪化は早期の疲労サイン',                   avg_morning <= 2.5),
    ('平均体重(kg)',                     f'{avg_weight:.2f}',  '±1kg以内の変動が目安',       '体重コントロールばっちりです！',                  abs(avg_weight - 61.0) <= 1.0),
    ('体重変動幅(kg)',                   f'{weight_range:.1f}','1.5kg以内が目安',             '大きい場合は水分/食事量確認',                    weight_range <= 1.5),
    ('平均水分摂取量(ml)',               f'{avg_fluid:.0f}',   '1000ml以上が目安',            '適切な量については今後要検討（「関連性」参照）', avg_fluid >= 1000),
    (f'水分1000ml以上の日数',            f'{fluid_1000}日',    '',                            '',                                               None),
    ('練習後補食「はい」の日数',         f'{snack_yes}日',     '練習日は毎回が理想',          '回復速度に関連しうる',                           snack_yes >= train_days * 0.8),
    ('きのこ・海藻「はい」の日数',       f'{mushroom_yes}日',  'ミネラル・食物繊維補給',      '週4日以上を目標',                                None),
    ('タンパク質平均種類数(昼夕合計)',   f'{avg_prot_total:.2f}','1.5以上で多様性◎',          '食材の豊富さを確認',                             avg_prot_total >= 1.5),
    ('昼食タンパク質平均種類数',         f'{avg_prot_lunch:.2f}','1.0以上が目安',             '',                                               avg_prot_lunch >= 1.0),
]

for i, (label, val, target, note, is_good) in enumerate(kpi_rows):
    r = 9 + i
    ws2.row_dimensions[r].height = 20
    # 背景色
    if is_good is True:
        row_fill = fill(C_GREEN_BG)
    elif is_good is False:
        row_fill = fill(C_ORANGE_BG)
    else:
        row_fill = fill(C_WHITE)

    for col in range(2, 7):
        ws2.cell(row=r, column=col).fill = row_fill
        ws2.cell(row=r, column=col).border = border_thin()

    ws2.cell(row=r, column=2, value=label).alignment = align('left')
    ws2.cell(row=r, column=3, value=val).alignment = align('center')
    ws2.cell(row=r, column=3).font = font(bold=True, size=11)
    ws2.cell(row=r, column=4, value=target).alignment = align('center')
    ws2.merge_cells(start_row=r, start_column=5, end_row=r, end_column=6)
    ws2.cell(row=r, column=5, value=note).alignment = align('left', wrap=True)

row_after_kpi = 9 + len(kpi_rows)
ws2.row_dimensions[row_after_kpi].height = 12

# Coach comments section
r = row_after_kpi + 1
ws2.row_dimensions[r].height = 22
merge_and_set(ws2, r, 2, r, 6, '■ 今期間のハイライト（コーチ記入欄）',
    fnt=Font(bold=True, size=12, color=C_WHITE),
    aln=align('left'),
    fll=fill(C_HEADER_BG))

r += 1
ws2.row_dimensions[r].height = 20
set_cell(ws2, r, 2, '① よかった点（継続したい行動）',
    fnt=Font(bold=True, size=10, color=C_TITLE_BG),
    aln=align('left'),
    fll=fill(C_SECTION_BG))
ws2.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)

r += 1
ws2.row_dimensions[r].height = 70
good_text = (
    "◯ 5/10 木南記念400m・5/16 ジャパンパラ当日は「動きが良かった」と記録されており、大会での発揮力が高い点は大きな強み。\n"
    "◯ 4/13・4/14 の長時間練習（各240分）でもメモに「疲労感が少ない」と記録され、補食「はい」・水分1000ml・多種タンパクが揃った日と重なっている。栄養サポートの効果が出ている可能性あり。\n"
    "◯ 5/6 練習中にポカリを飲んで「いつもより疲労感が少なかった」→ 練習中の水分+糖質補給の有効性を自ら気づき始めている。"
)
merge_and_set(ws2, r, 2, r, 6, good_text,
    fnt=Font(size=10),
    aln=Alignment(vertical='top', wrap_text=True),
    fll=fill(C_GREEN_BG))

r += 1
ws2.row_dimensions[r].height = 20
set_cell(ws2, r, 2, '② 気になった点（早めに手を打ちたいこと）',
    fnt=Font(bold=True, size=10, color="C00000"),
    aln=align('left'),
    fll=fill(C_SECTION_BG))
ws2.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)

r += 1
ws2.row_dimensions[r].height = 90
concern_text = (
    "◯ 「カラダが重く動きが悪かったし疲れやすかった」(4/6)・「疲れやすく練習短めになった・湿度高かった」(5/22) など、疲れやすさの訴えが期間後半にかけて増加傾向。\n"
    "◯ 4/19ハーフマラソン後、4/21〜4/26に運動後疲労が4〜5で高止まり。睡眠時間は確保できている一方で、食事面では補食が摂れていない日も散見され、エネルギー補充が不十分だった可能性あり。\n"
    "◯ 4/8の食事メモ「2泊3日の外出だったため偏った・何となく疲れている」→ 遠征・外出時の食環境が課題。コンビニ活用ガイド等の準備を検討されてはいかがでしょうか。\n"
    "◯ 5/19食事メモ「今日の夜は食欲がありませんでした」→ 蓄積疲労や高湿度による食欲低下に注意。暑熱期に向けてエネルギー不足を防ぐ食べ方（スポーツドリンク・おにぎりなど食べやすいもの）を準備しておくと良いかもしれません。"
)
merge_and_set(ws2, r, 2, r, 6, concern_text,
    fnt=Font(size=10),
    aln=Alignment(vertical='top', wrap_text=True),
    fll=fill(C_ORANGE_BG))

r += 1
ws2.row_dimensions[r].height = 20
set_cell(ws2, r, 2, '③ 次の大会までの小さな目標（1つだけ）',
    fnt=Font(bold=True, size=10, color="375623"),
    aln=align('left'),
    fll=fill(C_SECTION_BG))
ws2.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)

r += 1
ws2.row_dimensions[r].height = 40
goal_text = (
    "◯ 練習日は必ず練習後30分以内に補食（おにぎり1個＋牛乳or豆乳）を摂る。暑くなる季節は練習中の水分+糖質補給（ポカリ等）を習慣化する。"
)
merge_and_set(ws2, r, 2, r, 6, goal_text,
    fnt=Font(size=10),
    aln=Alignment(vertical='center', wrap_text=True),
    fll=fill(C_YELLOW_BG))

r += 1
ws2.row_dimensions[r].height = 12

# Self-reflection section
r += 1
ws2.row_dimensions[r].height = 22
merge_and_set(ws2, r, 2, r, 6, '■ 選手から（自己振り返り欄）',
    fnt=Font(bold=True, size=12, color=C_WHITE),
    aln=align('left'),
    fll=fill(C_HEADER_BG))

questions = [
    ('Q1. 今期間で「調子がよかった」と感じた日と、その理由', 50),
    ('Q2. 逆に「うまくいかなかった」日と、思い当たる原因', 50),
    ('Q3. 次に試してみたいこと（食事・睡眠・練習どれか1つ）', 50),
]
for q, h in questions:
    r += 1
    ws2.row_dimensions[r].height = 20
    set_cell(ws2, r, 2, q,
        fnt=Font(bold=True, size=10),
        aln=align('left'),
        fll=fill(C_GRAY_BG))
    ws2.merge_cells(start_row=r, start_column=2, end_row=r, end_column=6)
    r += 1
    ws2.row_dimensions[r].height = h
    merge_and_set(ws2, r, 2, r, 6, '（選手記入欄）',
        fnt=Font(size=10, italic=True, color='888888'),
        aln=Alignment(vertical='top', wrap_text=True),
        fll=fill(C_WHITE))
    for col in range(2, 7):
        ws2.cell(row=r, column=col).border = border_thin()

# ============================================================
# Sheet 3: ② 日次統合データ
# ============================================================
ws3 = wb.create_sheet('② 日次統合データ')
ws3.sheet_view.showGridLines = False

col_widths = [4, 14, 14, 10, 7, 7, 7, 10, 10, 10, 10, 10, 6, 12, 10]
col_letters = 'ABCDEFGHIJKLMNO'
for i, w in enumerate(col_widths):
    ws3.column_dimensions[get_column_letter(i+1)].width = w

ws3.row_dimensions[1].height = 22
merge_and_set(ws3, 1, 1, 1, 15, '日次統合データ（全項目を1行で確認）',
    fnt=Font(bold=True, size=13, color=C_WHITE),
    aln=align('center'),
    fll=fill(C_HEADER_BG))

ws3.row_dimensions[2].height = 8

# Headers row 3
ws3.row_dimensions[3].height = 22
daily_headers = ['日付', '種目', '練習時間(分)', 'RPE', '瞬発力', '持久力', '運動後疲労',
                 '体重(kg)', '起床時CD', '睡眠の質', '睡眠時間(h)', '補食', '栄養Bal', '水分(ml)', 'メモ']
for j, h in enumerate(daily_headers):
    c = ws3.cell(row=3, column=j+1, value=h)
    c.font = Font(bold=True, size=9, color=C_WHITE)
    c.fill = fill("2E75B6")
    c.alignment = align('center')
    c.border = border_thin()

# Build integrated dataset
df_daily = df_train.merge(df_body, on='日付', how='left') \
                   .merge(df_cond, on='日付', how='left') \
                   .merge(df_food[['日付','練習後補食','栄養バランス','水分摂取量_ml','メモ']].rename(columns={'メモ':'食事メモ'}), on='日付', how='left')
df_daily = df_daily.sort_values('日付').reset_index(drop=True)

for i, row in df_daily.iterrows():
    r = i + 4
    ws3.row_dimensions[r].height = 18

    is_rest  = row['種目'] == '休養日'
    fatigue  = row['運動後疲労'] if not is_rest else None
    rpe_val  = row['RPE'] if not is_rest else None

    # Row background
    if is_rest:
        bg = fill(C_GRAY_BG)
    else:
        bg = fill(C_WHITE)

    vals = [
        str(row['日付']),
        row['種目'],
        row['時間_分'] if not is_rest else 0,
        rpe_val,
        row['爆発力'] if not is_rest else None,
        row['持久力'] if not is_rest else None,
        fatigue,
        row['体重_kg'] if pd.notna(row['体重_kg']) else None,
        row['起床時コンディション'] if pd.notna(row['起床時コンディション']) else None,
        row['睡眠の質'] if pd.notna(row['睡眠の質']) else None,
        row['睡眠時間'] if pd.notna(row['睡眠時間']) else None,
        row['練習後補食'] if pd.notna(row['練習後補食']) else None,
        row['栄養バランス'] if pd.notna(row['栄養バランス']) else None,
        row['水分摂取量_ml'] if pd.notna(row['水分摂取量_ml']) else None,
        row['メモ'] if pd.notna(row['メモ']) else '',
    ]

    for j, v in enumerate(vals):
        c = ws3.cell(row=r, column=j+1, value=v)
        c.font = Font(size=9)
        c.alignment = align('center')
        c.border = border_thin()
        c.fill = bg

    # Color coding
    # RPE
    if rpe_val is not None:
        if 6 <= rpe_val <= 7:
            ws3.cell(row=r, column=4).fill = fill(C_GREEN_BG)
        elif rpe_val >= 8:
            ws3.cell(row=r, column=4).fill = fill(C_ORANGE_BG)

    # 運動後疲労
    if fatigue is not None:
        if fatigue <= 3:
            ws3.cell(row=r, column=7).fill = fill(C_GREEN_BG)
        elif fatigue >= 4:
            ws3.cell(row=r, column=7).fill = fill(C_ORANGE_BG)
        if fatigue == 5:
            ws3.cell(row=r, column=7).fill = fill(C_RED_BG)

    # 睡眠時間
    sleep_h = row['睡眠時間'] if pd.notna(row['睡眠時間']) else None
    if sleep_h is not None:
        if sleep_h >= 7:
            ws3.cell(row=r, column=11).fill = fill(C_GREEN_BG)
        else:
            ws3.cell(row=r, column=11).fill = fill(C_ORANGE_BG)

    # 睡眠の質
    sq = row['睡眠の質'] if pd.notna(row['睡眠の質']) else None
    if sq is not None:
        if sq <= 2:
            ws3.cell(row=r, column=10).fill = fill(C_GREEN_BG)
        elif sq >= 4:
            ws3.cell(row=r, column=10).fill = fill(C_ORANGE_BG)

# Summary row
r_sum = len(df_daily) + 4
ws3.row_dimensions[r_sum].height = 20
sum_vals = ['平均/合計', '', total_min,
            round(avg_rpe, 2), '', '', round(avg_fatigue, 2),
            round(avg_weight, 2), round(avg_morning, 2), round(avg_sleep_q, 2), round(avg_sleep_h, 2),
            snack_yes, '', round(avg_fluid, 0), '']
for j, v in enumerate(sum_vals):
    c = ws3.cell(row=r_sum, column=j+1, value=v)
    c.font = Font(bold=True, size=9)
    c.alignment = align('center')
    c.border = border_thin()
    c.fill = fill(C_SECTION_BG)

ws3.cell(row=r_sum+1, column=4, value='1=楽').font = Font(size=8, italic=True, color='888888')
ws3.cell(row=r_sum+1, column=7, value='1=低い').font = Font(size=8, italic=True, color='888888')

# ============================================================
# Sheet 4: ③ 食事バランス
# ============================================================
ws4 = wb.create_sheet('③ 食事バランス')
ws4.sheet_view.showGridLines = False

ws4.column_dimensions['A'].width = 14
for col_l in ['B','C','D','E','F','G','H','I']:
    ws4.column_dimensions[col_l].width = 7
ws4.column_dimensions['J'].width = 12
ws4.column_dimensions['K'].width = 8

ws4.row_dimensions[1].height = 22
merge_and_set(ws4, 1, 1, 1, 11, 'タンパク源バランス（色がついている＝摂取あり）',
    fnt=Font(bold=True, size=13, color=C_WHITE),
    aln=align('center'),
    fll=fill(C_HEADER_BG))

ws4.row_dimensions[2].height = 8

ws4.row_dimensions[3].height = 20
merge_and_set(ws4, 3, 1, 3, 11,
    '◎ 「魚・肉・豆・卵」がバランスよく揃うと回復が早まります。空白マスが多い列は意識的に増やしましょう。',
    fnt=Font(size=10, italic=True, color=C_TITLE_BG),
    aln=align('left', wrap=True))

ws4.row_dimensions[4].height = 8

food_headers = ['日付', '昼:魚', '昼:肉', '昼:豆', '昼:卵', '夕:魚', '夕:肉', '夕:豆', '夕:卵', '種類数(昼+夕)', '補食']
ws4.row_dimensions[5].height = 22
for j, h in enumerate(food_headers):
    c = ws4.cell(row=5, column=j+1, value=h)
    c.font = Font(bold=True, size=9, color=C_WHITE)
    c.fill = fill("2E75B6")
    c.alignment = align('center')
    c.border = border_thin()

df_food_sorted2 = df_food.sort_values('日付').reset_index(drop=True)

prot_col_map = {
    '昼タンパク質_魚': 2, '昼タンパク質_肉': 3, '昼タンパク質_豆': 4, '昼タンパク質_卵': 5,
    '夕タンパク質_魚': 6, '夕タンパク質_肉': 7, '夕タンパク質_豆': 8, '夕タンパク質_卵': 9,
}
prot_key_list = list(prot_col_map.keys())

totals = {k: 0 for k in prot_key_list}

for i, row in df_food_sorted2.iterrows():
    r = i + 6
    ws4.row_dimensions[r].height = 17

    total_prot = row['prot_total']
    snack = row['練習後補食']

    ws4.cell(row=r, column=1, value=str(row['日付'])).alignment = align('center')
    ws4.cell(row=r, column=1).border = border_thin()

    for col_name, col_idx in prot_col_map.items():
        val = row[col_name]
        c = ws4.cell(row=r, column=col_idx)
        if str(val) == '○':
            c.value = '○'
            c.fill = fill("E2EFDA")
            c.font = Font(color="375623", bold=True)
            totals[col_name] += 1
        else:
            c.value = ''
        c.alignment = align('center')
        c.border = border_thin()

    # 種類数
    prot_c = ws4.cell(row=r, column=10, value=total_prot)
    if total_prot >= 3:
        prot_c.fill = fill(C_GREEN_BG)
        prot_c.font = Font(bold=True, color="375623")
    elif total_prot == 0:
        prot_c.fill = fill(C_ORANGE_BG)
    prot_c.alignment = align('center')
    prot_c.border = border_thin()

    snack_c = ws4.cell(row=r, column=11, value=snack)
    if snack == 'はい':
        snack_c.fill = fill(C_GREEN_BG)
        snack_c.font = Font(color="375623")
    snack_c.alignment = align('center')
    snack_c.border = border_thin()

# Totals row
r_total = len(df_food_sorted2) + 6
ws4.row_dimensions[r_total].height = 20
ws4.cell(row=r_total, column=1, value='摂取日数').font = Font(bold=True)
ws4.cell(row=r_total, column=1).alignment = align('center')
ws4.cell(row=r_total, column=1).border = border_thin()
ws4.cell(row=r_total, column=1).fill = fill(C_SECTION_BG)

for col_name, col_idx in prot_col_map.items():
    c = ws4.cell(row=r_total, column=col_idx, value=totals[col_name])
    c.font = Font(bold=True)
    c.alignment = align('center')
    c.border = border_thin()
    c.fill = fill(C_SECTION_BG)

ws4.cell(row=r_total, column=10, value=round(avg_prot_total, 2)).alignment = align('center')
ws4.cell(row=r_total, column=10).fill = fill(C_SECTION_BG)
ws4.cell(row=r_total, column=10).font = Font(bold=True)
ws4.cell(row=r_total, column=10).border = border_thin()
ws4.cell(row=r_total, column=11, value=snack_yes).alignment = align('center')
ws4.cell(row=r_total, column=11).fill = fill(C_SECTION_BG)
ws4.cell(row=r_total, column=11).font = Font(bold=True)
ws4.cell(row=r_total, column=11).border = border_thin()

# Hints
r_hint = r_total + 2
ws4.row_dimensions[r_hint].height = 22
ws4.cell(row=r_hint, column=1, value='■ 改善のヒント').font = Font(bold=True, size=11, color=C_TITLE_BG)
hints = [
    '・最も少ない列（摂取日数が一番低い食材）が今期間の「弱点」。次の期間でその食材を週2回以上を目標に。',
    '・種類数が0〜1の日は「同じものに偏ったサイン」。冷蔵庫に常備しやすい卵・納豆を活用すると簡単に+1できる。',
]
for k, h in enumerate(hints):
    rr = r_hint + 1 + k
    ws4.row_dimensions[rr].height = 20
    merge_and_set(ws4, rr, 1, rr, 11, h, fnt=Font(size=10), aln=align('left', wrap=True))

# ============================================================
# Sheet 5: ④ トレンドグラフ
# ============================================================
ws5 = wb.create_sheet('④ トレンドグラフ')
ws5.sheet_view.showGridLines = False
ws5.column_dimensions['A'].width = 80

ws5.row_dimensions[1].height = 25
set_cell(ws5, 1, 1, 'トレンドグラフ（時系列）',
    fnt=Font(bold=True, size=14, color=C_WHITE),
    aln=align('center'),
    fll=fill(C_HEADER_BG))

notes = [
    '',
    'グラフ元データは「② 日次統合データ」を参照しています。データを更新するとグラフも自動更新されます。',
    '',
    '【推奨グラフ一覧】',
    '① 体重推移（折れ線）：日付 × 体重(kg)',
    '② RPE推移（折れ線）：日付 × RPE（練習日のみ）',
    '③ 運動後疲労推移（折れ線）：日付 × 運動後疲労',
    '④ 睡眠時間推移（棒グラフ）：日付 × 睡眠時間(h)',
    '⑤ 睡眠の質推移（折れ線）：日付 × 睡眠の質',
    '⑥ 水分摂取量推移（棒グラフ）：日付 × 水分摂取量(ml)',
    '',
    '→ ② 日次統合データシートで該当列を選択して「グラフ挿入」でご作成ください。',
]
for k, n in enumerate(notes):
    r = k + 2
    ws5.row_dimensions[r].height = 20
    c = ws5.cell(row=r, column=1, value=n)
    if n.startswith('【'):
        c.font = Font(bold=True, size=10, color=C_TITLE_BG)
    else:
        c.font = Font(size=10)

# ============================================================
# Sheet 6: ⑤ 関連性ヒント
# ============================================================
ws6 = wb.create_sheet('⑤ 関連性ヒント')
ws6.sheet_view.showGridLines = False
ws6.column_dimensions['A'].width = 4
ws6.column_dimensions['B'].width = 36
ws6.column_dimensions['C'].width = 18
ws6.column_dimensions['D'].width = 10
ws6.column_dimensions['E'].width = 14
ws6.column_dimensions['F'].width = 10
ws6.column_dimensions['G'].width = 10

ws6.row_dimensions[1].height = 10
ws6.row_dimensions[2].height = 22
merge_and_set(ws6, 2, 2, 2, 7,
    '行動とパフォーマンスの関連性（関連しそうなものだけピックアップ）',
    fnt=Font(bold=True, size=13, color=C_WHITE),
    aln=align('center'),
    fll=fill(C_HEADER_BG))

ws6.row_dimensions[3].height = 8
ws6.row_dimensions[4].height = 20

hint_headers = ['観点', 'A群条件', 'A群平均', 'B群条件', 'B群平均', '差(B-A)']
for j, h in enumerate(hint_headers):
    c = ws6.cell(row=4, column=j+2, value=h)
    c.font = Font(bold=True, size=10, color=C_WHITE)
    c.fill = fill("2E75B6")
    c.alignment = align('center')
    c.border = border_thin()

# Correlation data
corr_data = [
    ('練習後補食 vs 翌日の運動後疲労',    "補食「いいえ」の翌日", round(snack_no_next, 3),  "補食「はい」の翌日", round(snack_yes_next, 3), round(snack_yes_next - snack_no_next, 3)),
    ('睡眠時間 vs その日のRPE(練習日)',    '睡眠 < 7時間',         round(sleep_lt7, 3),    '睡眠 ≥ 7時間',        round(sleep_ge7, 3),     round(sleep_ge7 - sleep_lt7, 3)),
    ('睡眠の質 vs 運動後疲労(練習日)',     '睡眠の質 ≥ 3(良くない日)', round(sq_bad, 3),   '睡眠の質 ≤ 2',       round(sq_good, 3),       round(sq_good - sq_bad, 3)),
    ('水分量 vs 運動後疲労(練習日)',        '水分 < 1000ml',       round(fluid_lt, 3),     '水分 ≥ 1000ml',       round(fluid_ge, 3),      round(fluid_ge - fluid_lt, 3)),
    ('食材の豊富さ vs 翌日のRPE(練習日)', '1〜2種類',             round(prot_low_rpe, 3), '3種類以上',            round(prot_high_rpe, 3), round(prot_high_rpe - prot_low_rpe, 3)),
]

for i, (obs, a_cond, a_avg, b_cond, b_avg, diff) in enumerate(corr_data):
    r = i + 5
    ws6.row_dimensions[r].height = 22

    diff_bg = C_WHITE
    if abs(diff) >= 0.5:
        diff_bg = C_YELLOW_BG

    row_data = [obs, a_cond, a_avg, b_cond, b_avg, diff]
    for j, v in enumerate(row_data):
        c = ws6.cell(row=r, column=j+2, value=v)
        c.font = Font(size=10)
        c.alignment = align('center')
        c.border = border_thin()
        if j == 5:  # diff column
            c.fill = fill(diff_bg)
            if abs(diff) >= 0.5:
                c.font = Font(bold=True, size=10)

ws6.row_dimensions[r+1].height = 10
ws6.row_dimensions[r+2].height = 22
merge_and_set(ws6, r+2, 2, r+2, 7, '■ 読み方のヒント',
    fnt=Font(bold=True, size=11, color=C_TITLE_BG),
    aln=align('left'))

hint_notes = [
    '・「差」の絶対値が大きい行ほど、その行動の影響が出ているサイン。0.5以上なら傾向として注目に値する。',
    '・練習日のみの平均で比較しています。',
    '・サンプル数が少ない場合は参考程度に留め、継続データ蓄積で精度が上がります。',
]
for k, n in enumerate(hint_notes):
    rr = r + 3 + k
    ws6.row_dimensions[rr].height = 20
    merge_and_set(ws6, rr, 2, rr, 7, n, fnt=Font(size=10), aln=align('left'))

# ============================================================
# Sheet 7-10: 生データシート
# ============================================================
def create_raw_sheet(wb, name, df):
    ws = wb.create_sheet(name)
    ws.sheet_view.showGridLines = False

    # Title
    ws.row_dimensions[1].height = 22
    merge_and_set(ws, 1, 1, 1, len(df.columns),
        name,
        fnt=Font(bold=True, size=12, color=C_WHITE),
        aln=align('center'),
        fll=fill(C_HEADER_BG))

    ws.row_dimensions[2].height = 8

    # Headers
    ws.row_dimensions[3].height = 20
    for j, col in enumerate(df.columns):
        c = ws.cell(row=3, column=j+1, value=col)
        c.font = Font(bold=True, size=10, color=C_WHITE)
        c.fill = fill("2E75B6")
        c.alignment = align('center')
        c.border = border_thin()
        # Auto width
        ws.column_dimensions[get_column_letter(j+1)].width = max(12, len(str(col)) + 4)

    for i, row in df.iterrows():
        r = i + 4
        ws.row_dimensions[r].height = 16
        for j, col in enumerate(df.columns):
            v = row[col]
            if pd.isna(v):
                v = None
            elif col == '日付':
                v = str(v)
            c = ws.cell(row=r, column=j+1, value=v)
            c.font = Font(size=9)
            c.alignment = align('center')
            c.border = border_thin()
            if i % 2 == 0:
                c.fill = fill("F9FBFF")

create_raw_sheet(wb, 'データ_主観的体調', df_cond)
create_raw_sheet(wb, 'データ_身体データ', df_body)
create_raw_sheet(wb, 'データ_トレーニング', df_train)
create_raw_sheet(wb, 'データ_食事', df_food[['日付','練習後補食','栄養バランス','水分摂取量_ml','きのこ海藻',
                                              '昼タンパク質_魚','昼タンパク質_肉','昼タンパク質_豆','昼タンパク質_卵',
                                              '夕タンパク質_魚','夕タンパク質_肉','夕タンパク質_豆','夕タンパク質_卵','メモ']])

# ============================================================
# 保存
# ============================================================
wb.save(OUT)
print(f"\n✅ ファイル保存完了: {OUT}")
import os
size = os.path.getsize(OUT)
print(f"ファイルサイズ: {size:,} bytes ({size/1024:.1f} KB)")
