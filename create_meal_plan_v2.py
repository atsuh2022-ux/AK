from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

doc = Document()

section = doc.sections[0]
section.page_width = Cm(21)
section.page_height = Cm(29.7)
section.left_margin = Cm(1.5)
section.right_margin = Cm(1.5)
section.top_margin = Cm(1.5)
section.bottom_margin = Cm(1.5)

# カラー定義
COLOR_TITLE_BG    = RGBColor(0x4A, 0x1A, 0x6A)   # タイトル背景（深紫）
COLOR_TITLE_SUB   = RGBColor(0x7B, 0x3F, 0xA8)   # サブタイトル文字
COLOR_WHITE       = RGBColor(0xFF, 0xFF, 0xFF)
COLOR_GRAY        = RGBColor(0x80, 0x80, 0x80)
COLOR_TBL_HEADER  = RGBColor(0x5A, 0x5A, 0x5A)
COLOR_SUM_BG      = RGBColor(0xF0, 0xE8, 0xFF)   # サマリー背景
COLOR_SUM_TITLE   = RGBColor(0x4A, 0x1A, 0x6A)

# 金曜（移動・前日）
COLOR_FRI         = RGBColor(0x1A, 0x7A, 0x6A)   # teal
COLOR_FRI_LIGHT   = RGBColor(0xD0, 0xF0, 0xEA)

# 土曜（走幅跳 9:00）
COLOR_SAT         = RGBColor(0xC8, 0x50, 0x10)   # burnt orange
COLOR_SAT_LIGHT   = RGBColor(0xFD, 0xE2, 0xD0)

# 日曜（100m 12:33）
COLOR_SUN         = RGBColor(0x1A, 0x5B, 0xA8)   # blue
COLOR_SUN_LIGHT   = RGBColor(0xD6, 0xE8, 0xF8)

# リカバリー
COLOR_REC         = RGBColor(0x27, 0x8A, 0x3E)   # green
COLOR_REC_LIGHT   = RGBColor(0xD4, 0xEF, 0xDA)

COLS = 5

# ===== ユーティリティ =====
def rgb_tuple(c):
    return (c[0], c[1], c[2])

def set_cell_bg(cell, rgb_color):
    r, g, b = rgb_tuple(rgb_color)
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), f'{r:02X}{g:02X}{b:02X}')
    tcPr.append(shd)

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

def set_spacing(para, before=0, after=0):
    pPr = para._p.get_or_add_pPr()
    sp = OxmlElement('w:spacing')
    sp.set(qn('w:before'), str(before))
    sp.set(qn('w:after'), str(after))
    pPr.append(sp)

def add_run(para, text, bold=False, size=10, color=None, italic=False):
    run = para.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    run.italic = italic
    if color:
        run.font.color.rgb = color
    return run

def set_col_widths(table, widths_cm):
    for row in table.rows:
        for i, w in enumerate(widths_cm):
            if i < len(row.cells):
                row.cells[i].width = Cm(w)

# ===== テーブル行追加ヘルパー =====
def add_tbl_header(table, texts, bg):
    row = table.add_row()
    for i, text in enumerate(texts):
        c = row.cells[i]
        set_cell_bg(c, bg)
        set_cell_margins(c, 60, 60, 80, 80)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_run(p, text, bold=True, size=9, color=COLOR_WHITE)
    return row

def add_section_hdr(table, text, bg, color=None):
    row = table.add_row()
    for i in range(1, COLS):
        row.cells[0].merge(row.cells[i])
    c = row.cells[0]
    set_cell_bg(c, bg)
    set_cell_margins(c, 90, 90, 120, 120)
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    add_run(p, text, bold=True, size=10, color=color or COLOR_WHITE)
    return row

def add_data_row(table, t, timing, food, carb, note, bg=None):
    row = table.add_row()
    vals  = [t, timing, food, carb, note]
    aligns = [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER,
              WD_ALIGN_PARAGRAPH.LEFT,   WD_ALIGN_PARAGRAPH.CENTER,
              WD_ALIGN_PARAGRAPH.LEFT]
    for i, (v, a) in enumerate(zip(vals, aligns)):
        c = row.cells[i]
        if bg:
            set_cell_bg(c, bg)
        set_cell_margins(c, 50, 50, 80, 80)
        p = c.paragraphs[0]
        p.alignment = a
        add_run(p, v, size=8.5)
    return row

def add_race_row(table, text, bg):
    row = table.add_row()
    for i in range(1, COLS):
        row.cells[0].merge(row.cells[i])
    c = row.cells[0]
    set_cell_bg(c, bg)
    set_cell_margins(c, 90, 90, 120, 120)
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(p, text, bold=True, size=11, color=COLOR_WHITE)
    return row

def add_notice_row(table, text, bg=None):
    row = table.add_row()
    for i in range(1, COLS):
        row.cells[0].merge(row.cells[i])
    c = row.cells[0]
    set_cell_bg(c, bg or RGBColor(0xEE, 0xEE, 0xEE))
    set_cell_margins(c, 50, 50, 120, 120)
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_run(p, text, size=8.5, color=COLOR_GRAY)
    return row

# ===== タイトル =====
tt = doc.add_table(rows=1, cols=1)
tt.alignment = WD_TABLE_ALIGNMENT.CENTER
tc = tt.rows[0].cells[0]
set_cell_bg(tc, COLOR_TITLE_BG)
set_cell_margins(tc, 120, 80, 200, 200)
p = tc.paragraphs[0]
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_run(p, '　試合当日 食事・補食プラン　', bold=True, size=16, color=COLOR_WHITE)

doc.add_paragraph()

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_spacing(sub, 0, 60)
add_run(sub, '消化負担ゼロ・コンディション最優先　｜　体重51kg　糖質目標 7〜8g/kg/日', bold=True, size=10, color=COLOR_TITLE_SUB)

desc = doc.add_paragraph()
set_spacing(desc, 0, 80)
add_run(desc, '6/13（土）走幅跳・6/14（日）100mの2日間構成です。走幅跳は朝9:00スタートのため、朝食は早め（6:00〜6:30）を心がけましょう。'
        'ホテルビュッフェの開始時間が6:30以降の場合は、前夜にコンビニで購入しておいた食品を部屋で食べることを推奨します。'
        '金曜朝の自炊食でしっかりカーボローディングを行い、その後は外食・購入食でコンディションを整えましょう。', size=9)

# ===== メインスケジュール表 =====
table = doc.add_table(rows=0, cols=COLS)
table.style = 'Table Grid'
table.alignment = WD_TABLE_ALIGNMENT.CENTER

add_tbl_header(table, ['時間', 'タイミング', '食事・補食内容', '糖質量', '目的・ポイント'], COLOR_TBL_HEADER)

# ========== 金曜日 6/12 ==========
add_section_hdr(table, '　金曜日 6/12（移動日・前日）　※朝食のみ自炊、以降は外食・購入', COLOR_FRI)

add_data_row(table,
    '6:30〜\n7:30',
    '朝食\n（自炊・自宅）\n★最後の自炊★',
    '白飯200g\n卵料理（スクランブルエッグ等）\n野菜の煮物（消化しやすいもの）\nインスタント味噌汁',
    '約100〜\n120g',
    '試合前最後の自炊食。グリコーゲンをしっかり蓄える。消化しやすい食材で統一する。揚げ物・生野菜・きのこ類は避ける。',
    bg=COLOR_FRI_LIGHT)

add_data_row(table,
    '移動中\n11:30〜\n13:00',
    '昼食\n（コンビニ・外食）\n移動中または\nホテル近辺',
    'おにぎり2個（具は梅・昆布等）\nうどんまたは蕎麦\nバナナ1本\nスポーツドリンク',
    '約80〜\n100g',
    '移動疲労の回復と翌日に向けた補充。消化しやすい主食を選ぶ。脂質の多い弁当や揚げ物・生ものは避ける。水分補給もこまめに行う。')

add_data_row(table,
    '18:00〜\n20:00',
    '夕食\n（外食・コンビニ）\nホテル到着後',
    '白飯200g / 雑炊 / うどん\n焼き魚またはサラダチキン\n野菜料理（柔らかく調理）\nインスタント味噌汁',
    '約100〜\n120g',
    '翌日の走幅跳に向けて最後のグリコーゲン蓄積。なるべく早めに食べて消化時間を確保する（就寝3時間前が理想）。',
    bg=COLOR_FRI_LIGHT)

add_data_row(table,
    '就寝前\n（任意）',
    '補食\n（空腹時のみ）',
    '和菓子・ゼリー・糖質多めのドリンク\n※空腹でなければ無理しない',
    '約30〜\n40g',
    '就寝2時間前までに摂取。就寝直前は避ける。翌朝が非常に早いため、睡眠を最優先にする。')

# ========== 土曜日 6/13 走幅跳 9:00 ==========
add_section_hdr(table, '　土曜日 6/13（試合1日目）　走幅跳　招集8:20 / 招集終了8:45 / 競技9:00', COLOR_SAT)

add_data_row(table,
    '5:30',
    '起床\n水分補給',
    '水200〜250ml（ゆっくり）',
    '0g',
    '起床後すぐに水分補給で体内の水分バランスを整える。体調・体重を確認する。',
    bg=COLOR_SAT_LIGHT)

add_data_row(table,
    '6:00〜\n6:30',
    '朝食\n（競技 約2.5〜3時間前）\n★ホテルビュッフェ\nまたはコンビニ購入★',
    '【ビュッフェ開場時】\nご飯茶碗1杯 / おにぎり1個\nバナナ1本\nスポーツドリンクまたはジュース\n\n【ビュッフェ未開場時】\n前夜にコンビニで購入しておいた\nおにぎり1個 ＋ バナナ ＋ ゼリー',
    '約60〜\n80g',
    '競技まで時間が短いため量は少なめにする。消化の速い食材（おにぎり・バナナ・ゼリー）に絞る。脂質・タンパク質・食物繊維は最小限に。ビュッフェの開場時間を前夜に確認しておく。')

add_data_row(table,
    '7:00〜\n8:00',
    'ウォームアップ中',
    'スポーツドリンク 少量ずつ\n（150〜200ml）\nまたは水',
    '約10〜\n15g',
    '一気飲みせず少量ずつ補給する。体温調節と水分・電解質の維持を意識する。',
    bg=COLOR_SAT_LIGHT)

add_data_row(table,
    '7:30〜\n8:00',
    '補食①\n（競技 約1〜1.5時間前）',
    'エネルギーゼリー（1個）\nまたはタブレット',
    '約20〜\n30g',
    '追加のエネルギー補充。固形食は避けゼリーを優先する。')

add_notice_row(table, '8:20　走幅跳 招集　（8:05〜8:20は摂取しない）')

add_data_row(table,
    '8:45〜\n9:00',
    '招集終了〜\n競技待機\n（任意補食）',
    '羊羹またはタブレット',
    '約10g',
    '摂取できる環境であれば補給する。摂取できない場合は無理しない。',
    bg=COLOR_SAT_LIGHT)

add_race_row(table, '🏃‍♀️ 試合1日目　走幅跳　9:00 競技開始', COLOR_SAT)

add_data_row(table,
    '競技終了後\n〜10:30',
    '回復補給\n（なるべく早く）',
    'エネルギーゼリー1個\n水またはスポーツドリンク\n（100〜200ml）',
    '約30〜\n40g',
    '消耗した糖質をすみやかに補充する。少量ずつゆっくり摂取する。固形物はゼリー・ドリンクを優先する。',
    bg=COLOR_SAT_LIGHT)

add_data_row(table,
    '11:00〜\n12:00',
    '昼食\n（競技後・回復食）\nコンビニ・外食',
    'おにぎり2個またはうどん\nサラダチキンまたは卵料理\nバナナ1本\nスポーツドリンク',
    '約90〜\n110g',
    '走幅跳後の回復と翌日100mのエネルギー蓄積を兼ねる。タンパク質も摂取して筋肉の回復を促す。脂質の多いものは避ける。')

add_data_row(table,
    '18:00〜\n19:00',
    '夕食\n（翌日100mに備えて）\nコンビニ・外食',
    '白飯200g またはうどん\n焼き魚またはサラダチキン\n野菜料理（柔らかく調理）\nインスタント味噌汁',
    '約100〜\n120g',
    '翌日100mに向けてグリコーゲンをしっかり補充する。消化しやすい食材を選び、脂質・食物繊維の多いものは避ける。なるべく早めに食べる。',
    bg=COLOR_SAT_LIGHT)

add_data_row(table,
    '就寝前\n（任意）',
    '補食\n（空腹時のみ）',
    '和菓子・ゼリー・糖質多めのドリンク',
    '約30〜\n40g',
    '翌日100mに向けた追加補充。就寝2時間前までに摂取。睡眠を十分に確保する。')

# ========== 日曜日 6/14 100m 12:33 ==========
add_section_hdr(table, '　日曜日 6/14（試合2日目）　100m　招集11:58 / 招集終了12:18 / レース12:33', COLOR_SUN)

add_data_row(table,
    '6:30〜\n7:00',
    '起床\n水分補給',
    '水200〜250ml（ゆっくり）',
    '0g',
    '起床後すぐに水分補給で体内の水分バランスを整える。昨日の走幅跳の疲労状態を確認する。',
    bg=COLOR_SUN_LIGHT)

add_data_row(table,
    '7:00〜\n7:30',
    '朝食\n（ホテルビュッフェ）\n（レース 約5時間前）',
    'ご飯1膳またはおにぎり1個\nバナナ1本\nフルーツヨーグルト\nオレンジジュース\n（たまご料理1品）',
    '約90〜\n110g',
    '100mに備えてエネルギーをしっかり蓄える。消化しやすい食材のみを選ぶ。脂質・タンパク質は最小限に。食べ慣れたものだけにする。')

add_data_row(table,
    '10:00〜\n10:30',
    '補食①\n（レース 約2時間前）\n到着時〜アップ前',
    'エネルギーゼリーまたはおにぎり1個',
    '約30〜\n40g',
    '胃への負担を抑えるためゼリーや具の少ないおにぎりを選ぶ。固形物を食べる場合は少量ずつよく噛んで食べる。',
    bg=COLOR_SUN_LIGHT)

add_data_row(table,
    '〜11:45',
    'ウォームアップ中',
    'スポーツドリンク 少量ずつ\n（150〜200ml）',
    '約10〜\n15g',
    '一気飲みせず少量ずつ補給する。体温に注意しながら水分・電解質を維持する。')

add_notice_row(table, '11:58　100m 招集　（11:43〜11:58は摂取しない）')

add_data_row(table,
    '12:18〜\n12:33',
    '招集終了〜\nレース待機\n（任意補食）',
    '羊羹またはタブレット\n※アップ中でもok',
    '約10g',
    '摂取できる環境であれば補給する。摂取できない場合は無理しない。',
    bg=COLOR_SUN_LIGHT)

add_race_row(table, '🏃‍♀️ 試合2日目　100m　12:33 スタート', COLOR_SUN)

# ========== リカバリー ==========
add_section_hdr(table, '　日曜日 6/14（レース後）　リカバリー', COLOR_REC)

add_data_row(table,
    '〜13:15',
    'レース直後\n回復補給',
    'エネルギーゼリー1個\n水またはスポーツドリンク',
    '約30〜\n40g',
    'お疲れさまでした！まず水分と糖質を素早く補給する。少量ずつゆっくり摂取する。',
    bg=COLOR_REC_LIGHT)

add_data_row(table,
    '13:30〜\n14:30',
    '回復食・昼食\nコンビニ・外食',
    '好みの昼食（バランスよく）\nたんぱく質・糖質・野菜を含む食事\n例：定食・丼・うどん＋サラダチキン等',
    '—',
    '試合後は好みのものを食べてOK。ただし消化にやさしいものから始める。たんぱく質（肉・魚・卵）で筋肉の修復を促す。')

add_data_row(table,
    '17:00〜\n19:00',
    '夕食\nリカバリー食',
    '主食＋主菜＋副菜＋汁物\n（バランスの良い食事）\n果物やスポーツドリンクで\n抗酸化・電解質補給',
    '—',
    '2日間の疲労回復のため、栄養バランスを重視する。鉄分・ビタミンCも意識して摂取する。水分補給を続ける。帰宅後はゆっくり休む。',
    bg=COLOR_REC_LIGHT)

# 列幅設定
set_col_widths(table, [2.0, 2.6, 4.6, 1.8, 6.0])

doc.add_paragraph()

# ===== 糖質・水分まとめ =====
st = doc.add_table(rows=1, cols=1)
st.alignment = WD_TABLE_ALIGNMENT.CENTER
sc = st.rows[0].cells[0]
set_cell_bg(sc, COLOR_SUM_BG)
set_cell_margins(sc, 100, 100, 150, 150)

sp = sc.paragraphs[0]
add_run(sp, '【糖質・水分まとめ（体重51kg）】', bold=True, size=10, color=COLOR_SUM_TITLE)
set_spacing(sp, 0, 30)

lines = [
    '【6/12 金曜】　朝食（自炊）：約100〜120g　昼食：約80〜100g　夕食：約100〜120g　▶ 合計：約280〜340g',
    '【6/13 土曜 走幅跳】　朝食：約60〜80g　ウォームアップ中：約10〜15g　補食①：約20〜30g　招集前（任意）：約10g',
    '　　　　　　　　　　　　回復：約30〜40g　昼食：約90〜110g　夕食：約100〜120g　▶ 当日トータル：約320〜405g',
    '【6/14 日曜 100m】　朝食：約90〜110g　補食①：約30〜40g　ウォームアップ中：約10〜15g　招集前（任意）：約10g',
    '　　　　　　　　　　　　▶ レース前トータル：約140〜175g',
    '',
    '※ 試合前1週間の目標：体重51kg × 7〜8g = 357〜408g/日（試合前3〜5日）',
    '※ 走幅跳は朝9:00スタートのため、前夜にコンビニで購入しておき朝食の準備をしておく。ビュッフェ開場時間の確認を忘れずに。',
]
for line in lines:
    lp = sc.add_paragraph()
    add_run(lp, line, size=8.5)
    set_spacing(lp, 20, 20)

doc.add_paragraph()

# ===== ポイント =====
pt = doc.add_table(rows=1, cols=1)
pt.alignment = WD_TABLE_ALIGNMENT.CENTER
pc = pt.rows[0].cells[0]
set_cell_bg(pc, RGBColor(0xF5, 0xF5, 0xF5))
set_cell_margins(pc, 100, 100, 150, 150)

pp = pc.paragraphs[0]
add_run(pp, '【食事・補食のポイント】', bold=True, size=10, color=COLOR_SAT)
set_spacing(pp, 0, 30)

points = [
    ('【走幅跳（朝9:00）の注意点】',
     '競技まで時間が短いため、朝食は消化の速いものを少量で。おにぎり1個＋バナナ＋ゼリーが理想。ビュッフェが6:30以降に開場する場合は前夜コンビニで購入しておく。'),
    ('【消化負担を減らすために】',
     '食物繊維の多い食材（玄米・ゴボウ・こんにゃく・きのこ類）、脂質の多いもの（揚げ物・マヨネーズ）、生もの、乳製品は前日〜当日は避ける。白米・うどん・バナナなど消化の速い食材に絞る。'),
    ('【摂取タイミングの鉄則】',
     '固形食はなるべくレース2〜3時間前まで。少量ずつゆっくり摂ることで胃の不快感を防ぐ。走幅跳は競技2.5〜3時間前（6:00〜6:30）が最後の固形食。'),
    ('【試合当日に試してはいけないもの】',
     '初めて食べる食品・サプリメント・スポーツ製品は使用しない。事前に練習で試したことのあるものだけを選ぶ。'),
    ('【2日間を通じた戦略】',
     '6/13走幅跳後〜6/14朝食までの昼食・夕食が100mのパフォーマンスを左右する。走幅跳後の昼食でしっかり回復し、夕食でカーボローディングを完成させる。'),
]
for title, body in points:
    bp = pc.add_paragraph()
    add_run(bp, title, bold=True, size=8.5, color=COLOR_SAT)
    add_run(bp, '\n' + body, size=8.5)
    set_spacing(bp, 40, 20)

doc.add_paragraph()

# ===== 詳細テーブル =====
dh = doc.add_paragraph()
add_run(dh, '食事パターンとエネルギー・糖質量（詳細）', bold=True, size=10, color=COLOR_SUM_TITLE)

dt = doc.add_table(rows=0, cols=4)
dt.style = 'Table Grid'

def add_dt_hdr(table, texts, bg):
    row = table.add_row()
    for i, text in enumerate(texts):
        c = row.cells[i]
        set_cell_bg(c, bg)
        set_cell_margins(c, 60, 60, 80, 80)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_run(p, text, bold=True, size=8.5, color=COLOR_WHITE)

def add_dt_sec(table, text, bg):
    row = table.add_row()
    for i in range(1, 4):
        row.cells[0].merge(row.cells[i])
    c = row.cells[0]
    set_cell_bg(c, bg)
    set_cell_margins(c, 60, 60, 100, 100)
    p = c.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    add_run(p, text, bold=True, size=9, color=COLOR_WHITE)

def add_dt_row(table, cat, item, kcal, carb, bg=None, bold=False):
    row = table.add_row()
    for i, (v, a) in enumerate(zip(
        [cat, item, kcal, carb],
        [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT,
         WD_ALIGN_PARAGRAPH.RIGHT, WD_ALIGN_PARAGRAPH.RIGHT]
    )):
        c = row.cells[i]
        if bg:
            set_cell_bg(c, bg)
        set_cell_margins(c, 40, 40, 80, 80)
        p = c.paragraphs[0]
        p.alignment = a
        add_run(p, v, bold=bold, size=8.5)

TOTAL_BG = RGBColor(0xEE, 0xEE, 0xEE)

add_dt_hdr(dt, ['', '内容', 'エネルギー(kcal)', '糖質(g)'], COLOR_TBL_HEADER)

# 金曜 朝食（自炊）
add_dt_sec(dt, '金曜 朝食（自炊）', COLOR_FRI)
for r in [
    ('主食',   '白飯200g',              '300', '70'),
    ('主菜',   '卵料理',                '100',  '3'),
    ('副菜',   '野菜の煮物',            '80',  '15'),
    ('汁物',   'インスタント味噌汁',     '40',   '5'),
    ('',       '合計',                  '520', '93'),
]:
    row = add_dt_row(dt, *r, bg=COLOR_FRI_LIGHT if r[0] != '' else TOTAL_BG, bold=(r[0]==''))

# 金曜 昼食
add_dt_sec(dt, '金曜 昼食（コンビニ・外食）', COLOR_FRI)
for r in [
    ('主食',   'おにぎり2個',           '340', '80'),
    ('果物',   'バナナ1本',              '100', '20'),
    ('飲み物', 'スポーツドリンク',        '60', '15'),
    ('',       '合計',                  '500', '115'),
]:
    add_dt_row(dt, *r, bg=TOTAL_BG if r[0]=='' else None, bold=(r[0]==''))

# 金曜 夕食
add_dt_sec(dt, '金曜 夕食（外食・コンビニ）', COLOR_FRI)
for r in [
    ('主食',   '白飯200g',              '300', '70'),
    ('主菜',   '焼き魚またはサラダチキン','150',  '0'),
    ('副菜',   '野菜料理（柔らかく）',    '80',  '15'),
    ('汁物',   'インスタント味噌汁',      '40',   '5'),
    ('',       '合計',                  '570', '90'),
]:
    add_dt_row(dt, *r, bg=COLOR_FRI_LIGHT if r[0] != '' else TOTAL_BG, bold=(r[0]==''))

# 土曜 朝食
add_dt_sec(dt, '土曜 朝食（走幅跳 約2.5〜3時間前）', COLOR_SAT)
for r in [
    ('主食',   'ご飯1膳 / おにぎり1個',  '200', '50'),
    ('果物',   'バナナ1本',              '100', '20'),
    ('飲み物', 'スポーツドリンク/ジュース','60',  '15'),
    ('',       '合計',                  '360', '85'),
]:
    add_dt_row(dt, *r, bg=COLOR_SAT_LIGHT if r[0]!='' else TOTAL_BG, bold=(r[0]==''))

# 土曜 補食
add_dt_sec(dt, '土曜 補食（競技前〜競技中）', COLOR_SAT)
for r in [
    ('補食①',  'エネルギーゼリー',       '120', '25'),
    ('アップ中','スポーツドリンク',        '60', '15'),
    ('競技前',  '羊羹/タブレット（任意）', '40',  '10'),
    ('',        '合計',                  '220', '50'),
]:
    add_dt_row(dt, *r, bg=TOTAL_BG if r[0]=='' else None, bold=(r[0]==''))

# 土曜 昼食
add_dt_sec(dt, '土曜 昼食（競技後・回復食）', COLOR_SAT)
for r in [
    ('主食',   'おにぎり2個/うどん',     '340', '80'),
    ('主菜',   'サラダチキン/卵料理',     '130',  '3'),
    ('果物',   'バナナ1本',              '100', '20'),
    ('飲み物', 'スポーツドリンク',         '60', '15'),
    ('',       '合計',                  '630', '118'),
]:
    add_dt_row(dt, *r, bg=COLOR_SAT_LIGHT if r[0]!='' else TOTAL_BG, bold=(r[0]==''))

# 土曜 夕食
add_dt_sec(dt, '土曜 夕食（翌日100m準備）', COLOR_SAT)
for r in [
    ('主食',   '白飯200g / うどん',      '300', '70'),
    ('主菜',   '焼き魚/サラダチキン',     '150',  '0'),
    ('副菜',   '野菜料理（柔らかく）',     '80',  '15'),
    ('汁物',   'インスタント味噌汁',       '40',   '5'),
    ('',       '合計',                  '570', '90'),
]:
    add_dt_row(dt, *r, bg=COLOR_SAT_LIGHT if r[0]!='' else TOTAL_BG, bold=(r[0]==''))

# 日曜 朝食
add_dt_sec(dt, '日曜 朝食（100m 約5時間前）', COLOR_SUN)
for r in [
    ('主食',   'おにぎり1個/ご飯',        '200', '50'),
    ('果物',   'バナナ1本',               '100', '20'),
    ('乳製品', 'フルーツヨーグルト',        '120', '20'),
    ('補食',   'オレンジジュース',           '90', '20'),
    ('',       '合計',                   '510', '110'),
]:
    add_dt_row(dt, *r, bg=COLOR_SUN_LIGHT if r[0]!='' else TOTAL_BG, bold=(r[0]==''))

# 日曜 補食
add_dt_sec(dt, '日曜 補食（レース前）', COLOR_SUN)
for r in [
    ('補食①',  'ゼリーまたはおにぎり',    '180', '35'),
    ('アップ中','スポーツドリンク',          '60', '15'),
    ('レース前','羊羹/タブレット（任意）',   '40', '10'),
    ('',        '合計',                   '280', '60'),
]:
    add_dt_row(dt, *r, bg=TOTAL_BG if r[0]=='' else None, bold=(r[0]==''))

# 合計サマリー
add_dt_sec(dt, 'エネルギー・糖質 合計', COLOR_TITLE_BG)
for r in [
    ('金曜合計', '（朝食＋昼食＋夕食）',         '1590', '298'),
    ('土曜合計', '（朝食＋補食＋昼食＋夕食）',    '1780', '343'),
    ('日曜合計', '（朝食＋補食）',               '790',  '170'),
]:
    add_dt_row(dt, *r, bg=COLOR_SUM_BG, bold=True)

set_col_widths(dt, [2.0, 7.0, 3.5, 3.5])

output = '/home/user/AK/試合当日食事プラン_女性51kg_6月13-14日.docx'
doc.save(output)
print(f'保存完了: {output}')
