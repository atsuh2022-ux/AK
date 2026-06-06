from docx import Document
from docx.shared import Pt, RGBColor, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

doc = Document()

# ページ設定（A4）
section = doc.sections[0]
section.page_width = Cm(21)
section.page_height = Cm(29.7)
section.left_margin = Cm(1.5)
section.right_margin = Cm(1.5)
section.top_margin = Cm(1.5)
section.bottom_margin = Cm(1.5)

# カラー定義
COLOR_DARK_ORANGE = RGBColor(0xC0, 0x50, 0x10)   # タイトル背景
COLOR_ORANGE = RGBColor(0xE8, 0x6A, 0x20)          # セクションヘッダー
COLOR_LIGHT_ORANGE = RGBColor(0xFF, 0xE5, 0xCC)    # 薄いオレンジ
COLOR_AMBER = RGBColor(0xF5, 0xA6, 0x23)           # 補色ヘッダー
COLOR_RACE1 = RGBColor(0x1A, 0x6B, 0xB8)           # 1日目 青
COLOR_RACE1_LIGHT = RGBColor(0xD6, 0xE8, 0xF8)     # 1日目 薄青
COLOR_RACE2 = RGBColor(0x27, 0x8A, 0x3E)           # 2日目 緑
COLOR_RACE2_LIGHT = RGBColor(0xD4, 0xEF, 0xDA)     # 2日目 薄緑
COLOR_GRAY = RGBColor(0x80, 0x80, 0x80)
COLOR_WHITE = RGBColor(0xFF, 0xFF, 0xFF)
COLOR_LIGHT_GRAY = RGBColor(0xF5, 0xF5, 0xF5)
COLOR_TABLE_HEADER = RGBColor(0x5A, 0x5A, 0x5A)
COLOR_PREV_DAY = RGBColor(0x6A, 0x4A, 0xAA)        # 前日 紫
COLOR_PREV_DAY_LIGHT = RGBColor(0xEA, 0xE0, 0xFF)  # 前日 薄紫
COLOR_RECOVERY = RGBColor(0xD3, 0x20, 0x00)

def set_cell_bg(cell, rgb):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    hex_color = '%02X%02X%02X' % (rgb[0], rgb[1], rgb[2])
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def set_cell_bg_from_rgb(cell, rgb_color):
    set_cell_bg(cell, (rgb_color[0], rgb_color[1], rgb_color[2]))

def set_paragraph_spacing(para, before=0, after=0, line_spacing=None):
    pPr = para._p.get_or_add_pPr()
    spacing = OxmlElement('w:spacing')
    spacing.set(qn('w:before'), str(before))
    spacing.set(qn('w:after'), str(after))
    if line_spacing:
        spacing.set(qn('w:line'), str(line_spacing))
        spacing.set(qn('w:lineRule'), 'auto')
    pPr.append(spacing)

def add_run(para, text, bold=False, size=10, color=None, italic=False):
    run = para.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    if color:
        run.font.color.rgb = color
    run.italic = italic
    return run

def set_cell_margins(cell, top=50, bottom=50, left=80, right=80):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for side, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{side}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def merge_cells_horizontal(table, row_idx, start_col, end_col):
    row = table.rows[row_idx]
    for col in range(start_col + 1, end_col + 1):
        row.cells[col].merge(row.cells[start_col])

def set_col_width(table, col_idx, width_cm):
    for row in table.rows:
        row.cells[col_idx].width = Cm(width_cm)

# ==================== タイトルセクション ====================
title_table = doc.add_table(rows=1, cols=1)
title_table.alignment = WD_TABLE_ALIGNMENT.CENTER
title_cell = title_table.rows[0].cells[0]
set_cell_bg_from_rgb(title_cell, COLOR_DARK_ORANGE)
set_cell_margins(title_cell, top=120, bottom=80, left=200, right=200)

p = title_cell.paragraphs[0]
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_run(p, '　試合当日 食事・補食プラン　', bold=True, size=16, color=COLOR_WHITE)

doc.add_paragraph()

# サブタイトル
sub_p = doc.add_paragraph()
sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_paragraph_spacing(sub_p, before=0, after=60)
add_run(sub_p, '消化負担ゼロ・レース間の素早い回復　｜　体重61kg　糖質目標 8g/kg', bold=True, size=10, color=COLOR_DARK_ORANGE)

# 説明文
desc_p = doc.add_paragraph()
set_paragraph_spacing(desc_p, before=0, after=80)
add_run(desc_p, '6/13（金）400m・6/14（土）100mの2日間構成です。各レース日に合わせた補食プランを実行しましょう。朝食はホテルビュッフェでしっかり食べ、昼食・夕食はコンビニ・スーパー・外食から消化しやすいメニューを選びましょう。', size=9)

# ==================== メイン食事スケジュール表 ====================
COLS = 5
table = doc.add_table(rows=0, cols=COLS)
table.style = 'Table Grid'
table.alignment = WD_TABLE_ALIGNMENT.CENTER

def add_header_row(table, texts, bg_color, text_color=None, font_size=9):
    row = table.add_row()
    tc = None
    for i, text in enumerate(texts):
        cell = row.cells[i]
        set_cell_bg_from_rgb(cell, bg_color)
        set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        clr = text_color if text_color else COLOR_WHITE
        add_run(p, text, bold=True, size=font_size, color=clr)
    return row

def add_section_header(table, text, bg_color, text_color=None):
    row = table.add_row()
    for i in range(1, COLS):
        row.cells[0].merge(row.cells[i])
    cell = row.cells[0]
    set_cell_bg_from_rgb(cell, bg_color)
    set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    clr = text_color if text_color else COLOR_WHITE
    add_run(p, text, bold=True, size=10, color=clr)
    return row

def add_data_row(table, col0, col1, col2, col3, col4,
                 bg=None, bold_col0=False, align_center_col0=True,
                 row_color=None, italic_col2=False):
    row = table.add_row()
    data = [col0, col1, col2, col3, col4]
    aligns = [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER,
              WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER,
              WD_ALIGN_PARAGRAPH.LEFT]
    bolds = [bold_col0, False, False, False, False]
    for i, (text, align, bold) in enumerate(zip(data, aligns, bolds)):
        cell = row.cells[i]
        if bg:
            set_cell_bg_from_rgb(cell, bg)
        elif row_color:
            set_cell_bg_from_rgb(cell, row_color)
        set_cell_margins(cell, top=50, bottom=50, left=80, right=80)
        p = cell.paragraphs[0]
        p.alignment = align
        add_run(p, text, bold=bold, size=8.5)
    return row

def add_race_row(table, time_text, bg_color):
    row = table.add_row()
    for i in range(1, COLS):
        row.cells[0].merge(row.cells[i])
    cell = row.cells[0]
    set_cell_bg_from_rgb(cell, bg_color)
    set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(p, time_text, bold=True, size=11, color=COLOR_WHITE)
    return row

def add_no_intake_row(table, time_text, bg_color=None):
    row = table.add_row()
    for i in range(1, COLS):
        row.cells[0].merge(row.cells[i])
    cell = row.cells[0]
    if bg_color:
        set_cell_bg_from_rgb(cell, bg_color)
    else:
        set_cell_bg_from_rgb(cell, RGBColor(0xEE, 0xEE, 0xEE))
    set_cell_margins(cell, top=50, bottom=50, left=120, right=120)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(p, time_text, bold=False, size=8.5, color=COLOR_GRAY)
    return row

# テーブルヘッダー
add_header_row(table,
    ['時間', 'タイミング', '食事・補食内容', '糖質量', '目的・ポイント'],
    COLOR_TABLE_HEADER)

# ========== 前日（木曜日）6/12 ==========
add_section_header(table,
    '　前日（木曜日）6/12　ホテルチェックイン後',
    COLOR_PREV_DAY)

add_data_row(table,
    '18:00〜\n21:00',
    '前日\n夕食',
    '白飯200g\n焼き魚\n野菜の炒め物\nインスタント味噌汁',
    '約120g',
    '翌日に向けてグリコーゲンをしっかり蓄える。早めに食べて消化時間を十分に確保する。野菜は柔らかく調理した食材を選び、生野菜や脂質・食物繊維の多い食材は避ける。',
    row_color=COLOR_PREV_DAY_LIGHT)

add_data_row(table,
    '就寝前\n（任意）',
    '補食\n（空腹時）',
    '和菓子や糖質多めのドリンク\n※空腹でなければ無理して摂取しない',
    '約40〜\n50g',
    'できれば就寝2時間前までに。就寝直前の摂取は翌朝の胃もたれにつながるため避ける。十分な睡眠を確保する。')

# ========== 試合1日目（金曜日）6/13 400m 15:10 ==========
add_section_header(table,
    '　試合1日目（金曜日）6/13　400m　招集14:35 / 招集終了14:50 / レース15:10',
    COLOR_RACE1)

add_data_row(table,
    '起床',
    '水分補給',
    '水200〜250ml（ゆっくり）',
    '0g',
    '起床後すぐに水分補給で体内の水分バランスを整える。体調を確認する。')

add_data_row(table,
    '7:00〜\n7:30',
    '朝食\n（ホテルビュッフェ）\n（レース 約8時間前）',
    'おにぎり2個またはご飯\nたまご料理\n野菜料理（柔らかく調理）\nバナナ1本\n味噌汁',
    '約120〜\n140g',
    '2日間のレースを見据えてしっかりエネルギーを蓄える。消化しやすい食材のみを選ぶ。脂質・食物繊維の多いものは避ける。ホテルビュッフェで食べ慣れたものを選ぶ。',
    row_color=COLOR_RACE1_LIGHT)

add_data_row(table,
    '11:30〜\n12:00',
    '昼食\n（コンビニ・外食）\n（レース 約3時間前）',
    'うどんまたはおにぎり2個\nバナナ1本\nスポーツドリンク',
    '約80〜\n100g',
    'レース前最後の固形食。消化しやすく脂質・食物繊維が少ないものを選ぶ。うどん・おにぎり・バナナが理想的。揚げ物・サラダ・生野菜は避ける。')

add_data_row(table,
    '13:30〜\n14:00',
    '補食①\n（レース 約1〜1.5時間前）',
    'エネルギーゼリーorおにぎり1個\n（少量）',
    '約30〜\n40g',
    '胃への負担を抑えるためゼリーを優先。固形物を食べる場合は少量ずつよく噛んで食べる。',
    row_color=COLOR_RACE1_LIGHT)

add_data_row(table,
    '〜14:20',
    'ウォームアップ中',
    'スポーツドリンク 少量ずつ\n（150〜200ml）',
    '約10〜\n15g',
    '一気飲みせず少量ずつ補給する。体温に注意しながら水分・電解質を維持する。')

add_no_intake_row(table, '14:35　400m 招集　（14:20〜14:35は摂取しない）')

add_data_row(table,
    '14:50〜\n15:10',
    '招集終了〜\nレース待機\n（任意補食）',
    '羊羹orタブレット\n※アップ中でもok',
    '約10g',
    '摂取できる環境であれば補給する。摂取できない場合は無理をしなくてよい。',
    row_color=COLOR_RACE1_LIGHT)

add_race_row(table, '🏃 試合1日目　400m　15:10 スタート', COLOR_RACE1)

add_data_row(table,
    '〜15:40',
    'レース直後\n回復補給',
    'エネルギーゼリー1個\n水またはスポーツドリンク\n（なるべく早いタイミングで）',
    '約30〜\n45g',
    '消耗した糖質をすみやかに補充する。少量ずつゆっくり摂取する。固形物はゼリー・ドリンクを優先する。')

add_data_row(table,
    '18:00〜\n19:00',
    '夕食\n（翌日の100mに備えて）\nコンビニ・外食',
    '白飯200g\n焼き魚またはサラダチキン\n野菜料理（柔らかく調理）\nインスタント味噌汁',
    '約120g',
    '翌日のレースに向けてグリコーゲンをしっかり回復・蓄積する。消化しやすい食材を選び、脂質・食物繊維の多いものは避ける。早めに食べて消化時間を確保する。',
    row_color=COLOR_RACE1_LIGHT)

add_data_row(table,
    '就寝前\n（任意）',
    '補食\n（空腹時）',
    '和菓子や糖質多めのドリンク\n※空腹でなければ無理して摂取しない',
    '約40〜\n50g',
    '翌日100mに向けて追加の糖質補充。できれば就寝2時間前までに。十分な睡眠を確保する。')

# ========== 試合2日目（土曜日）6/14 100m 12:18 ==========
add_section_header(table,
    '　試合2日目（土曜日）6/14　100m　招集11:48 / 招集終了12:03 / レース12:18',
    COLOR_RACE2)

add_data_row(table,
    '起床',
    '水分補給',
    '水200〜250ml（ゆっくり）',
    '0g',
    '起床後すぐに水分補給で体内の水分バランスを整える。体調を確認する。',
    row_color=COLOR_RACE2_LIGHT)

add_data_row(table,
    '7:00〜\n7:30',
    '朝食\n（ホテルビュッフェ）\n（レース 約5時間前）',
    'おにぎり1個またはご飯\nバナナ1本\nフルーツヨーグルト\nオレンジジュース',
    '約90〜\n110g',
    '100mに備えてエネルギーをしっかり蓄える。消化しやすい食材のみを選ぶ。脂質・タンパク質は最小限に。食べ慣れたものだけにする。')

add_data_row(table,
    '10:00〜\n10:30',
    '補食①\n（レース 約2時間前）\n到着時〜アップ前',
    'エネルギーゼリーorおにぎり1個',
    '約40g',
    '胃への負担を抑えるためゼリーや具の少ないおにぎりを選ぶ。固形物を食べる場合は少量ずつよく噛んで食べる。',
    row_color=COLOR_RACE2_LIGHT)

add_data_row(table,
    '〜11:30',
    'ウォームアップ中',
    'スポーツドリンク 少量ずつ\n（150〜200ml）',
    '約10〜\n15g',
    '一気飲みせず少量ずつ補給する。体温に注意しながら水分・電解質を維持する。')

add_no_intake_row(table, '11:48　100m 招集　（11:33〜11:48は摂取しない）')

add_data_row(table,
    '12:03〜\n12:18',
    '招集終了〜\nレース待機\n（任意補食）',
    '羊羹orタブレット\n※アップ中でもok',
    '約10g',
    '摂取できる環境であれば補給する。摂取できない場合は無理をしなくてよい。',
    row_color=COLOR_RACE2_LIGHT)

add_race_row(table, '🏃 試合2日目　100m　12:18 スタート', COLOR_RACE2)

add_data_row(table,
    '〜12:45',
    'レース直後\n回復補給・昼食',
    'エネルギーゼリー・水分\nその後→好みの昼食（コンビニ・外食）',
    '—',
    'お疲れさまでした！消耗した分をしっかり補充する。好きなものを食べてOK。ただし消化に優しいものから始めると◎')

# 列幅設定
col_widths = [2.0, 2.5, 4.5, 1.8, 6.2]
for row in table.rows:
    for i, width in enumerate(col_widths):
        if i < len(row.cells):
            row.cells[i].width = Cm(width)

doc.add_paragraph()

# ==================== 糖質・水分まとめ ====================
summary_table = doc.add_table(rows=1, cols=1)
summary_table.alignment = WD_TABLE_ALIGNMENT.CENTER
sc = summary_table.rows[0].cells[0]
set_cell_bg_from_rgb(sc, COLOR_LIGHT_ORANGE)
set_cell_margins(sc, top=100, bottom=100, left=150, right=150)

sp = sc.paragraphs[0]
add_run(sp, '【糖質・水分まとめ（体重61kg）】', bold=True, size=10, color=COLOR_DARK_ORANGE)

lines = [
    '【6/12 前日夜】　夕食：約120g　就寝前補食（任意）：約40〜50g',
    '【6/13 試合1日目　400m】　朝食：約120〜140g　昼食：約80〜100g　補食①：約30〜40g　アップ中：約10〜15g　招集前（任意）：約10g　▶ 当日トータル：約〜310g',
    '【6/13 夕食（翌日準備）】　夕食：約120g　就寝前補食（任意）：約40〜50g',
    '【6/14 試合2日目　100m】　朝食：約90〜110g　補食①：約40g　アップ中：約10〜15g　招集前（任意）：約10g　▶ 当日トータル：約〜175g',
    '',
    '※ 試合前1週間の目標：体重61kg × 7〜8g = 427〜488g/日（試合前3〜5日）'
]
for line in lines:
    lp = sc.add_paragraph()
    add_run(lp, line, size=8.5)
    set_paragraph_spacing(lp, before=20, after=20)

doc.add_paragraph()

# ==================== 食事・補食のポイント ====================
point_table = doc.add_table(rows=1, cols=1)
point_table.alignment = WD_TABLE_ALIGNMENT.CENTER
pc = point_table.rows[0].cells[0]
set_cell_bg_from_rgb(pc, RGBColor(0xF0, 0xF0, 0xF0))
set_cell_margins(pc, top=100, bottom=100, left=150, right=150)

pp = pc.paragraphs[0]
add_run(pp, '【食事・補食のポイント】', bold=True, size=10, color=COLOR_DARK_ORANGE)

points = [
    ('【消化負担を減らすために】',
     '食物繊維の多い食材（玄米・ゴボウ・こんにゃく・きのこ類）、脂質の多いもの（揚げ物・マヨネーズ）、生もの、乳製品は前日〜当日は避ける。白米・うどん・バナナなど消化の速い食材に絞る。'),
    ('【摂取タイミングの鉄則】',
     '固形食はなるべくレース2〜3時間前まで。少量ずつゆっくり摂ることで胃の不快感を防ぐ。'),
    ('【試合当日に試してはいけないもの】',
     '初めて食べる食品・サプリメント・スポーツ製品は使用しない。事前に練習で試したことのあるものだけを選ぶ。'),
    ('【2日間を通じて】',
     '6/13のレース後〜6/14の朝食までの食事が100mのパフォーマンスを左右する。夕食と睡眠をしっかり確保しよう。'),
]
for title, body in points:
    bp = pc.add_paragraph()
    add_run(bp, title, bold=True, size=8.5, color=COLOR_DARK_ORANGE)
    add_run(bp, '\n' + body, size=8.5)
    set_paragraph_spacing(bp, before=40, after=20)

doc.add_paragraph()

# ==================== 食事パターン詳細テーブル ====================
detail_heading = doc.add_paragraph()
add_run(detail_heading, '食事パターンとエネルギー・糖質量（詳細）', bold=True, size=10, color=COLOR_DARK_ORANGE)

detail_table = doc.add_table(rows=0, cols=4)
detail_table.style = 'Table Grid'

def add_detail_header(table, texts, bg_color):
    row = table.add_row()
    for i, text in enumerate(texts):
        cell = row.cells[i]
        set_cell_bg_from_rgb(cell, bg_color)
        set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_run(p, text, bold=True, size=8.5, color=COLOR_WHITE)
    return row

def add_detail_row(table, col0, col1, col2, col3, col4=None, bg=None, bold=False):
    if col4 is not None:
        # 5 columns
        pass
    row = table.add_row()
    data = [col0, col1, col2, col3]
    aligns = [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT,
              WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.RIGHT]
    for i, (text, align) in enumerate(zip(data, aligns)):
        cell = row.cells[i]
        if bg:
            set_cell_bg_from_rgb(cell, bg)
        set_cell_margins(cell, top=40, bottom=40, left=80, right=80)
        p = cell.paragraphs[0]
        p.alignment = align
        add_run(p, text, bold=bold, size=8.5)
    return row

def add_section_row_detail(table, text, bg_color):
    row = table.add_row()
    for i in range(1, 4):
        row.cells[0].merge(row.cells[i])
    cell = row.cells[0]
    set_cell_bg_from_rgb(cell, bg_color)
    set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    add_run(p, text, bold=True, size=9, color=COLOR_WHITE)
    return row

add_detail_header(detail_table, ['', '内容', 'エネルギー(kcal)', '糖質(g)'], COLOR_TABLE_HEADER)

# 前日夕食
add_section_row_detail(detail_table, '前日夕食（パターン1）', COLOR_PREV_DAY)
rows_d1 = [
    ('主食', '白飯200g', '300', '70'),
    ('主菜', '焼き魚（鮭など）', '150', '0'),
    ('副菜', '野菜の炒め物', '120', '15'),
    ('汁物', 'インスタント味噌汁', '40', '5'),
    ('', '合計', '610', '90'),
]
for r in rows_d1:
    row = add_detail_row(detail_table, *r)
    if r[0] == '':
        set_cell_bg_from_rgb(row.cells[0], RGBColor(0xEE, 0xEE, 0xEE))
        set_cell_bg_from_rgb(row.cells[1], RGBColor(0xEE, 0xEE, 0xEE))
        set_cell_bg_from_rgb(row.cells[2], RGBColor(0xEE, 0xEE, 0xEE))
        set_cell_bg_from_rgb(row.cells[3], RGBColor(0xEE, 0xEE, 0xEE))
        for cell in row.cells:
            for para in cell.paragraphs:
                for run in para.runs:
                    run.bold = True

add_section_row_detail(detail_table, '前日補食', COLOR_PREV_DAY)
add_detail_row(detail_table, '', '和菓子/ドリンク', '200', '50')
total_row = add_detail_row(detail_table, '', '合計', '200', '50', bg=RGBColor(0xEE, 0xEE, 0xEE))
for cell in total_row.cells:
    for para in cell.paragraphs:
        for run in para.runs:
            run.bold = True

# 6/13 当日食事
add_section_row_detail(detail_table, '6/13 当日 朝食', COLOR_RACE1)
rows_breakfast13 = [
    ('主食', 'おにぎり2個またはご飯', '340', '80'),
    ('主菜', 'たまご料理', '100', '5'),
    ('副菜', '野菜料理（柔らかく調理）', '80', '15'),
    ('果物', 'バナナ1本', '100', '20'),
    ('汁物', '味噌汁', '40', '5'),
    ('', '合計', '660', '125'),
]
for r in rows_breakfast13:
    row = add_detail_row(detail_table, *r)
    if r[0] == '':
        for cell in row.cells:
            set_cell_bg_from_rgb(cell, RGBColor(0xEE, 0xEE, 0xEE))
            for para in cell.paragraphs:
                for run in para.runs:
                    run.bold = True

add_section_row_detail(detail_table, '6/13 当日 昼食（レース3時間前）', COLOR_RACE1)
rows_lunch13 = [
    ('主食', 'うどんまたはおにぎり2個', '360', '75'),
    ('果物', 'バナナ1本', '100', '20'),
    ('飲み物', 'スポーツドリンク', '60', '15'),
    ('', '合計', '520', '110'),
]
for r in rows_lunch13:
    row = add_detail_row(detail_table, *r, bg=COLOR_RACE1_LIGHT)
    if r[0] == '':
        for cell in row.cells:
            set_cell_bg_from_rgb(cell, RGBColor(0xEE, 0xEE, 0xEE))
            for para in cell.paragraphs:
                for run in para.runs:
                    run.bold = True

add_section_row_detail(detail_table, '6/13 当日 補食', COLOR_RACE1)
rows_snack13 = [
    ('補食①', 'ゼリーorおにぎり', '180', '35'),
    ('アップ中', 'スポーツドリンク', '60', '15'),
    ('レース前', '羊羹orタブレット', '40', '10'),
    ('', '合計', '280', '60'),
]
for r in rows_snack13:
    row = add_detail_row(detail_table, *r)
    if r[0] == '':
        for cell in row.cells:
            set_cell_bg_from_rgb(cell, RGBColor(0xEE, 0xEE, 0xEE))
            for para in cell.paragraphs:
                for run in para.runs:
                    run.bold = True

add_section_row_detail(detail_table, '6/13 夕食（翌日準備）', COLOR_RACE1)
rows_dinner13 = [
    ('主食', '白飯200g', '300', '70'),
    ('主菜', '焼き魚またはサラダチキン', '150', '0'),
    ('副菜', '野菜料理（柔らかく調理）', '100', '15'),
    ('汁物', 'インスタント味噌汁', '40', '5'),
    ('', '合計', '590', '90'),
]
for r in rows_dinner13:
    row = add_detail_row(detail_table, *r, bg=COLOR_RACE1_LIGHT)
    if r[0] == '':
        for cell in row.cells:
            set_cell_bg_from_rgb(cell, RGBColor(0xEE, 0xEE, 0xEE))
            for para in cell.paragraphs:
                for run in para.runs:
                    run.bold = True

# 6/14 当日食事
add_section_row_detail(detail_table, '6/14 当日 朝食', COLOR_RACE2)
rows_breakfast14 = [
    ('主食', 'おにぎり1個', '200', '50'),
    ('果物', 'バナナ1本', '100', '20'),
    ('乳製品', 'フルーツヨーグルト', '120', '20'),
    ('補食', 'オレンジジュース', '90', '20'),
    ('', '合計', '510', '110'),
]
for r in rows_breakfast14:
    row = add_detail_row(detail_table, *r)
    if r[0] == '':
        for cell in row.cells:
            set_cell_bg_from_rgb(cell, RGBColor(0xEE, 0xEE, 0xEE))
            for para in cell.paragraphs:
                for run in para.runs:
                    run.bold = True

add_section_row_detail(detail_table, '6/14 当日 補食', COLOR_RACE2)
rows_snack14 = [
    ('補食①', 'ゼリーorおにぎり', '180', '40'),
    ('アップ中', 'スポーツドリンク', '60', '15'),
    ('レース前', '羊羹orタブレット', '40', '10'),
    ('', '合計', '280', '65'),
]
for r in rows_snack14:
    row = add_detail_row(detail_table, *r, bg=COLOR_RACE2_LIGHT)
    if r[0] == '':
        for cell in row.cells:
            set_cell_bg_from_rgb(cell, RGBColor(0xEE, 0xEE, 0xEE))
            for para in cell.paragraphs:
                for run in para.runs:
                    run.bold = True

# サマリー行
add_section_row_detail(detail_table, 'エネルギー・糖質 合計', COLOR_DARK_ORANGE)
totals = [
    ('前日夜合計', '（夕食＋補食）', '810', '140'),
    ('6/13 合計', '（朝食＋昼食＋補食＋夕食）', '2050', '385'),
    ('6/14 合計', '（朝食＋補食）', '790', '175'),
]
for r in totals:
    add_detail_row(detail_table, *r, bg=COLOR_LIGHT_ORANGE, bold=True)

# 詳細テーブルの列幅
detail_col_widths = [2.0, 7.0, 3.5, 3.5]
for row in detail_table.rows:
    for i, width in enumerate(detail_col_widths):
        if i < len(row.cells):
            row.cells[i].width = Cm(width)

# 保存
output_path = '/home/user/AK/試合当日食事プラン_6月13-14日.docx'
doc.save(output_path)
print(f'保存完了: {output_path}')
