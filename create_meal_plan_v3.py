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
COLOR_TITLE_BG   = RGBColor(0xC0, 0x50, 0x10)
COLOR_TITLE_SUB  = RGBColor(0xC0, 0x50, 0x10)
COLOR_WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
COLOR_GRAY       = RGBColor(0x80, 0x80, 0x80)
COLOR_TBL_HDR    = RGBColor(0x5A, 0x5A, 0x5A)
COLOR_PREV       = RGBColor(0x6A, 0x4A, 0xAA)
COLOR_PREV_LIGHT = RGBColor(0xEA, 0xE0, 0xFF)
COLOR_DAY1       = RGBColor(0x1A, 0x6B, 0xB8)
COLOR_DAY1_LIGHT = RGBColor(0xD6, 0xE8, 0xF8)
COLOR_DAY2       = RGBColor(0x27, 0x8A, 0x3E)
COLOR_DAY2_LIGHT = RGBColor(0xD4, 0xEF, 0xDA)
COLOR_ORANGE_LIGHT = RGBColor(0xFF, 0xE5, 0xCC)
COLOR_JITAKI     = RGBColor(0x5A, 0x30, 0x00)  # 自炊ラベル色

COLS = 5

def rgb_t(c): return (c[0], c[1], c[2])

def cell_bg(cell, rgb):
    r, g, b = rgb_t(rgb)
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), f'{r:02X}{g:02X}{b:02X}')
    tcPr.append(shd)

def cell_mar(cell, top=50, bottom=50, left=80, right=80):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for side, val in [('top',top),('bottom',bottom),('left',left),('right',right)]:
        n = OxmlElement(f'w:{side}')
        n.set(qn('w:w'), str(val)); n.set(qn('w:type'), 'dxa')
        tcMar.append(n)
    tcPr.append(tcMar)

def spacing(para, before=0, after=0):
    sp = OxmlElement('w:spacing')
    sp.set(qn('w:before'), str(before)); sp.set(qn('w:after'), str(after))
    para._p.get_or_add_pPr().append(sp)

def run(para, text, bold=False, size=10, color=None, italic=False):
    r = para.add_run(text)
    r.bold = bold; r.font.size = Pt(size); r.italic = italic
    if color: r.font.color.rgb = color
    return r

def col_widths(table, ws):
    for row in table.rows:
        for i, w in enumerate(ws):
            if i < len(row.cells): row.cells[i].width = Cm(w)

# ── テーブル行ヘルパー ──
def tbl_header(table, texts, bg):
    row = table.add_row()
    for i, t in enumerate(texts):
        c = row.cells[i]; cell_bg(c, bg); cell_mar(c, 60,60,80,80)
        p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run(p, t, bold=True, size=9, color=COLOR_WHITE)

def section_hdr(table, text, bg):
    row = table.add_row()
    for i in range(1, COLS): row.cells[0].merge(row.cells[i])
    c = row.cells[0]; cell_bg(c, bg); cell_mar(c, 90,90,120,120)
    p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run(p, text, bold=True, size=10, color=COLOR_WHITE)

def data_row(table, t, timing_lines, food, carb, note, bg=None):
    """timing_lines: list of (text, color) tuples for multi-style timing cell"""
    row = table.add_row()
    vals = [t, None, food, carb, note]
    aligns = [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.CENTER,
              WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT]
    for i, (v, a) in enumerate(zip(vals, aligns)):
        c = row.cells[i]
        if bg: cell_bg(c, bg)
        cell_mar(c, 50,50,80,80)
        p = c.paragraphs[0]; p.alignment = a
        if i == 1:  # timing cell with colored sub-labels
            for (txt, clr) in timing_lines:
                run(p, txt, size=8.5, color=clr, bold=(clr is not None and clr != COLOR_GRAY))
        else:
            run(p, v or '', size=8.5)
    return row

def race_row(table, text, bg):
    row = table.add_row()
    for i in range(1, COLS): row.cells[0].merge(row.cells[i])
    c = row.cells[0]; cell_bg(c, bg); cell_mar(c, 90,90,120,120)
    p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, text, bold=True, size=11, color=COLOR_WHITE)

def notice_row(table, text, bg=None):
    row = table.add_row()
    for i in range(1, COLS): row.cells[0].merge(row.cells[i])
    c = row.cells[0]; cell_bg(c, bg or RGBColor(0xEE,0xEE,0xEE)); cell_mar(c,50,50,120,120)
    p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run(p, text, size=8.5, color=COLOR_GRAY)

def jitaki(txt):
    """自炊ラベル付きタイミングタプル"""
    return [(txt + '\n', None), ('★自炊', COLOR_JITAKI)]

def gaishoku(txt):
    return [(txt + '\n', None), ('外食', RGBColor(0x1A,0x6B,0xB8))]

def jisan(txt):
    return [(txt + '\n', None), ('持参またはコンビニ', RGBColor(0x27,0x7A,0x3E))]

# ════════════ タイトル ════════════
tt = doc.add_table(rows=1, cols=1); tt.alignment = WD_TABLE_ALIGNMENT.CENTER
tc = tt.rows[0].cells[0]; cell_bg(tc, COLOR_TITLE_BG); cell_mar(tc,120,80,200,200)
p = tc.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run(p, '　試合当日 食事・補食プラン　', bold=True, size=16, color=COLOR_WHITE)

doc.add_paragraph()

sub = doc.add_paragraph(); sub.alignment = WD_ALIGN_PARAGRAPH.CENTER; spacing(sub,0,60)
run(sub, '消化負担ゼロ・レース間の素早い回復　｜　体重61kg　糖質目標 8g/kg/日', bold=True, size=10, color=COLOR_TITLE_SUB)

desc = doc.add_paragraph(); spacing(desc,0,80)
run(desc,
    '6/13（金）400m・6/14（土）100mの2日間構成です。'
    '6/12〜6/14の夕食・6/13〜6/14の朝食は自炊（数日前の作り置き対応可）、'
    '6/12昼食は外食、6/13昼食は持参またはコンビニ購入、6/14昼食（レース後）は外食です。'
    '★マークは作り置き可の料理です。消化しやすい食材に統一しましょう。', size=9)

# ════════════ メインスケジュール表 ════════════
table = doc.add_table(rows=0, cols=COLS)
table.style = 'Table Grid'; table.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_header(table, ['時間','タイミング','食事・補食内容','糖質量','目的・ポイント'], COLOR_TBL_HDR)

# ────────── 6/12 木曜 前日 ──────────
section_hdr(table, '　前日（木曜日）6/12　自宅', COLOR_PREV)

data_row(table,
    '12:00〜\n13:00',
    gaishoku('昼食\n（外食）'),
    '鶏の照り焼き定食\n（白飯200g＋鶏肉料理＋野菜料理＋味噌汁）\nまたは うどん定食・丼もの（白米系）',
    '約100〜\n120g',
    '翌々日に向けてグリコーゲンを蓄え始める。消化しやすい定食・丼系を選ぶ。揚げ物・生もの・脂質の多い料理は避ける。',
    bg=COLOR_PREV_LIGHT)

data_row(table,
    '18:00〜\n19:00',
    jitaki('夕食\n（自炊）\n★作り置き可'),
    '白飯200g\n肉じゃが★（数日前から作り置きOK）\nほうれん草のおひたし★\nインスタント味噌汁',
    '約110〜\n130g',
    '翌日のレースに向けてグリコーゲンをしっかり蓄える。野菜は柔らかく調理。生野菜・揚げ物・脂質の多いものは避ける。なるべく早めに食べる（就寝3時間前が理想）。')

data_row(table,
    '就寝前\n（任意）',
    [('補食\n（空腹時のみ）', None)],
    '和菓子・バナナ・糖質多めのドリンク\n※空腹でなければ無理しない',
    '約30〜\n50g',
    '就寝2時間前までに。就寝直前の摂取は翌朝の胃もたれにつながるため避ける。',
    bg=COLOR_PREV_LIGHT)

# ────────── 6/13 金曜 試合1日目 400m ──────────
section_hdr(table, '　試合1日目（金曜日）6/13　400m　招集14:35 / 招集終了14:50 / レース15:10', COLOR_DAY1)

data_row(table,
    '起床\n6:30〜',
    [('水分補給', None)],
    '水200〜250ml（ゆっくり）',
    '0g',
    '起床後すぐに水分補給で体内の水分バランスを整える。体調を確認する。')

data_row(table,
    '7:00〜\n7:30',
    jitaki('朝食\n（自炊）\n★作り置き可\n（レース 約8時間前）'),
    '白飯200g\n卵焼き★（前夜または当朝に作る）\n野菜の煮物★（かぼちゃ煮・ひじき等）\nインスタント味噌汁\nバナナ1本',
    '約120〜\n140g',
    'レースまで時間があるためしっかり食べる。消化しやすい食材のみを選ぶ。脂質・食物繊維の多いものは避ける。野菜は柔らかく調理したものに限る。',
    bg=COLOR_DAY1_LIGHT)

data_row(table,
    '午前中',
    [('移動', COLOR_GRAY)],
    '（会場へ移動）\n移動中：水またはスポーツドリンクを少量ずつ補給',
    '約5〜\n10g',
    '移動中も水分をこまめに補給する。')

data_row(table,
    '11:30〜\n12:00',
    jisan('昼食\n（レース 約3時間前）'),
    '【持参（自作）】\nおにぎり2個（梅・昆布★）＋卵焼き★＋バナナ1本\n\n【コンビニ購入の場合】\nおにぎり2個（具少なめ）＋バナナ1本＋スポーツドリンク',
    '約90〜\n110g',
    'レース前最後の固形食。持参品は前夜または当朝に準備する。コンビニの場合は梅・昆布など具の少ないおにぎりを選ぶ。揚げ物・サラダ・生野菜・脂質の多いものは絶対に避ける。',
    bg=COLOR_DAY1_LIGHT)

data_row(table,
    '13:30〜\n14:00',
    [('補食①\n（レース 約1〜1.5時間前）', None)],
    'エネルギーゼリー（1個）\nまたは おにぎり1個（少量）',
    '約30〜\n40g',
    '胃への負担を抑えるためゼリーを優先。固形物を食べる場合は少量ずつよく噛んで食べる。')

data_row(table,
    '〜14:20',
    [('ウォームアップ中', None)],
    'スポーツドリンク 少量ずつ（150〜200ml）',
    '約10〜\n15g',
    '一気飲みせず少量ずつ補給する。体温に注意しながら水分・電解質を維持する。',
    bg=COLOR_DAY1_LIGHT)

notice_row(table, '14:35　400m 招集　（14:20〜14:35は摂取しない）')

data_row(table,
    '14:50〜\n15:10',
    [('招集終了〜\nレース待機\n（任意補食）', None)],
    '羊羹またはタブレット　※アップ中でもok',
    '約10g',
    '摂取できる環境であれば補給する。摂取できない場合は無理しなくてよい。',
    bg=COLOR_DAY1_LIGHT)

race_row(table, '🏃 試合1日目　400m　15:10 スタート', COLOR_DAY1)

data_row(table,
    '〜15:40',
    [('レース直後\n回復補給', None)],
    'エネルギーゼリー1個\n水またはスポーツドリンク（なるべく早く）',
    '約30〜\n45g',
    '消耗した糖質をすみやかに補充する。少量ずつゆっくり摂取する。')

data_row(table,
    '帰宅後\n18:30〜\n19:30',
    jitaki('夕食\n（自炊）\n★作り置き可\n翌日100m準備'),
    '白飯200g（多め・翌日の握り飯分も炊く）\n鶏むね肉の照り焼き★（数日前から作り置きOK）\nかぼちゃの煮物★（数日前から作り置きOK）\nインスタント味噌汁',
    '約110〜\n130g',
    '翌日100mに向けてグリコーゲンをしっかり回復・蓄積する。消化しやすい食材を選ぶ。翌朝のおにぎり分も一緒に炊いておくと便利。早めに食べて消化時間を確保する。',
    bg=COLOR_DAY1_LIGHT)

data_row(table,
    '就寝前\n（任意）',
    [('補食\n（空腹時のみ）', None)],
    '和菓子・バナナ・糖質多めのドリンク\n※空腹でなければ無理しない',
    '約30〜\n50g',
    '翌日100mに向けた追加補充。就寝2時間前までに摂取。十分な睡眠を確保する。')

# ────────── 6/14 土曜 試合2日目 100m ──────────
section_hdr(table, '　試合2日目（土曜日）6/14　100m　招集11:48 / 招集終了12:03 / レース12:18', COLOR_DAY2)

data_row(table,
    '起床\n7:00〜',
    [('水分補給', None)],
    '水200〜250ml（ゆっくり）',
    '0g',
    '起床後すぐに水分補給。体調確認。昨日の400mの疲労状態も確認する。',
    bg=COLOR_DAY2_LIGHT)

data_row(table,
    '7:00〜\n7:30',
    jitaki('朝食\n（自炊）\n（レース 約5時間前）'),
    'おにぎり1個（前夜に握っておく★）\nバナナ1本\nフルーツヨーグルト\nオレンジジュース',
    '約90〜\n110g',
    '100mに備えてエネルギーをしっかり蓄える。おにぎりは前夜の夕食時にまとめて握っておくと楽。消化しやすい食材のみを選ぶ。脂質・タンパク質は最小限に。')

data_row(table,
    '午前中\n9:00〜',
    [('移動', COLOR_GRAY)],
    '（会場へ移動）\n移動中：水またはスポーツドリンクを少量ずつ補給',
    '約5〜\n10g',
    '移動中も水分をこまめに補給する。',
    bg=COLOR_DAY2_LIGHT)

data_row(table,
    '10:00〜\n10:30',
    [('補食①\n（レース 約2時間前）\n到着時〜アップ前', None)],
    'エネルギーゼリーまたはおにぎり1個（小）',
    '約30〜\n40g',
    '胃への負担を抑えるためゼリーや具の少ないおにぎりを選ぶ。固形物を食べる場合は少量ずつよく噛んで食べる。')

data_row(table,
    '〜11:30',
    [('ウォームアップ中', None)],
    'スポーツドリンク 少量ずつ（150〜200ml）',
    '約10〜\n15g',
    '一気飲みせず少量ずつ補給する。体温に注意しながら水分・電解質を維持する。',
    bg=COLOR_DAY2_LIGHT)

notice_row(table, '11:48　100m 招集　（11:33〜11:48は摂取しない）')

data_row(table,
    '12:03〜\n12:18',
    [('招集終了〜\nレース待機\n（任意補食）', None)],
    '羊羹またはタブレット　※アップ中でもok',
    '約10g',
    '摂取できる環境であれば補給する。摂取できない場合は無理しなくてよい。',
    bg=COLOR_DAY2_LIGHT)

race_row(table, '🏃 試合2日目　100m　12:18 スタート', COLOR_DAY2)

data_row(table,
    '〜12:50',
    [('レース直後\n回復補給', None)],
    'エネルギーゼリー1個\n水またはスポーツドリンク（なるべく早く）',
    '約30〜\n40g',
    'お疲れさまでした！消耗した糖質をすみやかに補充する。少量ずつゆっくり摂取する。')

data_row(table,
    '13:00〜\n14:00',
    gaishoku('昼食\n（外食・レース後）\n回復食'),
    '好みのものを食べてOK\n例：定食・丼もの・うどん＋たんぱく質\n（鶏肉・魚・卵料理を含むものを推奨）',
    '—',
    '試合後は好みのものを食べてOK。ただし消化にやさしいものから始めると◎。たんぱく質（肉・魚・卵）を含む食事で筋肉の修復を促す。',
    bg=COLOR_DAY2_LIGHT)

data_row(table,
    '帰宅後\n18:00〜\n19:00',
    jitaki('夕食\n（自炊）\n★作り置き可\nリカバリー食'),
    '白飯または雑穀米\n主菜：鮭の塩焼き★ or 鶏肉の煮物★\n副菜：野菜たっぷりの煮物★（ひじき・ほうれん草等）\n汁物：具沢山の味噌汁（豆腐・わかめ）',
    '—',
    '2日間の疲労回復のため、栄養バランスを重視する。鉄分・ビタミンCも意識して摂取。作り置きを活用してゆっくり休む。水分補給も続ける。')

col_widths(table, [2.0, 2.8, 4.6, 1.8, 5.8])
doc.add_paragraph()

# ════════════ 糖質まとめ ════════════
st = doc.add_table(rows=1, cols=1); st.alignment = WD_TABLE_ALIGNMENT.CENTER
sc = st.rows[0].cells[0]; cell_bg(sc, COLOR_ORANGE_LIGHT); cell_mar(sc,100,100,150,150)
p = sc.paragraphs[0]; run(p, '【糖質・水分まとめ（体重61kg）】', bold=True, size=10, color=COLOR_TITLE_BG); spacing(p,0,30)

for line in [
    '【6/12 前日】　昼食（外食）：約100〜120g　夕食（自炊）：約110〜130g　就寝前補食（任意）：約30〜50g',
    '【6/13 試合1日目 400m】　朝食（自炊）：約120〜140g　昼食（持参/コンビニ）：約90〜110g　補食①：約30〜40g',
    '　　　　　　　　　　　　　アップ中：約10〜15g　招集前（任意）：約10g　▶ 当日トータル：約〜310g',
    '　　　　　　　　　　　　　夕食（自炊）：約110〜130g　就寝前補食（任意）：約30〜50g',
    '【6/14 試合2日目 100m】　朝食（自炊）：約90〜110g　補食①：約30〜40g　アップ中：約10〜15g　招集前（任意）：約10g　▶ レース前トータル：約〜175g',
    '',
    '※ 試合前1週間の目標：体重61kg × 7〜8g = 427〜488g/日（試合前3〜5日）',
]:
    lp = sc.add_paragraph(); run(lp, line, size=8.5); spacing(lp,20,20)

doc.add_paragraph()

# ════════════ 作り置きメモ ════════════
at = doc.add_table(rows=1, cols=1); at.alignment = WD_TABLE_ALIGNMENT.CENTER
ac = at.rows[0].cells[0]; cell_bg(ac, RGBColor(0xFB,0xF3,0xE8)); cell_mar(ac,100,100,150,150)
p = ac.paragraphs[0]; run(p, '【★ 作り置きレシピ候補（数日前から準備OK）】', bold=True, size=10, color=COLOR_JITAKI); spacing(p,0,30)

recipes = [
    ('肉じゃが',         '3〜4日前から保存可。じゃがいも・人参・玉ねぎ・牛または豚薄切り肉。糖質を多く含むじゃがいもで効率よく補充。'),
    ('鶏むね肉の照り焼き','3日前から保存可。脂質が少なくたんぱく質が豊富。そのままでも冷蔵保存でOK。'),
    ('かぼちゃの煮物',   '3〜4日前から保存可。糖質・ビタミン豊富。やわらかく煮れば消化しやすい。'),
    ('ほうれん草のおひたし','2〜3日前から保存可。鉄分・ビタミン補給に。だし醤油で和えるだけで簡単。'),
    ('卵焼き',          '前日夜または当日朝に作る。だし巻き卵など甘さ控えめが◎。お弁当・持参ランチにも活用できる。'),
    ('おにぎり（梅・昆布）','前夜に大量に握り、朝食・持参ランチ・翌日朝食分をまとめて準備すると効率的。'),
    ('鮭の塩焼き・煮魚', '2〜3日前から保存可。リカバリー食の主菜として活用。'),
]
for title, body in recipes:
    bp = ac.add_paragraph()
    run(bp, f'◆ {title}　', bold=True, size=8.5, color=COLOR_JITAKI)
    run(bp, body, size=8.5)
    spacing(bp, 30, 10)

doc.add_paragraph()

# ════════════ ポイント ════════════
pt = doc.add_table(rows=1, cols=1); pt.alignment = WD_TABLE_ALIGNMENT.CENTER
pc = pt.rows[0].cells[0]; cell_bg(pc, RGBColor(0xF0,0xF0,0xF0)); cell_mar(pc,100,100,150,150)
p = pc.paragraphs[0]; run(p, '【食事・補食のポイント】', bold=True, size=10, color=COLOR_TITLE_BG); spacing(p,0,30)

for title, body in [
    ('【消化負担を減らすために】',
     '食物繊維の多い食材（玄米・ゴボウ・こんにゃく・きのこ類）、脂質の多いもの（揚げ物・マヨネーズ）、生もの、乳製品は前日〜当日は避ける。白米・うどん・バナナなど消化の速い食材に絞る。'),
    ('【持参ランチの準備ポイント】',
     '6/13の持参ランチは前夜または当日朝に準備。おにぎりは夕食の白米を多めに炊いてそのまま握ると効率的。卵焼きも作り置きして一緒に持参できる。保冷剤・保冷バッグで衛生管理を徹底する。'),
    ('【摂取タイミングの鉄則】',
     '固形食はなるべくレース2〜3時間前まで。少量ずつゆっくり摂ることで胃の不快感を防ぐ。'),
    ('【試合当日に試してはいけないもの】',
     '初めて食べる食品・サプリメント・スポーツ製品は使用しない。事前に練習で試したことのあるものだけを選ぶ。'),
    ('【2日間を通じた戦略】',
     '6/13 400mのレース後夕食〜6/14の朝食が100mのパフォーマンスを左右する。帰宅後すみやかに食事をとり、十分な睡眠を確保する。'),
]:
    bp = pc.add_paragraph()
    run(bp, title, bold=True, size=8.5, color=COLOR_TITLE_BG)
    run(bp, '\n' + body, size=8.5)
    spacing(bp, 40, 20)

doc.add_paragraph()

# ════════════ 詳細テーブル ════════════
dh = doc.add_paragraph(); run(dh, '食事パターンとエネルギー・糖質量（詳細）', bold=True, size=10, color=COLOR_TITLE_BG)
dt = doc.add_table(rows=0, cols=4); dt.style = 'Table Grid'
TOTAL = RGBColor(0xEE,0xEE,0xEE)

def dt_hdr(t, texts, bg):
    row = t.add_row()
    for i, tx in enumerate(texts):
        c = row.cells[i]; cell_bg(c,bg); cell_mar(c,60,60,80,80)
        p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run(p, tx, bold=True, size=8.5, color=COLOR_WHITE)

def dt_sec(t, tx, bg):
    row = t.add_row()
    for i in range(1,4): row.cells[0].merge(row.cells[i])
    c = row.cells[0]; cell_bg(c,bg); cell_mar(c,60,60,100,100)
    p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run(p, tx, bold=True, size=9, color=COLOR_WHITE)

def dt_row(t, cat, item, kcal, carb, bg=None, bold=False):
    row = t.add_row()
    for i,(v,a) in enumerate(zip([cat,item,kcal,carb],
        [WD_ALIGN_PARAGRAPH.LEFT,WD_ALIGN_PARAGRAPH.LEFT,
         WD_ALIGN_PARAGRAPH.RIGHT,WD_ALIGN_PARAGRAPH.RIGHT])):
        c = row.cells[i]
        if bg: cell_bg(c,bg)
        cell_mar(c,40,40,80,80)
        p = c.paragraphs[0]; p.alignment = a
        run(p, v, bold=bold, size=8.5)

dt_hdr(dt, ['','内容','エネルギー(kcal)','糖質(g)'], COLOR_TBL_HDR)

# 6/12 昼食
dt_sec(dt, '6/12 昼食（外食）', COLOR_PREV)
for r in [('主食','白飯200g','300','70'),('主菜','鶏の照り焼き','180','8'),
          ('副菜','野菜料理','80','15'),('汁物','味噌汁','40','5'),('','合計','600','98')]:
    dt_row(dt,*r, bg=COLOR_PREV_LIGHT if r[0] else TOTAL, bold=not r[0])

# 6/12 夕食
dt_sec(dt, '6/12 夕食（自炊★作り置き）', COLOR_PREV)
for r in [('主食','白飯200g','300','70'),('主菜','肉じゃが★','200','25'),
          ('副菜','ほうれん草のおひたし★','50','5'),('汁物','インスタント味噌汁','40','5'),
          ('','合計','590','105')]:
    dt_row(dt,*r, bg=TOTAL if not r[0] else None, bold=not r[0])

# 6/13 朝食
dt_sec(dt, '6/13 朝食（自炊★作り置き）', COLOR_DAY1)
for r in [('主食','白飯200g','300','70'),('主菜','卵焼き★','120','3'),
          ('副菜','野菜の煮物★','80','15'),('果物','バナナ1本','100','20'),
          ('汁物','インスタント味噌汁','40','5'),('','合計','640','113')]:
    dt_row(dt,*r, bg=COLOR_DAY1_LIGHT if r[0] else TOTAL, bold=not r[0])

# 6/13 昼食
dt_sec(dt, '6/13 昼食（持参またはコンビニ）', COLOR_DAY1)
for r in [('主食','おにぎり2個（梅・昆布）★','340','80'),('主菜','卵焼き★（持参）','120','3'),
          ('果物','バナナ1本','100','20'),('飲み物','スポーツドリンク','60','15'),
          ('','合計','620','118')]:
    dt_row(dt,*r, bg=TOTAL if not r[0] else None, bold=not r[0])

# 6/13 補食
dt_sec(dt, '6/13 補食（レース前）', COLOR_DAY1)
for r in [('補食①','エネルギーゼリー','180','35'),('アップ中','スポーツドリンク','60','15'),
          ('レース前','羊羹/タブレット（任意）','40','10'),('','合計','280','60')]:
    dt_row(dt,*r, bg=COLOR_DAY1_LIGHT if r[0] else TOTAL, bold=not r[0])

# 6/13 夕食
dt_sec(dt, '6/13 夕食（自炊★作り置き・翌日100m準備）', COLOR_DAY1)
for r in [('主食','白飯200g（多め）','300','70'),
          ('主菜','鶏むね肉の照り焼き★','160','5'),
          ('副菜','かぼちゃの煮物★','130','30'),
          ('汁物','インスタント味噌汁','40','5'),('','合計','630','110')]:
    dt_row(dt,*r, bg=TOTAL if not r[0] else None, bold=not r[0])

# 6/14 朝食
dt_sec(dt, '6/14 朝食（自炊★前夜仕込み）', COLOR_DAY2)
for r in [('主食','おにぎり1個（前夜に握る★）','200','50'),
          ('果物','バナナ1本','100','20'),
          ('乳製品','フルーツヨーグルト','120','20'),
          ('飲み物','オレンジジュース','90','20'),('','合計','510','110')]:
    dt_row(dt,*r, bg=COLOR_DAY2_LIGHT if r[0] else TOTAL, bold=not r[0])

# 6/14 補食
dt_sec(dt, '6/14 補食（レース前）', COLOR_DAY2)
for r in [('補食①','エネルギーゼリー','180','35'),('アップ中','スポーツドリンク','60','15'),
          ('レース前','羊羹/タブレット（任意）','40','10'),('','合計','280','60')]:
    dt_row(dt,*r, bg=TOTAL if not r[0] else None, bold=not r[0])

# 6/14 夕食
dt_sec(dt, '6/14 夕食（自炊★作り置き・リカバリー）', COLOR_DAY2)
for r in [('主食','白飯または雑穀米','300','65'),
          ('主菜','鮭の塩焼き★','150','0'),
          ('副菜','野菜の煮物★（ひじき等）','80','10'),
          ('汁物','具沢山の味噌汁（豆腐・わかめ）','60','7'),('','合計','590','82')]:
    dt_row(dt,*r, bg=COLOR_DAY2_LIGHT if r[0] else TOTAL, bold=not r[0])

# 合計
dt_sec(dt, 'エネルギー・糖質 合計', COLOR_TITLE_BG)
for r in [('6/12合計','（昼食＋夕食）','1190','203'),
          ('6/13合計','（朝食＋昼食＋補食＋夕食）','2170','401'),
          ('6/14合計','（朝食＋補食）','790','170')]:
    dt_row(dt,*r, bg=COLOR_ORANGE_LIGHT, bold=True)

col_widths(dt, [2.0, 7.0, 3.5, 3.5])

output = '/home/user/AK/試合当日食事プラン_61kg_6月13-14日_修正版.docx'
doc.save(output)
print(f'保存完了: {output}')
