"""
legends.xlsx を生成するスクリプト。
このファイルを編集後、visualize_v2.py / visualize2_v2.py を実行すると
編集内容が図表に反映されます。
"""
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = openpyxl.Workbook()

# ── スタイル定義 ──────────────────────────────────────────
HDR_FILL  = PatternFill("solid", fgColor="2F5496")
HDR_FONT  = Font(color="FFFFFF", bold=True, size=11)
EVEN_FILL = PatternFill("solid", fgColor="DCE6F1")
NOTE_FONT = Font(color="7F7F7F", italic=True, size=9)
BORDER = Border(
    left=Side(style='thin', color='BFBFBF'),
    right=Side(style='thin', color='BFBFBF'),
    top=Side(style='thin', color='BFBFBF'),
    bottom=Side(style='thin', color='BFBFBF'),
)

def write_header(ws, row, cols):
    for c, val in enumerate(cols, 1):
        cell = ws.cell(row=row, column=c, value=val)
        cell.fill = HDR_FILL
        cell.font = HDR_FONT
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = BORDER

def write_row(ws, row, values, even=False):
    for c, val in enumerate(values, 1):
        cell = ws.cell(row=row, column=c, value=val)
        if even:
            cell.fill = EVEN_FILL
        cell.alignment = Alignment(horizontal='left', vertical='center')
        cell.border = BORDER

def set_col_widths(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w

def add_note(ws, row, col, text):
    cell = ws.cell(row=row, column=col, value=text)
    cell.font = NOTE_FONT

# ═══════════════════════════════════════════════════════════
# シート1: グループ名・性別
# ═══════════════════════════════════════════════════════════
ws1 = wb.active
ws1.title = "グループ設定"
ws1.row_dimensions[1].height = 22

write_header(ws1, 1, ["パート", "表示名", "性別（男性/女性）", "カラーコード"])
rows = [
    ("A", "A", "男性", "#3A7FC1"),
    ("B", "B", "男性", "#3A7FC1"),
    ("C", "C", "男性", "#3A7FC1"),
    ("D", "D", "男性", "#3A7FC1"),
    ("E", "E", "男性", "#3A7FC1"),
    ("F", "F", "女性", "#E05C7A"),
    ("G", "G", "女性", "#E05C7A"),
    ("H", "H", "女性", "#E05C7A"),
    ("I", "I", "女性", "#E05C7A"),
]
for i, r in enumerate(rows, 2):
    write_row(ws1, i, r, even=(i % 2 == 0))

add_note(ws1, 12, 1, "※ カラーコードは16進数（例：#3A7FC1）で指定してください")
set_col_widths(ws1, [10, 12, 18, 16])

# ═══════════════════════════════════════════════════════════
# シート2: 図1（食品群比較）の凡例
# ═══════════════════════════════════════════════════════════
ws2 = wb.create_sheet("図1_食品群比較")
write_header(ws2, 1, ["キー", "表示テキスト", "備考"])
rows2 = [
    ("title_fig1",   "食品群別 摂取量の男女比較（グループ平均）", "図1タイトル"),
    ("legend_male",  "男性 (A–E 平均)", "男性の凡例ラベル"),
    ("legend_female","女性 (F–I 平均)", "女性の凡例ラベル"),
    ("xlabel_fig1",  "摂取量 (g/日)", "X軸ラベル"),
    ("title_fig2",   "食品バランス レーダーチャート\n（男女グループ平均）", "図2タイトル"),
    ("legend_male_radar",  "男性平均", "レーダー男性ラベル"),
    ("legend_female_radar","女性平均", "レーダー女性ラベル"),
    ("title_fig3",   "グループ別 食品摂取量（積み上げ棒グラフ）", "図3タイトル"),
    ("label_male_group",  "男性グループ", "図3 男性ゾーンラベル"),
    ("label_female_group","女性グループ", "図3 女性ゾーンラベル"),
    ("title_fig4",   "グループ別 身体特性（年齢・身長・体重）", "図4タイトル"),
    ("legend_male_body",  "男性 (A–E)", "図4 男性凡例"),
    ("legend_female_body","女性 (F–I)", "図4 女性凡例"),
    ("title_fig5",   "男女差が大きい食品群\n（＋：男性が多い　−：女性が多い）", "図5タイトル"),
    ("legend_more_male",  "男性が多い", "図5 男性ラベル"),
    ("legend_more_female","女性が多い", "図5 女性ラベル"),
    ("xlabel_fig5",  "男性平均 − 女性平均 (g/日)", "図5 X軸ラベル"),
]
for i, r in enumerate(rows2, 2):
    write_row(ws2, i, r, even=(i % 2 == 0))
set_col_widths(ws2, [22, 42, 24])

# ═══════════════════════════════════════════════════════════
# シート3: 図2（栄養素）の凡例
# ═══════════════════════════════════════════════════════════
ws3 = wb.create_sheet("図2_栄養素")
write_header(ws3, 1, ["キー", "表示テキスト", "備考"])
rows3 = [
    ("title_figA",   "エネルギー・主要栄養素の男女グループ比較", "figAタイトル"),
    ("avg_male_label",  "男平均", "平均ラインラベル（男）※値は自動付加"),
    ("avg_female_label","女平均", "平均ラインラベル（女）※値は自動付加"),
    ("title_figB",   "PFCエネルギー比率（各グループ）", "figBタイトル"),
    ("label_protein","たんぱく質", "PFC たんぱく質"),
    ("label_fat",    "脂質",       "PFC 脂質"),
    ("label_carb",   "炭水化物",   "PFC 炭水化物"),
    ("label_male_zone",  "男性", "figB 男性ゾーン"),
    ("label_female_zone","女性", "figB 女性ゾーン"),
    ("title_figC",   "ミネラル摂取バランス（レーダーチャート）\n※鉄・亜鉛は×50、リンは÷10でスケール調整", "figCタイトル"),
    ("legend_male_c",  "男性平均", "figC 男性凡例"),
    ("legend_female_c","女性平均", "figC 女性凡例"),
    ("title_figD",   "ビタミン摂取量の男女比較（グループ平均）", "figDタイトル"),
    ("legend_male_d",  "男性平均", "figD 男性凡例"),
    ("legend_female_d","女性平均", "figD 女性凡例"),
    ("title_figE",   "注目指標：塩分・食物繊維・コレステロール・水分", "figEタイトル"),
    ("ref_salt",     "WHO目標: 8g以下", "食塩参照線ラベル"),
    ("ref_fiber",    "目安量(成人): 18–21g", "食物繊維参照線ラベル"),
    ("title_figF",   "ミネラル摂取量 ヒートマップ（行内Zスコアで色付け）", "figFタイトル"),
    ("cbar_label",   "Zスコア（行内）", "カラーバーラベル"),
    ("label_male_hm",  "男性", "figF 男性ゾーン"),
    ("label_female_hm","女性", "figF 女性ゾーン"),
]
for i, r in enumerate(rows3, 2):
    write_row(ws3, i, r, even=(i % 2 == 0))
set_col_widths(ws3, [22, 48, 28])

# ═══════════════════════════════════════════════════════════
# シート4: 食品群ラベル
# ═══════════════════════════════════════════════════════════
ws4 = wb.create_sheet("食品群ラベル")
write_header(ws4, 1, ["キー", "図1用ラベル", "レーダー用ラベル", "積み上げ用ラベル"])
food_labels = [
    ("穀類",           "穀類",           "穀類",     "穀類"),
    ("いも類",         "いも類",         "いも類",   "いも類"),
    ("豆類",           "豆類",           "豆類",     "豆類"),
    ("野菜類",         "野菜類",         "野菜類",   "野菜類"),
    ("果物",           "果物",           "果物",     "果物"),
    ("魚介類",         "魚介類",         "魚介類",   "魚介類"),
    ("肉類",           "肉類",           "肉類",     "肉類"),
    ("卵類",           "卵類",           "卵類",     "卵類"),
    ("乳類",           "乳類",           "乳類",     "乳類"),
]
food_labels_fixed = [
    ("穀類",           "穀類",           "穀類",         "穀類"),
    ("いも類",         "いも類",         "いも類",       "いも類"),
    ("豆類",           "豆類",           "豆類",         "豆類"),
    ("野菜類",         "野菜類",         "野菜類",       "野菜類"),
    ("果物",           "果物",           "果物",         "果物"),
    ("魚介類",         "魚介類",         "魚介類",       "魚介類"),
    ("肉類",           "肉類",           "肉類",         "肉類"),
    ("卵類",           "卵類",           "卵類",         "卵類"),
    ("乳類",           "乳類",           "乳類",         "乳類"),
    ("菓子類",         "菓子類",         "（レーダー未使用）","菓子類"),
    ("非アルコール飲料","非アルコール飲料","（レーダー未使用）","非アルコール飲料"),
    ("海藻類",         "海藻類",         "（レーダー未使用）","（積み上げ未使用）"),
]
for i, r in enumerate(food_labels_fixed, 2):
    write_row(ws4, i, r, even=(i % 2 == 0))
set_col_widths(ws4, [20, 20, 20, 20])

# ═══════════════════════════════════════════════════════════
# シート5: ミネラル・ビタミンラベル
# ═══════════════════════════════════════════════════════════
ws5 = wb.create_sheet("栄養素ラベル")
write_header(ws5, 1, ["キー", "表示ラベル", "単位", "備考"])
nutr_labels = [
    ("エネルギー",          "エネルギー (kcal/日)",    "kcal",  ""),
    ("エネルギー_kg",       "エネルギー (kcal/kg BW)", "kcal/kg",""),
    ("たんぱく質",          "たんぱく質 (g/日)",        "g",     ""),
    ("脂質",               "脂質 (g/日)",              "g",     ""),
    ("炭水化物",            "炭水化物 (g/日)",          "g",     ""),
    ("炭水化物_kg",         "炭水化物 (g/kg BW)",       "g/kg",  ""),
    ("食塩相当量",          "食塩相当量 (g/日)",        "g",     "spotlightパネル1"),
    ("食物繊維総量",        "食物繊維総量 (g/日)",      "g",     "spotlightパネル2"),
    ("コレステロール",      "コレステロール (mg/日)",   "mg",    "spotlightパネル3"),
    ("水分",               "水分 (g/日)",              "g",     "spotlightパネル4"),
    ("ナトリウム",          "ナトリウム(mg)",           "mg",    "ヒートマップ"),
    ("カリウム",            "カリウム(mg)",             "mg",    "ヒートマップ"),
    ("カルシウム",          "カルシウム(mg)",           "mg",    "ヒートマップ・レーダー"),
    ("マグネシウム",        "マグネシウム(mg)",         "mg",    "ヒートマップ・レーダー"),
    ("リン",               "リン(mg)",                 "mg",    "ヒートマップ・レーダー"),
    ("鉄",                 "鉄(mg)",                   "mg",    "ヒートマップ・レーダー"),
    ("亜鉛",               "亜鉛(mg)",                 "mg",    "ヒートマップ・レーダー"),
    ("銅",                 "銅(mg)",                   "mg",    "ヒートマップ"),
    ("マンガン",            "マンガン(mg)",             "mg",    "ヒートマップ"),
    ("ビタミンA",           "ビタミンA\n(µg RE)",      "µg RE", "ビタミン比較"),
    ("ビタミンD",           "ビタミンD\n(µg)",         "µg",    "ビタミン比較"),
    ("ビタミンE",           "ビタミンE\n(mg)",         "mg",    "ビタミン比較"),
    ("ビタミンB1",          "ビタミンB1\n(mg)",        "mg",    "ビタミン比較"),
    ("ナイアシン",          "ナイアシン\n(mg)",        "mg",    "ビタミン比較"),
    ("ビタミンB6",          "ビタミンB6\n(mg)",        "mg",    "ビタミン比較"),
    ("ビタミンB12",         "ビタミンB12\n(µg)",       "µg",    "ビタミン比較"),
    ("葉酸",               "葉酸\n(µg)",              "µg",    "ビタミン比較"),
    ("ビタミンC",           "ビタミンC\n(mg)",         "mg",    "ビタミン比較"),
]
for i, r in enumerate(nutr_labels, 2):
    write_row(ws5, i, r, even=(i % 2 == 0))
set_col_widths(ws5, [20, 28, 10, 24])

# ═══════════════════════════════════════════════════════════
# シート6: 食事摂取基準（2020年版）
# ═══════════════════════════════════════════════════════════
ws6 = wb.create_sheet("食事摂取基準")

# タイトル行
title_cell = ws6.cell(row=1, column=1,
    value="食事摂取基準 2020年版（推奨量／目安量／目標量）　※空欄＝基準値なし・値を変更する場合はこのシートを編集してください")
title_cell.font = Font(bold=True, size=10, color="1F4E79")
ws6.merge_cells("A1:I1")

write_header(ws6, 2, [
    "栄養素キー", "単位", "種別",
    "男性 18-29歳", "男性 30-49歳",
    "女性 18-29歳", "女性 30-49歳",
    "凡例ラベル（男性）", "凡例ラベル（女性）",
])
ws6.row_dimensions[2].height = 22

# (キー, 単位, 種別, m18, m30, f18, f30, lbl_m, lbl_f)
dri_rows = [
    ("エネルギー",     "kcal/日", "推定必要量",  2650,  2700,  2000,  2050,
     "推定必要量(男)", "推定必要量(女)"),
    ("エネルギー_kg",  "kcal/kg", "参考値",      None,  None,  None,  None,
     "",               ""),
    ("たんぱく質",     "g/日",    "推奨量",       65,    65,    50,    50,
     "推奨量(男)",     "推奨量(女)"),
    ("たんぱく質/kg BW","g/kg",   "参考値",      0.9,   0.9,   0.9,   0.9,
     "参考値(男)",     "参考値(女)"),
    ("炭水化物",       "g/日",    "目標量(%E換算)",None, None,  None,  None,
     "",               ""),
    ("炭水化物_kg",    "g/kg",    "目標量(%E換算)",None, None,  None,  None,
     "",               ""),
    ("PFC",            "%E",      "目標量（下限）", None, None, None, None,
     "",               ""),
    ("食物繊維総量",   "g/日",    "目安量",       21,    21,    18,    18,
     "目安量(男)",     "目安量(女)"),
    ("食塩相当量",     "g/日",    "目標量(未満)",  7.5,   7.5,   6.5,   6.5,
     "目標量(男)",     "目標量(女)"),
    ("カルシウム",     "mg/日",   "推奨量",       800,   750,   650,   650,
     "推奨量(男)",     "推奨量(女)"),
    ("鉄",             "mg/日",   "推奨量",        7.5,   7.5,  10.5,  10.5,
     "推奨量(男)",     "推奨量(女)"),
    ("ビタミンD",      "µg/日",   "目安量",        8.5,   8.5,   8.5,   8.5,
     "目安量(男)",     "目安量(女)"),
    ("ビタミンB1",     "mg/日",   "推奨量",        1.4,   1.4,   1.1,   1.1,
     "推奨量(男)",     "推奨量(女)"),
    ("ビタミンB2",     "mg/日",   "推奨量",        1.6,   1.6,   1.2,   1.2,
     "推奨量(男)",     "推奨量(女)"),
    ("ビタミンB6",     "mg/日",   "推奨量",        1.4,   1.4,   1.1,   1.1,
     "推奨量(男)",     "推奨量(女)"),
    ("ビタミンC",      "mg/日",   "推奨量",       100,   100,   100,   100,
     "推奨量(男)",     "推奨量(女)"),
]
for i, r in enumerate(dri_rows, 3):
    write_row(ws6, i, r, even=(i % 2 == 0))

add_note(ws6, 20, 1,
    "※ エネルギー推定必要量はPAL II（ふつう）の値。たんぱく質/kg BW の参考値は EAR 算定基礎値（0.9g/kg）。"
    "炭水化物は目標量が 50〜65%E のため g/日換算なし。")
set_col_widths(ws6, [20, 10, 16, 14, 14, 14, 14, 18, 18])

wb.save('/home/user/AK/legends.xlsx')
print("legends.xlsx saved")
