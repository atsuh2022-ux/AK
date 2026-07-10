from docx import Document
from docx.shared import Pt, Emu, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml

doc = Document()

section = doc.sections[0]
section.page_width = Emu(7772400)
section.page_height = Emu(10058400)
section.left_margin = Emu(685800)
section.right_margin = Emu(685800)
section.top_margin = Emu(685800)
section.bottom_margin = Emu(685800)

FONT_NAME = 'ヒラギノ丸ゴ Pro W4'

DARK_BLUE = '1A5276'
DARK_BG = '1B2631'
LIGHT_BLUE_ROW = 'EBF5FB'
LIGHT_GREEN_ROW = 'EAFAF1'
LIGHT_ORANGE_ROW = 'FEF5E7'
SUMMARY_BG = 'EAF2FF'
POINTS_BG = 'FEF9E7'
TEXT_COLOR = RGBColor(0x2C, 0x3E, 0x50)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
RED_ACCENT = RGBColor(0x92, 0x2B, 0x21)
GOLD_ACCENT = RGBColor(0x7D, 0x66, 0x08)
GRAY_TEXT = RGBColor(0x7F, 0x8C, 0x8D)
BLUE_TITLE = RGBColor(0x1A, 0x52, 0x76)
RACE_BG = 'F5B7B1'
RECOVERY_BG = 'D5F5E3'


def set_cell_shading(cell, color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)


def add_run(paragraph, text, font_name=FONT_NAME, size=Pt(9.5), bold=False, color=TEXT_COLOR):
    run = paragraph.add_run(text)
    run.font.name = font_name
    run.font.size = size
    run.font.bold = bold
    if color:
        run.font.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:eastAsia="{font_name}"/>')
        rPr.append(rFonts)
    else:
        rFonts.set(qn('w:eastAsia'), font_name)
    return run


def set_row_height(row, height_twips):
    trPr = row._tr.get_or_add_trPr()
    trHeight = parse_xml(f'<w:trHeight {nsdecls("w")} w:val="{height_twips}"/>')
    trPr.append(trHeight)


def set_col_width(cell, width_twips):
    tcPr = cell._tc.get_or_add_tcPr()
    tcW = tcPr.find(qn('w:tcW'))
    if tcW is None:
        tcW = parse_xml(f'<w:tcW {nsdecls("w")} w:w="{width_twips}" w:type="dxa"/>')
        tcPr.append(tcW)
    else:
        tcW.set(qn('w:w'), str(width_twips))
        tcW.set(qn('w:type'), 'dxa')


def merge_row_cells(table, row_idx, start_col, end_col):
    table.cell(row_idx, start_col).merge(table.cell(row_idx, end_col))


def add_section_header(table, row_idx, text, bg_color=DARK_BG):
    merge_row_cells(table, row_idx, 0, 4)
    cell = table.cell(row_idx, 0)
    set_cell_shading(cell, bg_color)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    add_run(p, text, bold=True, color=WHITE, size=Pt(10))
    set_row_height(table.rows[row_idx], 350)


def add_content_row(table, row_idx, time_str, timing, food_items, carb, point,
                    bg_color=LIGHT_BLUE_ROW, row_height=800):
    cells = table.rows[row_idx].cells
    for i in range(5):
        set_cell_shading(cells[i], bg_color)

    p = cells[0].paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(p, time_str, size=Pt(9.5), color=TEXT_COLOR)

    p = cells[1].paragraphs[0]
    add_run(p, timing, size=Pt(9.5), bold=True, color=TEXT_COLOR)

    p = cells[2].paragraphs[0]
    for j, item in enumerate(food_items):
        if j > 0:
            add_run(p, '\n', size=Pt(9.5))
        is_note = item.startswith('※') or item.startswith('(')
        add_run(p, item, size=Pt(9), color=GRAY_TEXT if is_note else TEXT_COLOR)

    p = cells[3].paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(p, carb, size=Pt(9.5), bold=True, color=TEXT_COLOR)

    p = cells[4].paragraphs[0]
    add_run(p, point, size=Pt(9), color=TEXT_COLOR)

    set_row_height(table.rows[row_idx], row_height)


def add_race_row(table, row_idx, time_str, text):
    cells = table.rows[row_idx].cells
    merge_row_cells(table, row_idx, 1, 4)
    for i in range(5):
        set_cell_shading(cells[i], RACE_BG)
    p = cells[0].paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(p, time_str, size=Pt(9.5), bold=True, color=RED_ACCENT)
    cell = table.cell(row_idx, 1)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(p, text, size=Pt(10), bold=True, color=RED_ACCENT)
    set_row_height(table.rows[row_idx], 280)


def add_no_intake_row(table, row_idx, time_range, label):
    cells = table.rows[row_idx].cells
    merge_row_cells(table, row_idx, 2, 4)
    for i in range(5):
        set_cell_shading(cells[i], LIGHT_BLUE_ROW)
    p = cells[0].paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(p, time_range, size=Pt(9.5), color=TEXT_COLOR)
    p = cells[1].paragraphs[0]
    add_run(p, label, size=Pt(9.5), bold=True, color=TEXT_COLOR)
    cell = table.cell(row_idx, 2)
    p = cell.paragraphs[0]
    add_run(p, f'{time_range}は摂取しない', size=Pt(9), color=GRAY_TEXT)
    set_row_height(table.rows[row_idx], 280)


# ========================================
# TITLE
# ========================================
h1 = doc.add_heading(level=1)
h1.alignment = WD_ALIGN_PARAGRAPH.LEFT
add_run(h1, '　前日夜〜試合当日 食事・補食プラン', size=Pt(16), bold=True, color=TEXT_COLOR)

h2 = doc.add_heading(level=2)
h2.alignment = WD_ALIGN_PARAGRAPH.LEFT
add_run(h2, '普段のスタイルを活かした試合食　｜　体重64kg　糖質目標 5〜6g/kg', size=Pt(12), color=TEXT_COLOR)

intro = doc.add_paragraph()
add_run(intro,
    '100m 予選・決勝に出場するため、午前中にしっかり朝食・昼食でエネルギーを蓄え、'
    '午後のレースに備えます。予選（16:05）→決勝（18:00）のレース間は約2時間と短いため、'
    '回復補食はゼリー・ドリンク中心で胃への負担をゼロにします。'
    '普段から食べ慣れているサケ・白米・サラダ・ヨーグルトをベースに、'
    '当日レース前は消化しやすい食材に絞りましょう。',
    size=Pt(10), color=TEXT_COLOR)

# ========================================
# MAIN TABLE
# ========================================
# Rows:
#  0: Header
#  1: 前日 section
#  2: 前日夕食
#  3: 前日補食
#  4: 当日 section header
#  5: 起床・水分
#  6: 朝食
#  7: 間食（午前）
#  8: 昼食
#  9: 補食①（予選前）
# 10: ウォームアップ中
# 11: 招集前
# 12: 予選スタート
# 13: レース間 section
# 14: レース直後 回復
# 15: ウォームアップ中（決勝）
# 16: 招集前
# 17: 決勝スタート

NUM_ROWS = 18
table = doc.add_table(rows=NUM_ROWS, cols=5)
table.alignment = WD_TABLE_ALIGNMENT.CENTER

col_widths = [919, 1521, 2934, 902, 3788]
for row in table.rows:
    for i, w in enumerate(col_widths):
        set_col_width(row.cells[i], w)

# Row 0: Header
for i, label in enumerate(['時間', 'タイミング', '食事・補食内容', '糖質量', '目的・ポイント']):
    cell = table.cell(0, i)
    set_cell_shading(cell, DARK_BLUE)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(p, label, bold=True, color=WHITE, size=Pt(10))
set_row_height(table.rows[0], 521)

# Row 1: 前日セクション
add_section_header(table, 1, '前日（7/11 土曜日）　布勢スプリント2026', DARK_BG)

# Row 2: 前日夕食
add_content_row(table, 2,
    '18:00〜\n20:00',
    '前日 夕食',
    [
        '白米 250g',
        '生姜焼き（豚肉、玉ねぎ）',
        'ブロッコリー',
        'サラダ（レタス、トマト2個、たまご1個、鶏肉）',
        'ヨーグルト',
        'ゴールドキウイ',
    ],
    '約130g',
    '翌日に向けてグリコーゲンをしっかり蓄える。早めに食べて消化時間を十分に確保する。'
    '揚げ物や脂質の多いものは避け、消化しやすい調理法を選ぶ。',
    LIGHT_BLUE_ROW, 950)

# Row 3: 前日補食
add_content_row(table, 3,
    '20:00〜\n21:00',
    '補食\n（空腹時）',
    [
        '焼き芋 小1本 or 和菓子',
        '※空腹でなければ',
        '無理して摂取はしない',
    ],
    '約40〜50g',
    'できれば就寝2時間前までに。就寝直前の摂取は翌朝の胃もたれにつながるため避ける。'
    '十分な睡眠を確保する。',
    LIGHT_BLUE_ROW, 651)

# Row 4: 当日セクション
add_section_header(table, 4,
    '試合当日（7/12 日曜日）　予選 招集15:45〜55 / 競技16:05　決勝 招集17:40〜50 / 競技18:00',
    DARK_BLUE)
set_row_height(table.rows[4], 566)

# Row 5: 起床
add_content_row(table, 5,
    '',
    '起床\n水分補給',
    ['水 200〜250ml（ゆっくり）'],
    '0g',
    '起床後すぐに水分補給で体内の水分バランスを整える。体調を確認する。',
    LIGHT_GREEN_ROW, 421)

# Row 6: 朝食
add_content_row(table, 6,
    '7:30〜\n8:00',
    '朝食',
    [
        '白米 250g',
        'サケ 1切れ',
        '味噌汁（豆腐、ネギ）',
        'たまご焼き 1個分',
        'ヨーグルト',
        'ゴールドキウイ',
    ],
    '約110g',
    '午後レースのため朝は普段通りしっかり食べてOK。'
    '普段の朝食に近い内容で安心感を持たせる。',
    LIGHT_GREEN_ROW, 950)

# Row 7: 間食（午前）
add_content_row(table, 7,
    '10:00〜\n10:30',
    '間食\n（午前）',
    [
        'バナナ 1本',
        'ヨーグルト or 豆乳',
    ],
    '約30g',
    '朝食と昼食の間のエネルギー補給。'
    '午後レースに向けて糖質を分散して摂取する。',
    LIGHT_GREEN_ROW, 600)

# Row 8: 昼食
add_content_row(table, 8,
    '11:30〜\n12:00',
    '昼食\n（予選\n約4時間前）',
    [
        '白米 250〜300g',
        'サケ 1切れ or 鶏肉ソテー',
        '味噌汁',
        'サラダ（レタス、トマト）',
        '※脂質の多い調理法は避ける',
    ],
    '約100〜\n120g',
    '当日のメインエネルギー源。予選の約4時間前に済ませることで'
    '消化を十分に終えてからレースに臨む。白米をしっかり食べて'
    'グリコーゲンを満たす。',
    LIGHT_GREEN_ROW, 985)

# Row 9: 補食①
add_content_row(table, 9,
    '14:00〜\n14:30',
    '補食①\n（予選\n約1.5〜2時間前）',
    [
        'おにぎり 1個（鮭 or 梅）',
        'エネルギーゼリー 1個',
        '(会場到着時〜アップ前)',
    ],
    '約60〜\n70g',
    '昼食から時間が空くため、おにぎりで糖質を追加補給。'
    'ゼリーで即効性のエネルギーも確保する。胃への負担を抑えるため少量ずつ。',
    LIGHT_GREEN_ROW, 800)

# Row 10: ウォームアップ中
add_content_row(table, 10,
    '15:00〜\n15:30',
    'ウォーム\nアップ中',
    [
        'スポーツドリンク 少量ずつ',
        '(150〜200ml)',
    ],
    '約10〜15g',
    '一気飲みせず少量ずつ補給する。体温に注意しながら水分・電解質を維持する。',
    LIGHT_GREEN_ROW, 600)

# Row 11: 招集前
add_no_intake_row(table, 11, '15:30〜\n15:55', '予選 招集')

# Row 12: 予選スタート
add_race_row(table, 12, '16:05', '🏃 予選 100m スタート')

# Row 13: レース間セクション
add_section_header(table, 13,
    'レース間 回復タイム　（約1時間55分　16:05〜18:00）',
    DARK_BLUE)

# Row 14: レース直後回復
add_content_row(table, 14,
    '〜16:30',
    'レース直後\n回復補給',
    [
        '水分補給',
        'エネルギーゼリー 1個',
        '(なるべく早いタイミングで)',
        '※固形物は消化に時間がかかるため',
        '　ゼリー・ドリンクを優先',
    ],
    '約30〜45g',
    '消耗した糖質をすみやかに補充する。レース間が約2時間と短いため、'
    '固形物は避けてゼリー・ドリンクに限定する。少量ずつゆっくり摂取する。',
    LIGHT_ORANGE_ROW, 900)

# Row 15: ウォームアップ中（決勝）
add_content_row(table, 15,
    '17:00〜\n17:30',
    'アクティブ\nリカバリー\n＋\nウォーム\nアップ',
    [
        '水 or スポーツドリンク 少量ずつ',
        '(100〜150ml)',
        '※この時間帯は固形物を摂らない',
    ],
    '約6〜10g',
    '軽いストレッチ・アップで回復を促進する。この時間に固形物を摂ると'
    '決勝スタート時に胃の重さが残るため避ける。水分補給はこまめに。',
    LIGHT_ORANGE_ROW, 800)

# Row 16: 招集前
add_no_intake_row(table, 16, '17:25〜\n17:50', '決勝 招集')

# Row 17: 決勝スタート
add_race_row(table, 17, '18:00', '🏃 決勝 100m スタート')

# ========================================
# SUMMARY BOX
# ========================================
doc.add_paragraph()
summary_table = doc.add_table(rows=1, cols=1)
summary_table.alignment = WD_TABLE_ALIGNMENT.CENTER
cell = summary_table.cell(0, 0)
set_cell_shading(cell, SUMMARY_BG)

p = cell.paragraphs[0]
add_run(p, '当日 糖質・水分まとめ（体重64kg）', bold=True, color=BLUE_TITLE, size=Pt(11))

p2 = cell.add_paragraph()
add_run(p2, '【前日夜】　夕食：約130g　就寝前補食（任意）：約40〜50g', size=Pt(9.5), color=TEXT_COLOR)

p3 = cell.add_paragraph()
add_run(p3, '【当日 朝〜予選前】　朝食：約110g　間食：約30g　昼食：約100〜120g　補食①：約60〜70g　アップ中：約10〜15g',
        size=Pt(9.5), color=TEXT_COLOR)

p4 = cell.add_paragraph()
add_run(p4, '【レース間〜決勝前】　回復補給：約30〜45g　アップ中：約6〜10g',
        size=Pt(9.5), color=TEXT_COLOR)

p5 = cell.add_paragraph()
add_run(p5, '▶ 前日 糖質トータル：約170〜180g', bold=True, color=RED_ACCENT, size=Pt(9.5))

p6 = cell.add_paragraph()
add_run(p6, '▶ 当日 糖質トータル（夕食前）：約350〜400g（5.5〜6.3g/kg）✓',
        bold=True, color=RED_ACCENT, size=Pt(9.5))

p7 = cell.add_paragraph()
add_run(p7, '※ 午後レースのため、朝食〜昼食〜補食で十分な糖質を蓄積可能。目標5〜6g/kgは当日の食事だけで達成できる。',
        size=Pt(9), color=GRAY_TEXT)

# ========================================
# POINTS BOX
# ========================================
doc.add_paragraph()
points_table = doc.add_table(rows=1, cols=1)
points_table.alignment = WD_TABLE_ALIGNMENT.CENTER
cell = points_table.cell(0, 0)
set_cell_shading(cell, POINTS_BG)

p = cell.paragraphs[0]
add_run(p, '食事・補食のポイント', bold=True, color=BLUE_TITLE, size=Pt(11))

p2 = cell.add_paragraph()
add_run(p2, '【午後レースの食事戦略】', bold=True, color=GOLD_ACCENT, size=Pt(9.5))
p3 = cell.add_paragraph()
add_run(p3, '午前中に朝食・間食・昼食と3回の食事機会があるため、エネルギー貯蔵は余裕を持って行える。'
        '昼食は予選の約4時間前に済ませ、消化を十分に終えてからレースに臨む。',
        size=Pt(9.5), color=TEXT_COLOR)

p4 = cell.add_paragraph()
add_run(p4, '【予選→決勝のレース間（約2時間）】', bold=True, color=GOLD_ACCENT, size=Pt(9.5))
p5 = cell.add_paragraph()
add_run(p5, 'レース間が約2時間と短いため、固形物は避けてゼリー・ドリンクに限定する。'
        '予選直後にすみやかにゼリーで糖質を補充し、あとは水分補給のみ。'
        '決勝の招集（17:40）の15分前（17:25頃）から摂取しない。',
        size=Pt(9.5), color=TEXT_COLOR)

p6 = cell.add_paragraph()
add_run(p6, '【消化負担を減らすために】', bold=True, color=GOLD_ACCENT, size=Pt(9.5))
p7 = cell.add_paragraph()
add_run(p7, '食物繊維の多い食材（玄米・ゴボウ・こんにゃく・きのこ類）、脂質の多いもの（揚げ物・マヨネーズ・チョコレート）'
        'は前日夕食〜当日レース前は避ける。白米・バナナ・ゼリーなど消化の速い食材に絞る。',
        size=Pt(9.5), color=TEXT_COLOR)

p8 = cell.add_paragraph()
add_run(p8, '【試合当日に試してはいけないもの】', bold=True, color=RED_ACCENT, size=Pt(9.5))
p9 = cell.add_paragraph()
add_run(p9, '初めて食べる食品・サプリメント・スポーツ製品は使用しない。'
        '事前に練習で試したことのあるものだけを選ぶ。',
        size=Pt(9.5), color=TEXT_COLOR)

p10 = cell.add_paragraph()
add_run(p10, '【普段の食事との違い】', bold=True, color=GOLD_ACCENT, size=Pt(9.5))
p11 = cell.add_paragraph()
add_run(p11, '普段食べているサケ・白米・ヨーグルト・サラダをベースに、当日レース前はサラダ（生野菜）を減らし、'
        '消化の良い食材に絞る。チョコレート・豆乳は当日レース前は避ける。',
        size=Pt(9.5), color=TEXT_COLOR)

# ========================================
# DETAILED NUTRITION TABLE
# ========================================
doc.add_paragraph()
dh = doc.add_paragraph()
add_run(dh, '食事パターンとエネルギー・糖質量（詳細）', bold=True, color=BLUE_TITLE, size=Pt(11))

detail_data = [
    ('前日夕食', '主食', '白米 250g', '375', '92'),
    ('', '主菜', '生姜焼き（豚肉、玉ねぎ）', '250', '10'),
    ('', '副菜', 'ブロッコリー', '30', '5'),
    ('', '副菜', 'サラダ（レタス、トマト、たまご、鶏肉）', '180', '8'),
    ('', '乳製品', 'ヨーグルト', '80', '12'),
    ('', '果物', 'ゴールドキウイ', '50', '10'),
    ('', '', '合計', '965', '137'),
    ('前日補食', '間食', '焼き芋 小1本', '200', '48'),
    ('', '', '合計', '200', '48'),
    ('当日朝食', '主食', '白米 250g', '375', '92'),
    ('', '主菜', 'サケ 1切れ', '130', '0'),
    ('', '汁物', '味噌汁（豆腐、ネギ）', '50', '5'),
    ('', '副菜', 'たまご焼き 1個分', '100', '1'),
    ('', '乳製品', 'ヨーグルト', '80', '12'),
    ('', '果物', 'ゴールドキウイ', '50', '10'),
    ('', '', '合計', '785', '120'),
    ('午前 間食', '果物', 'バナナ 1本', '100', '25'),
    ('', '乳製品', 'ヨーグルト or 豆乳', '80', '8'),
    ('', '', '合計', '180', '33'),
    ('当日昼食', '主食', '白米 250〜300g', '375', '92'),
    ('', '主菜', 'サケ or 鶏肉ソテー', '150', '2'),
    ('', '汁物', '味噌汁', '40', '5'),
    ('', '副菜', 'サラダ（レタス、トマト）', '30', '5'),
    ('', '', '合計', '595', '104'),
    ('当日補食', '補食①', 'おにぎり1個＋ゼリー', '280', '65'),
    ('', 'アップ中', 'スポーツドリンク', '60', '15'),
    ('', '', '合計', '340', '80'),
    ('レース間', '回復補給', 'エネルギーゼリー', '180', '45'),
    ('', 'アップ中', 'スポーツドリンク', '40', '10'),
    ('', '', '合計', '220', '55'),
]

num_detail = len(detail_data)
dt = doc.add_table(rows=num_detail + 2, cols=5)
dt.alignment = WD_TABLE_ALIGNMENT.CENTER

detail_widths = [1800, 1400, 2800, 1200, 1200]
for row in dt.rows:
    for i, w in enumerate(detail_widths):
        set_col_width(row.cells[i], w)

# Header
merge_row_cells(dt, 0, 0, 4)
cell = dt.cell(0, 0)
set_cell_shading(cell, DARK_BLUE)
p = cell.paragraphs[0]
add_run(p, '食事パターンとエネルギー・糖質量（詳細）', bold=True, color=WHITE, size=Pt(10))

# Sub header
for i, txt in enumerate(['', '', '', 'エネルギー', '糖質']):
    p = dt.rows[1].cells[i].paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(p, txt, bold=True, size=Pt(9), color=TEXT_COLOR)
    set_cell_shading(dt.rows[1].cells[i], 'D5D8DC')

# Data
for idx, (section, cat, food, energy, carb) in enumerate(detail_data):
    row_idx = idx + 2
    cells = dt.rows[row_idx].cells
    is_total = food == '合計'
    bg = 'F2F3F4' if is_total else 'FFFFFF'
    for j in range(5):
        set_cell_shading(cells[j], bg)
    for j, txt in enumerate([section, cat, food, energy, carb]):
        p = cells[j].paragraphs[0]
        if j >= 3:
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        add_run(p, txt, size=Pt(9), color=TEXT_COLOR, bold=is_total)

# ========================================
# SAVE
# ========================================
output_path = '/home/user/AK/布勢スプリント2026_食事プラン_0712.docx'
doc.save(output_path)
print(f'Saved: {output_path}')
