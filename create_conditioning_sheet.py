"""
create_conditioning_sheet.py
コンディション×食事 自己管理Excelシートを生成する。
シート構成:
  ① 使い方（説明・凡例）
  ② 日次記録（30日分、自動警告つき）
  ③ 週次サマリー（自動集計）
  ④ グラフ（体重×疲労／週負荷×主食）は③に埋め込み
"""
import openpyxl
from openpyxl.styles import (
    PatternFill, Font, Alignment, Border, Side, GradientFill
)
from openpyxl.utils import get_column_letter, column_index_from_string
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule, FormulaRule
from openpyxl.chart import LineChart, BarChart, Reference, Series
from openpyxl.chart.series import SeriesLabel
from openpyxl.chart.layout import Layout
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.styles.numbers import FORMAT_DATE_DATETIME
from datetime import date, timedelta

wb = openpyxl.Workbook()

# ── カラー定数 ────────────────────────────────────────────────
C_HEADER    = "1E3A5F"   # 濃紺
C_SUBHDR    = "2563EB"   # 青
C_GREEN     = "16A34A"   # 緑
C_WHITE     = "FFFFFF"
C_LIGHT_BLU = "DBEAFE"   # 薄青（自動入力列）
C_LIGHT_GRN = "DCFCE7"   # 薄緑
C_LIGHT_YLW = "FEF9C3"   # 薄黄
C_LIGHT_RED = "FEE2E2"   # 薄赤
C_WARN_RED  = "DC2626"   # 警告赤
C_WARN_ORG  = "EA580C"   # 警告橙
C_WARN_YLW  = "CA8A04"   # 警告黄
C_GRAY      = "F1F5F9"   # 薄グレー
C_DARKGRAY  = "64748B"

def fill(hex_code):
    return PatternFill("solid", fgColor=hex_code)

def font(size=10, bold=False, color="1E293B", name="メイリオ"):
    return Font(size=size, bold=bold, color=color, name=name)

def border_thin(color="CBD5E1"):
    s = Side(style="thin", color=color)
    return Border(left=s, right=s, top=s, bottom=s)

def center():
    return Alignment(horizontal="center", vertical="center", wrap_text=True)

def left():
    return Alignment(horizontal="left", vertical="center", wrap_text=True)

def set_col_width(ws, col_letter, width):
    ws.column_dimensions[col_letter].width = width

def set_row_height(ws, row, height):
    ws.row_dimensions[row].height = height

# =========================================================================
# ① 使い方シート
# =========================================================================
ws_how = wb.active
ws_how.title = "使い方"
ws_how.sheet_view.showGridLines = False

# タイトル
ws_how.merge_cells("A1:H1")
ws_how["A1"] = "コンディション × 食事 自己管理シート　使い方"
ws_how["A1"].fill = fill(C_HEADER)
ws_how["A1"].font = font(16, True, C_WHITE)
ws_how["A1"].alignment = center()
ws_how.row_dimensions[1].height = 36

ws_how.merge_cells("A2:H2")
ws_how["A2"] = "このシートの目的：食事・コンディションの記録を通じて、自分の体の傾向を把握し、食事を調整する力を身につける"
ws_how["A2"].fill = fill(C_LIGHT_BLU)
ws_how["A2"].font = font(10, False, C_SUBHDR)
ws_how["A2"].alignment = center()
ws_how.row_dimensions[2].height = 22

# 使い方セクション
sections = [
    ("STEP 1", "毎日記録する項目（「日次記録」シートに入力）", C_SUBHDR, [
        ("体重 (kg)",          "毎朝、起床直後・トイレ後に測定。同じ条件で測ることが大切"),
        ("疲労度 (0〜10)",     "0=全く疲れていない、10=ひどく疲れて動けないほど　で主観評価"),
        ("睡眠時間 (h)",       "前夜の実際の睡眠時間（例：7.5）"),
        ("睡眠の質 (0〜5)",    "0=最悪、5=最高　で主観評価"),
        ("練習時間 (分)",      "その日のトレーニング時間（例：90）"),
        ("RPE (0〜10)",        "運動強度の自覚（0=安静、10=最大強度）"),
        ("練習負荷スコア",     "自動計算：練習時間(分) × RPE　→ 高いほど負荷が大きい"),
        ("主食量 (茶碗換算)",  "ご飯・パン・麺を「茶碗何杯分」に換算（パン1枚≒0.5杯、麺1人前≒1.5杯）"),
        ("水分摂取量 (mL)",    "練習中も含めた1日の合計水分量（目安：練習日は2,500 mL以上）"),
        ("補食・サプリ",       "摂取したものを自由記述（例：プロテイン20g、バナナ1本）"),
    ]),
    ("STEP 2", "週に1回チェックする（「週次サマリー」シートを確認）", C_GREEN, [
        ("体重の変動",         "3日移動平均が2日以上連続で下降→エネルギー不足のサイン。主食を1品追加"),
        ("疲労度と前日の主食", "高疲労（7以上）の日の前日に主食が少なくなかったか確認"),
        ("練習負荷と体重",     "高負荷（スコア700以上）翌日に体重が-1 kg以上→脱水＋グリコーゲン消耗"),
        ("水分不足",           "水分摂取量が2,000 mL未満の日が続いたら意識的に補給量を増やす"),
    ]),
    ("STEP 3", "月に1回グラフを確認する（「週次サマリー」シートのグラフ）", "9333EA", [
        ("グラフ①",           "体重の推移（折れ線）＋疲労度の平均（棒）→エネルギー不足の時期を特定"),
        ("グラフ②",           "週ごとの練習負荷スコア（棒）＋主食量の平均（折れ線）→負荷に炭水化物が追いついているか確認"),
    ]),
]

r = 4
for step_name, step_title, color, items in sections:
    # ステップヘッダー
    ws_how.merge_cells(f"A{r}:H{r}")
    ws_how[f"A{r}"] = f"  {step_name}　{step_title}"
    ws_how[f"A{r}"].fill = fill(color)
    ws_how[f"A{r}"].font = font(11, True, C_WHITE)
    ws_how[f"A{r}"].alignment = left()
    ws_how.row_dimensions[r].height = 24
    r += 1

    # 項目ヘッダー
    for col, txt in [("B", "項目"), ("D", "説明")]:
        ws_how[f"{col}{r}"] = txt
        ws_how[f"{col}{r}"].fill = fill(C_GRAY)
        ws_how[f"{col}{r}"].font = font(9, True, C_DARKGRAY)
        ws_how[f"{col}{r}"].alignment = center()
    ws_how.merge_cells(f"D{r}:H{r}")
    ws_how.row_dimensions[r].height = 18
    r += 1

    for item, desc in items:
        ws_how.merge_cells(f"B{r}:C{r}")
        ws_how[f"B{r}"] = item
        ws_how[f"B{r}"].font = font(10, True)
        ws_how[f"B{r}"].alignment = left()
        ws_how[f"B{r}"].border = border_thin()

        ws_how.merge_cells(f"D{r}:H{r}")
        ws_how[f"D{r}"] = desc
        ws_how[f"D{r}"].font = font(10)
        ws_how[f"D{r}"].alignment = left()
        ws_how[f"D{r}"].border = border_thin()
        ws_how.row_dimensions[r].height = 18
        r += 1
    r += 1

# 警告色の凡例
r += 1
ws_how.merge_cells(f"A{r}:H{r}")
ws_how[f"A{r}"] = "  自動警告の色の意味（「日次記録」シート）"
ws_how[f"A{r}"].fill = fill("475569")
ws_how[f"A{r}"].font = font(11, True, C_WHITE)
ws_how[f"A{r}"].alignment = left()
ws_how.row_dimensions[r].height = 22
r += 1

warn_items = [
    (C_LIGHT_RED, "赤：体重が前日比 −1.0 kg以上低下　→ 脱水の可能性。水分・電解質を補給"),
    (C_LIGHT_YLW, "橙：疲労度が 8 以上　→ 高疲労。前日・当日の炭水化物摂取を確認"),
    ("FFF3CD",    "黄：主食量が 2 茶碗未満　→ 炭水化物不足の可能性"),
    ("E0F2FE",    "水色：水分摂取量が 2,000 mL未満　→ 水分補給の強化が必要"),
]
for bg, desc in warn_items:
    ws_how.merge_cells(f"B{r}:C{r}")
    ws_how[f"B{r}"].fill = fill(bg)
    ws_how[f"B{r}"].border = border_thin()
    ws_how.merge_cells(f"D{r}:H{r}")
    ws_how[f"D{r}"] = desc
    ws_how[f"D{r}"].font = font(10)
    ws_how[f"D{r}"].alignment = left()
    ws_how[f"D{r}"].border = border_thin()
    ws_how.row_dimensions[r].height = 18
    r += 1

for col_letter, width in zip("ABCDEFGH", [3, 16, 6, 12, 12, 12, 12, 12]):
    set_col_width(ws_how, col_letter, width)

# =========================================================================
# ② 日次記録シート
# =========================================================================
ws_d = wb.create_sheet("日次記録")
ws_d.sheet_view.showGridLines = False

# 列定義: (列, ヘッダー行1, ヘッダー行2, 幅, 入力種別, bg_color)
# 入力種別: 'manual'=手入力, 'auto'=自動計算, 'text'=自由記述
COLS = [
    # (letter, line1,            line2,             width, kind,     bg)
    ("A", "日付",             "",                  10,  "manual", C_WHITE),
    ("B", "体重",             "(kg)",              8,   "manual", C_WHITE),
    ("C", "前日比",           "(kg)",              7,   "auto",   C_LIGHT_BLU),
    ("D", "3日移動\n平均",    "(kg)",              8,   "auto",   C_LIGHT_BLU),
    ("E", "疲労度",           "(0〜10)",           7,   "manual", C_WHITE),
    ("F", "睡眠時間",         "(h)",               7,   "manual", C_WHITE),
    ("G", "睡眠の質",         "(0〜5)",            7,   "manual", C_WHITE),
    ("H", "練習時間",         "(分)",              8,   "manual", C_WHITE),
    ("I", "RPE",              "(0〜10)",           7,   "manual", C_WHITE),
    ("J", "練習負荷\nスコア", "(分×RPE)",         8,   "auto",   C_LIGHT_BLU),
    ("K", "主食量",           "(茶碗換算)",        9,   "manual", C_WHITE),
    ("L", "水分摂取量",       "(mL)",              9,   "manual", C_WHITE),
    ("M", "補食・サプリメント","(自由記述)",       30,  "text",   C_LIGHT_GRN),
]

# タイトル
n_cols = len(COLS)
last_col = COLS[-1][0]
ws_d.merge_cells(f"A1:{last_col}1")
ws_d["A1"] = "コンディション × 食事　日次記録シート"
ws_d["A1"].fill = fill(C_HEADER)
ws_d["A1"].font = font(14, True, C_WHITE)
ws_d["A1"].alignment = center()
ws_d.row_dimensions[1].height = 30

# 凡例メモ
ws_d.merge_cells(f"A2:{last_col}2")
ws_d["A2"] = "　青色列：自動計算（入力不要）　緑色列：自由記述　白色列：毎日入力"
ws_d["A2"].fill = fill(C_GRAY)
ws_d["A2"].font = font(9, False, C_DARKGRAY)
ws_d["A2"].alignment = left()
ws_d.row_dimensions[2].height = 16

# ヘッダー行 (3, 4)
for c, (letter, h1, h2, width, kind, bg) in enumerate(COLS, 1):
    # 行3: ヘッダー名
    cell3 = ws_d.cell(row=3, column=c)
    cell3.value = h1
    cell3.fill = fill(C_HEADER)
    cell3.font = font(9, True, C_WHITE)
    cell3.alignment = center()
    cell3.border = border_thin(C_WHITE)

    # 行4: 単位
    cell4 = ws_d.cell(row=4, column=c)
    cell4.value = h2
    cell4.fill = fill("2E4F7F")
    cell4.font = font(8, False, "93C5FD")
    cell4.alignment = center()
    cell4.border = border_thin(C_WHITE)

    set_col_width(ws_d, letter, width)

ws_d.row_dimensions[3].height = 22
ws_d.row_dimensions[4].height = 16

# データ行（30日分）
start_date = date(2026, 6, 1)
DATA_START = 5
DATA_END   = DATA_START + 29  # 30日

for i in range(30):
    row = DATA_START + i
    d = start_date + timedelta(days=i)
    ws_d.row_dimensions[row].height = 18

    for c, (letter, h1, h2, width, kind, bg) in enumerate(COLS, 1):
        cell = ws_d.cell(row=row, column=c)
        cell.border = border_thin()
        cell.alignment = center()

        # 行の背景（交互）
        base_bg = "F8FAFC" if i % 2 == 0 else C_WHITE
        if kind == "auto":
            cell.fill = fill("EFF6FF") if i % 2 == 0 else fill(C_LIGHT_BLU)
        elif kind == "text":
            cell.fill = fill("F0FDF4") if i % 2 == 0 else fill(C_LIGHT_GRN)
            cell.alignment = left()
        else:
            cell.fill = fill(base_bg)

        # 値・数式の設定
        if letter == "A":
            cell.value = d
            cell.number_format = 'M月D日(aaa)'
            cell.font = font(9, True)
        elif letter == "C":
            # 前日比
            if row > DATA_START:
                cell.value = f"=B{row}-B{row-1}"
                cell.number_format = '+0.0;-0.0;0.0'
            cell.font = font(9, False, C_SUBHDR)
        elif letter == "D":
            # 3日移動平均
            if row >= DATA_START + 2:
                cell.value = f"=IFERROR(AVERAGE(B{row-2}:B{row}),\"\")"
                cell.number_format = '0.0'
            cell.font = font(9, False, C_SUBHDR)
        elif letter == "J":
            # 練習負荷スコア
            cell.value = f"=IFERROR(H{row}*I{row},\"\")"
            cell.number_format = '0'
            cell.font = font(9, False, C_SUBHDR)
        else:
            cell.font = font(9)

# ── 入力規則（データバリデーション）────────────────────────
# 疲労度 0-10
dv_fatigue = DataValidation(type="whole", operator="between",
                            formula1="0", formula2="10",
                            showErrorMessage=True,
                            errorTitle="入力エラー",
                            error="0〜10の整数を入力してください")
dv_fatigue.sqref = f"E{DATA_START}:E{DATA_END}"
ws_d.add_data_validation(dv_fatigue)

# 睡眠の質 0-5
dv_sleep = DataValidation(type="whole", operator="between",
                           formula1="0", formula2="5",
                           showErrorMessage=True,
                           errorTitle="入力エラー",
                           error="0〜5の整数を入力してください")
dv_sleep.sqref = f"G{DATA_START}:G{DATA_END}"
ws_d.add_data_validation(dv_sleep)

# RPE 0-10
dv_rpe = DataValidation(type="whole", operator="between",
                         formula1="0", formula2="10",
                         showErrorMessage=True,
                         errorTitle="入力エラー",
                         error="0〜10の整数を入力してください")
dv_rpe.sqref = f"I{DATA_START}:I{DATA_END}"
ws_d.add_data_validation(dv_rpe)

# ── 条件付き書式（自動警告）────────────────────────────────
data_range = f"{DATA_START}:{DATA_END}"

# 体重前日比 ≤ -1.0 → 赤
ws_d.conditional_formatting.add(
    f"C{DATA_START}:C{DATA_END}",
    CellIsRule(operator="lessThanOrEqual", formula=["-1.0"],
               fill=fill(C_LIGHT_RED),
               font=Font(color=C_WARN_RED, bold=True, name="メイリオ", size=9))
)

# 疲労度 ≥ 8 → 橙
ws_d.conditional_formatting.add(
    f"E{DATA_START}:E{DATA_END}",
    CellIsRule(operator="greaterThanOrEqual", formula=["8"],
               fill=fill("FFEDD5"),
               font=Font(color=C_WARN_ORG, bold=True, name="メイリオ", size=9))
)

# 主食量 < 2 → 黄
ws_d.conditional_formatting.add(
    f"K{DATA_START}:K{DATA_END}",
    CellIsRule(operator="lessThan", formula=["2"],
               fill=fill(C_LIGHT_YLW),
               font=Font(color=C_WARN_YLW, bold=True, name="メイリオ", size=9))
)

# 水分 < 2000 → 水色
ws_d.conditional_formatting.add(
    f"L{DATA_START}:L{DATA_END}",
    CellIsRule(operator="lessThan", formula=["2000"],
               fill=fill("E0F2FE"),
               font=Font(color="0369A1", bold=True, name="メイリオ", size=9))
)

# 練習負荷スコア：カラースケール（緑〜黄〜赤）
ws_d.conditional_formatting.add(
    f"J{DATA_START}:J{DATA_END}",
    ColorScaleRule(start_type="num", start_value=0,   start_color="DCFCE7",
                   mid_type="num",   mid_value=500,   mid_color="FEF9C3",
                   end_type="num",   end_value=1000,  end_color="FEE2E2")
)

# ウィンドウ枠固定（ヘッダー4行 + 日付列）
ws_d.freeze_panes = "B5"

# =========================================================================
# ③ 週次サマリーシート + グラフ
# =========================================================================
ws_w = wb.create_sheet("週次サマリー")
ws_w.sheet_view.showGridLines = False

ws_w.merge_cells("A1:J1")
ws_w["A1"] = "週次サマリー（自動集計）"
ws_w["A1"].fill = fill(C_HEADER)
ws_w["A1"].font = font(14, True, C_WHITE)
ws_w["A1"].alignment = center()
ws_w.row_dimensions[1].height = 30

ws_w.merge_cells("A2:J2")
ws_w["A2"] = "※ 日次記録シートに入力すると自動で集計されます。週の開始は月曜日とします。"
ws_w["A2"].fill = fill(C_GRAY)
ws_w["A2"].font = font(9, False, C_DARKGRAY)
ws_w["A2"].alignment = left()
ws_w.row_dimensions[2].height = 16

# 週サマリー列定義
W_COLS = [
    ("A", "週",           "（No.）",       6),
    ("B", "期間",         "",              16),
    ("C", "平均体重",     "(kg)",           9),
    ("D", "体重変化",     "(週初→週末)",    9),
    ("E", "平均疲労度",   "(0〜10)",        9),
    ("F", "週合計\n負荷", "(分×RPE合計)",  10),
    ("G", "平均\n主食量", "(茶碗/日)",      9),
    ("H", "平均\n水分量", "(mL/日)",        9),
    ("I", "平均\n睡眠",   "(h/日)",         8),
    ("J", "コメント・\n所見", "",           20),
]

for c, (letter, h1, h2, width) in enumerate(W_COLS, 1):
    c3 = ws_w.cell(row=3, column=c, value=h1)
    c3.fill = fill(C_HEADER); c3.font = font(9, True, C_WHITE)
    c3.alignment = center(); c3.border = border_thin(C_WHITE)
    c4 = ws_w.cell(row=4, column=c, value=h2)
    c4.fill = fill("2E4F7F"); c4.font = font(8, False, "93C5FD")
    c4.alignment = center(); c4.border = border_thin(C_WHITE)
    set_col_width(ws_w, letter, width)

ws_w.row_dimensions[3].height = 22
ws_w.row_dimensions[4].height = 16

# 週サマリーデータ行（4週分 + 手動入力分）
# 日次記録シートの行位置: DATA_START=5, 各週7行
week_labels = ["第1週", "第2週", "第3週", "第4週"]
week_dates = [
    ("6/1(月)", "6/7(日)",   5, 11),
    ("6/8(月)", "6/14(日)", 12, 18),
    ("6/15(月)","6/21(日)", 19, 25),
    ("6/22(月)","6/28(日)", 26, 32),
]

W_DATA_START = 5
for wi, (wlabel, (ds, de, r1, r2)) in enumerate(zip(week_labels, week_dates)):
    row = W_DATA_START + wi
    ws_w.row_dimensions[row].height = 22
    bg = "F8FAFC" if wi % 2 == 0 else C_WHITE

    # 参照する日次記録の実際の行番号（r1〜r2 は DATA_START=5 を基準）
    dr1 = r1  # 日次記録の開始行
    dr2 = min(r2, DATA_END)  # 日次記録の終了行（30日以内）

    cells_data = [
        (1, wlabel, True, C_SUBHDR),
        (2, f"{ds}〜{de}", False, "1E293B"),
        (3, f"=IFERROR(AVERAGE('日次記録'!B{dr1}:B{dr2}),\"\")", False, C_SUBHDR),
        (4, f"=IFERROR('日次記録'!B{dr2}-'日次記録'!B{dr1},\"\")", False, C_SUBHDR),
        (5, f"=IFERROR(AVERAGE('日次記録'!E{dr1}:E{dr2}),\"\")", False, C_SUBHDR),
        (6, f"=IFERROR(SUM('日次記録'!J{dr1}:J{dr2}),\"\")", False, C_SUBHDR),
        (7, f"=IFERROR(AVERAGE('日次記録'!K{dr1}:K{dr2}),\"\")", False, C_SUBHDR),
        (8, f"=IFERROR(AVERAGE('日次記録'!L{dr1}:L{dr2}),\"\")", False, C_SUBHDR),
        (9, f"=IFERROR(AVERAGE('日次記録'!F{dr1}:F{dr2}),\"\")", False, C_SUBHDR),
        (10, "", False, "1E293B"),
    ]
    for col, val, bold, color in cells_data:
        cell = ws_w.cell(row=row, column=col, value=val)
        cell.fill = fill(bg)
        cell.font = font(10, bold, color)
        cell.alignment = center() if col != 10 else left()
        cell.border = border_thin()
        if col in [3,4,7,8,9]:
            cell.number_format = "0.0"

# 警告行: 疲労度平均 ≥ 7 → 橙
ws_w.conditional_formatting.add(
    f"E{W_DATA_START}:E{W_DATA_START+3}",
    CellIsRule(operator="greaterThanOrEqual", formula=["7"],
               fill=fill("FFEDD5"),
               font=Font(color=C_WARN_ORG, bold=True, name="メイリオ", size=10))
)
# 主食量平均 < 2 → 黄
ws_w.conditional_formatting.add(
    f"G{W_DATA_START}:G{W_DATA_START+3}",
    CellIsRule(operator="lessThan", formula=["2"],
               fill=fill(C_LIGHT_YLW),
               font=Font(color=C_WARN_YLW, bold=True, name="メイリオ", size=10))
)

# ── グラフ① 体重移動平均の折れ線（日次記録から） ─────────────
chart1 = LineChart()
chart1.title = "グラフ① 体重3日移動平均の推移"
chart1.style = 10
chart1.y_axis.title = "体重 (kg)"
chart1.x_axis.title = "日付"
chart1.width  = 18
chart1.height = 10

weight_data = Reference(ws_d, min_col=4, min_row=DATA_START,
                         max_row=DATA_END)  # 3日移動平均
fatigue_data = Reference(ws_d, min_col=5, min_row=DATA_START,
                          max_row=DATA_END)  # 疲労度

s_weight = Series(weight_data, title="3日移動平均体重(kg)")
s_weight.graphicalProperties.line.solidFill = "2563EB"
s_weight.graphicalProperties.line.width = 20000
chart1.append(s_weight)

# 日付ラベル
dates_ref = Reference(ws_d, min_col=1, min_row=DATA_START, max_row=DATA_END)
chart1.set_categories(dates_ref)
ws_w.add_chart(chart1, "A10")

# ── グラフ② 週次：練習負荷（棒）× 主食量平均（折れ線） ────────
chart2 = BarChart()
chart2.type = "col"
chart2.title = "グラフ② 週ごとの練習負荷スコアと主食量"
chart2.style = 10
chart2.y_axis.title = "練習負荷スコア"
chart2.x_axis.title = "週"
chart2.width  = 18
chart2.height = 10

load_ref  = Reference(ws_w, min_col=6, min_row=W_DATA_START,
                       max_row=W_DATA_START+3)
food_ref  = Reference(ws_w, min_col=7, min_row=W_DATA_START,
                       max_row=W_DATA_START+3)
week_ref  = Reference(ws_w, min_col=1, min_row=W_DATA_START,
                       max_row=W_DATA_START+3)

s_load = Series(load_ref, title="練習負荷スコア（週合計）")
s_load.graphicalProperties.solidFill = "DC2626"
chart2.append(s_load)

s_food = Series(food_ref, title="平均主食量（茶碗/日）")
# 折れ線に変換して2軸
from openpyxl.chart import LineChart as LC2
line2 = LC2()
s_food2 = Series(food_ref, title="平均主食量（茶碗/日）")
s_food2.graphicalProperties.line.solidFill = "16A34A"
s_food2.graphicalProperties.line.width = 25000
line2.append(s_food2)
line2.y_axis.axId = 200
line2.y_axis.title = "主食量 (茶碗/日)"
line2.y_axis.crosses = "max"
chart2 += line2

chart2.set_categories(week_ref)
ws_w.add_chart(chart2, "A29")

# =========================================================================
# 保存
# =========================================================================
out = "/home/user/AK/conditioning_tracker.xlsx"
wb.save(out)
print(f"完了: {out}")
