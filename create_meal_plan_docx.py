from docx import Document
from docx.shared import Pt, Cm, Emu, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
import copy

doc = Document()

# Page setup (A4, narrow margins like original)
section = doc.sections[0]
section.page_width = Emu(7772400)
section.page_height = Emu(10058400)
section.left_margin = Emu(685800)
section.right_margin = Emu(685800)
section.top_margin = Emu(685800)
section.bottom_margin = Emu(685800)

# Font name - use available font (original used ヒラギノ丸ゴ Pro W4 which is Mac-only)
FONT_NAME = 'ヒラギノ丸ゴ Pro W4'
FONT_NAME_FALLBACK = 'Yu Gothic'

# Colors
DARK_BLUE = '1A5276'
DARK_BG = '1B2631'
LIGHT_BLUE_ROW = 'EBF5FB'
LIGHT_GREEN_ROW = 'EAFAF1'
LIGHT_ORANGE_ROW = 'FEF5E7'
LIGHT_PINK_ROW = 'FDEDEC'
SUMMARY_BG = 'EAF2FF'
POINTS_BG = 'FEF9E7'
TEXT_COLOR = RGBColor(0x2C, 0x3E, 0x50)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
RED_ACCENT = RGBColor(0x92, 0x2B, 0x21)
GOLD_ACCENT = RGBColor(0x7D, 0x66, 0x08)
GRAY_TEXT = RGBColor(0x7F, 0x8C, 0x8D)
BLUE_TITLE = RGBColor(0x1A, 0x52, 0x76)
RACE_BG = 'F5B7B1'  # light red for race rows
RECOVERY_BG = 'D5F5E3'  # light green for recovery section

def set_cell_shading(cell, color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_border(cell, **kwargs):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = tcPr.find(qn('w:tcBorders'))
    if tcBorders is None:
        tcBorders = parse_xml(f'<w:tcBorders {nsdecls("w")}/>')
        tcPr.append(tcBorders)
    for edge, val in kwargs.items():
        element = tcBorders.find(qn(f'w:{edge}'))
        if element is None:
            element = parse_xml(f'<w:{edge} {nsdecls("w")} w:val="{val.get("val","single")}" w:sz="{val.get("sz","4")}" w:space="0" w:color="{val.get("color","BDC3C7")}"/>')
            tcBorders.append(element)

def add_run(paragraph, text, font_name=FONT_NAME, size=Pt(9.5), bold=False, color=TEXT_COLOR):
    run = paragraph.add_run(text)
    run.font.name = font_name
    run.font.size = size
    run.font.bold = bold
    if color:
        run.font.color.rgb = color
    # Set East Asian font
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
    """Merge cells in a row horizontally."""
    table.cell(row_idx, start_col).merge(table.cell(row_idx, end_col))

def add_section_header(table, row_idx, text, bg_color=DARK_BG):
    """Add a dark section header spanning all columns."""
    merge_row_cells(table, row_idx, 0, 4)
    cell = table.cell(row_idx, 0)
    set_cell_shading(cell, bg_color)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    add_run(p, text, bold=True, color=WHITE, size=Pt(10))
    set_row_height(table.rows[row_idx], 350)

def add_content_row(table, row_idx, time_str, timing, food_items, carb, point, bg_color=LIGHT_BLUE_ROW, row_height=800):
    """Add a content row with food details."""
    cells = table.rows[row_idx].cells

    for i in range(5):
        set_cell_shading(cells[i], bg_color)

    # Time
    p = cells[0].paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(p, time_str, size=Pt(9.5), color=TEXT_COLOR)

    # Timing
    p = cells[1].paragraphs[0]
    add_run(p, timing, size=Pt(9.5), bold=True, color=TEXT_COLOR)

    # Food content
    p = cells[2].paragraphs[0]
    for j, item in enumerate(food_items):
        if j > 0:
            add_run(p, '\n', size=Pt(9.5))
        is_note = item.startswith('※') or item.startswith('(')
        add_run(p, item, size=Pt(9), color=GRAY_TEXT if is_note else TEXT_COLOR,
                bold=False)

    # Carb amount
    p = cells[3].paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(p, carb, size=Pt(9.5), bold=True, color=TEXT_COLOR)

    # Point
    p = cells[4].paragraphs[0]
    add_run(p, point, size=Pt(9), color=TEXT_COLOR)

    set_row_height(table.rows[row_idx], row_height)

def add_race_row(table, row_idx, time_str, text):
    """Add a race start row."""
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

def add_no_intake_row(table, row_idx, time_str, label):
    """Add a 'no intake' row before race."""
    cells = table.rows[row_idx].cells
    merge_row_cells(table, row_idx, 2, 4)

    for i in range(5):
        set_cell_shading(cells[i], LIGHT_BLUE_ROW)

    p = cells[0].paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(p, time_str, size=Pt(9.5), color=TEXT_COLOR)

    p = cells[1].paragraphs[0]
    add_run(p, label, size=Pt(9.5), bold=True, color=TEXT_COLOR)

    cell = table.cell(row_idx, 2)
    p = cell.paragraphs[0]
    add_run(p, f'{time_str}は摂取しない', size=Pt(9), color=GRAY_TEXT)

    set_row_height(table.rows[row_idx], 280)

# ========================================
# TITLE
# ========================================
h1 = doc.add_heading(level=1)
h1.alignment = WD_ALIGN_PARAGRAPH.LEFT
add_run(h1, '　前日夜〜試合当日 食事・補食プラン', size=Pt(16), bold=True, color=TEXT_COLOR)

# Subtitle
h2 = doc.add_heading(level=2)
h2.alignment = WD_ALIGN_PARAGRAPH.LEFT
add_run(h2, '普段のスタイルを活かした試合食　｜　体重64kg　糖質目標 5〜6g/kg', size=Pt(12), color=TEXT_COLOR)

# Intro paragraph
intro = doc.add_paragraph()
intro_text = (
    '100mに2本出場するため、朝食でしっかりエネルギーを蓄え、レース間は消化の良い補食で'
    'つないでいきましょう。普段から食べ慣れているサケ・白米・サラダ・ヨーグルトを中心に、'
    '試合当日は脂質を控えめにし、糖質をしっかり摂るプランです。'
    '前日は筋グリコーゲンの貯蔵を意識して、白米を多めにしましょう。'
)
add_run(intro, intro_text, size=Pt(10), color=TEXT_COLOR)

# ========================================
# MAIN TABLE
# ========================================
# Total rows needed:
# 0: Header
# 1: 前日 section header
# 2: 前日夕食
# 3: 前日補食（任意）
# 4: 当日 section header
# 5: 起床・水分補給
# 6: 朝食
# 7: 補食①
# 8: ウォームアップ中
# 9: 招集前（摂取しない）
# 10: 1本目レーススタート
# 11: レース間セクションヘッダー
# 12: レース直後回復
# 13: 補食②
# 14: ウォームアップ中（2本目）
# 15: 招集前（摂取しない）
# 16: 2本目レーススタート

NUM_ROWS = 17
table = doc.add_table(rows=NUM_ROWS, cols=5)
table.alignment = WD_TABLE_ALIGNMENT.CENTER

# Column widths
col_widths = [919, 1521, 2934, 902, 3788]
for row in table.rows:
    for i, w in enumerate(col_widths):
        set_col_width(row.cells[i], w)

# Row 0: Header
header_labels = ['時間', 'タイミング', '食事・補食内容', '糖質量', '目的・ポイント']
for i, label in enumerate(header_labels):
    cell = table.cell(0, i)
    set_cell_shading(cell, DARK_BLUE)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(p, label, bold=True, color=WHITE, size=Pt(10))
set_row_height(table.rows[0], 521)

# Row 1: 前日セクション
add_section_header(table, 1, '前日　布勢スプリント2026', DARK_BG)

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
    'できれば就寝2時間前までに。就寝直前の摂取は翌朝の胃もたれにつながるため避ける。十分な睡眠を確保する。',
    LIGHT_BLUE_ROW, 651)

# Row 4: 当日セクション
add_section_header(table, 4,
    '試合当日　①100m 招集9:20 / 競技開始9:40　②100m 招集12:20 / 競技開始12:40',
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
    '6:00〜\n6:30',
    '朝食\n（1本目\n約3.5時間前）',
    [
        '白米 250g',
        'サケ 1切れ',
        '味噌汁（豆腐、ネギ）',
        'たまご焼き 1個分',
        'ヨーグルト',
        'ゴールドキウイ',
    ],
    '約110g',
    '普段の朝食に近い内容で安心感を持たせる。白米をしっかり食べてエネルギーを蓄える。'
    '消化しやすい食材のみを選ぶ。脂質は最小限に。食べ慣れたものだけにする。',
    LIGHT_GREEN_ROW, 985)

# Row 7: 補食①
add_content_row(table, 7,
    '8:00〜\n8:30',
    '補食①\n（1本目\n約1〜1.5時間前）',
    [
        'バナナ 1本',
        'エネルギーゼリー 1個',
        '(到着時〜アップ前)',
    ],
    '約50g',
    '胃への負担を抑えるためゼリーやバナナを選ぶ。固形物を食べる場合は少量ずつよく噛んで食べる。',
    LIGHT_GREEN_ROW, 765)

# Row 8: ウォームアップ中
add_content_row(table, 8,
    '〜9:05',
    'ウォーム\nアップ中',
    [
        'スポーツドリンク 少量ずつ',
        '(150〜200ml)',
    ],
    '約10〜15g',
    '一気飲みせず少量ずつ補給する。体温に注意しながら水分・電解質を維持する。',
    LIGHT_GREEN_ROW, 736)

# Row 9: 招集前
add_no_intake_row(table, 9, '9:05〜9:20', '100m 招集')

# Row 10: 1本目レース
add_race_row(table, 10, '9:40', '🏃 第1レース 100m スタート')

# Row 11: レース間セクション
add_section_header(table, 11,
    'レース間 回復タイム　（約3時間　9:40〜12:20）',
    DARK_BLUE)

# Row 12: レース直後
add_content_row(table, 12,
    '9:50〜\n10:00',
    'レース直後\n回復補給',
    [
        '水分補給',
        'おにぎり 1個（鮭 or 梅）',
        '(時間に余裕があるため固形物もOK)',
    ],
    '約40g',
    'レース間が約3時間あるため、固形物の消化も十分間に合う。'
    'おにぎりで糖質をしっかり補給する。水分もこまめに摂る。',
    LIGHT_ORANGE_ROW, 800)

# Row 13: 補食②
add_content_row(table, 13,
    '10:00〜\n10:30',
    '補食②\n（2本目\n約2時間前）',
    [
        'バナナ 1本',
        'スポーツドリンク',
        '※10:50頃までには食べ終える',
    ],
    '約30〜35g',
    '2本目の招集（12:20）の1.5時間前までに食べ終える。'
    '消化しやすいものに限定する。胃の重さが残らないよう少量ずつ。',
    LIGHT_ORANGE_ROW, 800)

# Row 14: ウォームアップ（2本目）
add_content_row(table, 14,
    '11:00〜',
    'ウォーム\nアップ中',
    [
        'スポーツドリンク 少量ずつ',
        '(100〜150ml)',
        '※固形物は摂らない',
    ],
    '約6〜10g',
    '軽いストレッチ・アップで回復を促進する。この時間に固形物を摂ると'
    '2本目スタート時に胃の重さが残るため避ける。水分補給はこまめに。',
    LIGHT_ORANGE_ROW, 736)

# Row 15: 招集前
add_no_intake_row(table, 15, '12:05〜12:20', '100m 招集')

# Row 16: 2本目レース
add_race_row(table, 16, '12:40', '🏃 第2レース 100m スタート')

# ========================================
# SUMMARY BOX (Table 1)
# ========================================
doc.add_paragraph()  # spacer

summary_table = doc.add_table(rows=1, cols=1)
summary_table.alignment = WD_TABLE_ALIGNMENT.CENTER
cell = summary_table.cell(0, 0)
set_cell_shading(cell, SUMMARY_BG)

p = cell.paragraphs[0]
add_run(p, '当日 糖質・水分まとめ（体重64kg）', bold=True, color=BLUE_TITLE, size=Pt(11))

p2 = cell.add_paragraph()
add_run(p2, '【前日夜】　夕食：約130g　就寝前補食（任意）：約40〜50g', size=Pt(9.5), color=TEXT_COLOR)

p3 = cell.add_paragraph()
add_run(p3, '【当日 朝〜1本目前】　朝食：約110g　補食①：約50g　ウォームアップ中：約10〜15g', size=Pt(9.5), color=TEXT_COLOR)

p4 = cell.add_paragraph()
add_run(p4, '【レース間〜2本目前】　回復補給：約40g　補食②：約30〜35g　ウォームアップ中：約6〜10g', size=Pt(9.5), color=TEXT_COLOR)

p5 = cell.add_paragraph()
add_run(p5, '▶ 前日 糖質トータル：約170〜180g', bold=True, color=RED_ACCENT, size=Pt(9.5))

p6 = cell.add_paragraph()
add_run(p6, '▶ 当日 糖質トータル：約250〜270g（夕食含まず）', bold=True, color=RED_ACCENT, size=Pt(9.5))

p7 = cell.add_paragraph()
add_run(p7, '※ 前日〜当日の目標：体重64kg × 5〜6g = 320〜384g/日 → 前日夕食＋当日合計で達成', size=Pt(9), color=GRAY_TEXT)

# ========================================
# POINTS BOX (Table 2)
# ========================================
doc.add_paragraph()

points_table = doc.add_table(rows=1, cols=1)
points_table.alignment = WD_TABLE_ALIGNMENT.CENTER
cell = points_table.cell(0, 0)
set_cell_shading(cell, POINTS_BG)

p = cell.paragraphs[0]
add_run(p, '食事・補食のポイント', bold=True, color=BLUE_TITLE, size=Pt(11))

p2 = cell.add_paragraph()
add_run(p2, '【消化負担を減らすために】', bold=True, color=GOLD_ACCENT, size=Pt(9.5))
p3 = cell.add_paragraph()
add_run(p3, '食物繊維の多い食材（玄米・ゴボウ・こんにゃく・きのこ類）、脂質の多いもの（揚げ物・マヨネーズ・チョコレート）は前日夕食〜当日レース前は避ける。白米・バナナ・ゼリーなど消化の速い食材に絞る。', size=Pt(9.5), color=TEXT_COLOR)

p4 = cell.add_paragraph()
add_run(p4, '【レース間の補食タイミング】', bold=True, color=GOLD_ACCENT, size=Pt(9.5))
p5 = cell.add_paragraph()
add_run(p5, '1本目→2本目のレース間は約3時間あるため、固形物（おにぎり）も十分消化可能。ただし2本目の招集（12:20）の1.5時間前（10:50頃）までに食べ終える。', size=Pt(9.5), color=TEXT_COLOR)

p6 = cell.add_paragraph()
add_run(p6, '【試合当日に試してはいけないもの】', bold=True, color=RED_ACCENT, size=Pt(9.5))
p7 = cell.add_paragraph()
add_run(p7, '初めて食べる食品・サプリメント・スポーツ製品は使用しない。事前に練習で試したことのあるものだけを選ぶ。', size=Pt(9.5), color=TEXT_COLOR)

p8 = cell.add_paragraph()
add_run(p8, '【普段の食事との違い】', bold=True, color=GOLD_ACCENT, size=Pt(9.5))
p9 = cell.add_paragraph()
add_run(p9, '普段食べているサケ・白米・ヨーグルト・サラダをベースに、当日レース前はサラダ（生野菜）を減らし、消化の良い食材に絞る。チョコレート・豆乳は当日レース前は避ける。', size=Pt(9.5), color=TEXT_COLOR)

# ========================================
# DETAILED NUTRITION TABLE (Table 3)
# ========================================
doc.add_paragraph()

detail_heading = doc.add_paragraph()
add_run(detail_heading, '食事パターンとエネルギー・糖質量（詳細）', bold=True, color=BLUE_TITLE, size=Pt(11))

detail_table = doc.add_table(rows=24, cols=5)
detail_table.alignment = WD_TABLE_ALIGNMENT.CENTER

detail_widths = [1800, 1400, 2800, 1200, 1200]
for row in detail_table.rows:
    for i, w in enumerate(detail_widths):
        set_col_width(row.cells[i], w)

# Header for detail table
detail_header_row = detail_table.rows[0]
merge_row_cells(detail_table, 0, 0, 4)
cell = detail_table.cell(0, 0)
set_cell_shading(cell, DARK_BLUE)
p = cell.paragraphs[0]
add_run(p, '食事パターンとエネルギー・糖質量（詳細）', bold=True, color=WHITE, size=Pt(10))

# Sub header
cells = detail_table.rows[1].cells
for i, txt in enumerate(['', '', '', 'エネルギー', '糖質']):
    p = cells[i].paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(p, txt, bold=True, size=Pt(9), color=TEXT_COLOR)
    set_cell_shading(cells[i], 'D5D8DC')

# Data rows
detail_data = [
    # (section, category, food, energy, carb)
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
    ('当日補食', '補食①', 'バナナ1本＋ゼリー', '200', '50'),
    ('', 'アップ中', 'スポーツドリンク', '60', '15'),
    ('', '', '合計', '260', '65'),
    ('レース間', '回復補給', 'おにぎり1個＋バナナ', '280', '65'),
    ('', 'アップ中', 'スポーツドリンク', '40', '10'),
    ('', '', '合計', '320', '75'),
]

for i, (section, cat, food, energy, carb) in enumerate(detail_data):
    row_idx = i + 2
    cells = detail_table.rows[row_idx].cells

    is_total = food == '合計'
    bg = 'F2F3F4' if is_total else 'FFFFFF'

    for j in range(5):
        set_cell_shading(cells[j], bg)

    for j, txt in enumerate([section, cat, food, energy, carb]):
        p = cells[j].paragraphs[0]
        if j >= 3:
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        add_run(p, txt, size=Pt(9), color=TEXT_COLOR, bold=is_total)

# Save
output_path = '/home/user/AK/布勢スプリント2026_食事プラン.docx'
doc.save(output_path)
print(f'Saved: {output_path}')
