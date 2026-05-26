"""
create_ppt_proposal.py
パラ陸上 栄養サポート計画 提案書をPowerPoint形式で作成。
"""
from pptx import Presentation
from pptx.util import Cm, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Cm
from pptx.oxml.ns import qn
from lxml import etree
import copy

prs = Presentation()
prs.slide_width  = Cm(33.87)
prs.slide_height = Cm(19.05)

# ── カラー定数 ────────────────────────────────────────────────
NAVY   = RGBColor(0x1E, 0x3A, 0x5F)
BLUE   = RGBColor(0x25, 0x63, 0xEB)
GREEN  = RGBColor(0x16, 0xA3, 0x4A)
RED    = RGBColor(0xDC, 0x26, 0x26)
ORANGE = RGBColor(0xEA, 0x58, 0x0C)
PURPLE = RGBColor(0x93, 0x33, 0xEA)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
GRAY   = RGBColor(0xF1, 0xF5, 0xF9)
DGRAY  = RGBColor(0x64, 0x74, 0x8B)
DARK   = RGBColor(0x1E, 0x29, 0x3B)
LBLUE  = RGBColor(0xDB, 0xEA, 0xFE)
LGREEN = RGBColor(0xDC, 0xFC, 0xE7)
LRED   = RGBColor(0xFE, 0xE2, 0xE2)
LYELLOW= RGBColor(0xFE, 0xF9, 0xC3)
LPURP  = RGBColor(0xF3, 0xE8, 0xFF)
LORANG = RGBColor(0xFF, 0xF7, 0xED)

W = prs.slide_width
H = prs.slide_height
BLANK = prs.slide_layouts[6]

def cm(v): return Cm(v)
def rgb(*args): return RGBColor(*args)

def add_shape(slide, l, t, w, h, fill, line=None, lw=None):
    s = slide.shapes.add_shape(1, l, t, w, h)
    s.fill.solid(); s.fill.fore_color.rgb = fill
    if line:
        s.line.color.rgb = line
        s.line.width = Pt(lw or 1)
    else:
        s.line.fill.background()
    return s

def add_rr(slide, l, t, w, h, fill, adj=0.05, line=None):
    s = slide.shapes.add_shape(5, l, t, w, h)
    s.fill.solid(); s.fill.fore_color.rgb = fill
    s.adjustments[0] = adj
    if line:
        s.line.color.rgb = line; s.line.width = Pt(1)
    else:
        s.line.fill.background()
    return s

def txb(slide, text, l, t, w, h, size=11, bold=False, color=DARK,
        align=PP_ALIGN.LEFT, wrap=True, italic=False, fname='メイリオ'):
    box = slide.shapes.add_textbox(l, t, w, h)
    tf = box.text_frame; tf.word_wrap = wrap
    lines = text.split('\n')
    for li, line in enumerate(lines):
        p = tf.paragraphs[0] if li == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_before = Pt(0); p.space_after = Pt(1)
        run = p.add_run(); run.text = line
        run.font.size = Pt(size); run.font.bold = bold
        run.font.color.rgb = color; run.font.name = fname
        run.font.italic = italic
    return box

def set_txt_in_shape(shape, text, size=10, bold=False, color=WHITE,
                      align=PP_ALIGN.CENTER, fname='メイリオ'):
    tf = shape.text_frame; tf.word_wrap = True
    for i, para in enumerate(tf.paragraphs):
        for run in para.runs: run.text = ''
    lines = text.split('\n')
    p0 = tf.paragraphs[0]; p0.alignment = align
    p0.space_before = Pt(0); p0.space_after = Pt(0)
    for li, line in enumerate(lines):
        if li == 0:
            r = p0.add_run()
        else:
            br = etree.SubElement(p0._p, qn('a:br'))
            etree.SubElement(br, qn('a:rPr'), attrib={'lang': 'ja-JP'})
            r = p0.add_run()
        r.text = line; r.font.size = Pt(size)
        r.font.bold = bold; r.font.color.rgb = color; r.font.name = fname

def header_bar(slide, title, sub=None):
    """上部タイトルバー"""
    add_shape(slide, 0, 0, W, cm(1.6), NAVY)
    add_shape(slide, 0, cm(1.6), W, cm(0.12), BLUE)
    txb(slide, title, cm(0.6), cm(0.1), W-cm(8), cm(1.5),
        size=20, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
    if sub:
        txb(slide, sub, W-cm(7.5), cm(0.3), cm(7), cm(1.1),
            size=10, color=RGBColor(0x93,0xC5,0xFD), align=PP_ALIGN.RIGHT)

def bullet_box(slide, l, t, w, h, title, items, title_color=BLUE,
               bg=GRAY, item_size=10, title_size=12):
    """タイトル付き箇条書きボックス"""
    s = add_rr(slide, l, t, w, h, bg)
    add_shape(slide, l, t, w, cm(0.6), title_color)
    txb(slide, title, l+cm(0.2), t+cm(0.04), w-cm(0.4), cm(0.55),
        size=title_size, bold=True, color=WHITE)
    y_off = cm(0.7)
    for item in items:
        txb(slide, '・'+item, l+cm(0.25), t+y_off, w-cm(0.4),
            cm(0.5+item.count('\n')*0.4),
            size=item_size, color=DARK)
        y_off += cm(0.48 + item.count('\n')*0.4)

def tag(slide, l, t, text, color=BLUE):
    """小タグ"""
    s = add_rr(slide, l, t, cm(2.4), cm(0.55), color, adj=0.3)
    set_txt_in_shape(s, text, size=9, bold=True)

# =========================================================================
# スライド 1：タイトル
# =========================================================================
sl = prs.slides.add_slide(BLANK)
add_shape(sl, 0, 0, W, H, NAVY)
add_shape(sl, 0, cm(5.5), W, cm(8.0), BLUE)
add_shape(sl, 0, cm(5.5), cm(0.5), cm(8.0), RED)

txb(sl, 'パラ陸上 栄養サポート計画', cm(1.2), cm(5.8), W-cm(2), cm(2.2),
    size=36, bold=True, color=WHITE, align=PP_ALIGN.LEFT)
txb(sl, '2026年6月〜2027年3月', cm(1.2), cm(8.2), W-cm(2), cm(1.2),
    size=20, color=RGBColor(0xBF,0xDB,0xFF), align=PP_ALIGN.LEFT)
txb(sl, '🏆 アジア大会（愛知・10月18〜24日）を見据えた計画',
    cm(1.2), cm(9.5), W-cm(2), cm(1.0),
    size=15, color=RGBColor(0xFD,0xBA,0x74), align=PP_ALIGN.LEFT)
txb(sl, '管理栄養士　小池 ●●', cm(1.2), cm(11.5), W-cm(2), cm(0.8),
    size=13, color=RGBColor(0x93,0xC5,0xFD), align=PP_ALIGN.LEFT)

# =========================================================================
# スライド 2：目次
# =========================================================================
sl = prs.slides.add_slide(BLANK)
add_shape(sl, 0, 0, W, H, RGBColor(0xF8,0xFA,0xFF))
header_bar(sl, '本日の内容', '栄養サポート計画 提案書')

items_toc = [
    (NAVY,   '1',  'これまでの取り組み',        '12月・4月の2回の講義実績'),
    (RED,    '2',  '現状の課題（5点）',          '食事調査・アンケートから見えた競技団体の課題'),
    (BLUE,   '3',  '年間サポート計画',           '2026年6月〜2027年3月のスケジュール'),
    (GREEN,  '4',  'コンディション記録の活用',   '食事×コンディションデータの分析・活用法'),
    (ORANGE, '5',  'アジア大会 食環境整備',      '事前準備〜大会中のサポート体制'),
    (PURPLE, '6',  '課題別 解決策まとめ',        '5つの課題に対する具体的な対応策'),
]

for i, (col, num, title, sub) in enumerate(items_toc):
    row = i // 2; col_idx = i % 2
    lx = cm(1.0) + col_idx * cm(16.0)
    ty = cm(2.3) + row * cm(4.5)
    s = add_rr(sl, lx, ty, cm(15.5), cm(4.0), WHITE, line=col)
    add_shape(sl, lx, ty, cm(1.1), cm(4.0), col)
    txb(sl, num, lx, ty+cm(1.2), cm(1.1), cm(1.6),
        size=22, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    txb(sl, title, lx+cm(1.3), ty+cm(0.5), cm(14.0), cm(1.2),
        size=15, bold=True, color=col)
    txb(sl, sub, lx+cm(1.3), ty+cm(1.8), cm(14.0), cm(1.5),
        size=10, color=DGRAY)

# =========================================================================
# スライド 3：これまでの取り組み
# =========================================================================
sl = prs.slides.add_slide(BLANK)
add_shape(sl, 0, 0, W, H, RGBColor(0xF8,0xFA,0xFF))
header_bar(sl, '1. これまでの取り組み', '本計画の位置づけ')

phases = [
    (cm(1.0),  '2025年12月',  '食事バランスに関する講義',
     '・「5つのお皿」をそろえることの重要性\n・食品群の摂り方の基礎\n・食事調査結果の活用方法',
     RGBColor(0x47,0x55,0x69), RGBColor(0xE2,0xE8,0xF0), '実施済み'),
    (cm(12.0), '2026年4月',   '食事調査 & コンディション×食事記録',
     '・3日間食事調査の実施\n・体重・疲労度・練習負荷の記録を開始\n・Excelテンプレートを配布',
     RGBColor(0x47,0x55,0x69), RGBColor(0xE2,0xE8,0xF0), '実施済み'),
    (cm(23.0), '2026年6月〜\n2027年3月', '【本計画】アジア大会に向けた\n年間栄養サポート',
     '・アジア大会（10月）を主ターゲット\n・試合期対策・記録分析・次シーズン準備',
     NAVY, LBLUE, '今後の計画'),
]

# 矢印接続
for i in range(2):
    lx = cm(10.5) + i*cm(11.0)
    add_shape(sl, lx, cm(9.0), cm(1.5), cm(0.8), DGRAY)
    txb(sl, '▶', lx, cm(8.8), cm(1.5), cm(0.8),
        size=18, color=DGRAY, align=PP_ALIGN.CENTER)

for lx, period, title, content, tc, bg, badge in phases:
    bw = cm(10.5)
    s_card = add_rr(sl, lx, cm(2.5), bw, cm(14.0), bg, line=tc)
    # 上部カラーバー
    add_shape(sl, lx, cm(2.5), bw, cm(0.7), tc)
    # バッジ
    b = add_rr(sl, lx+bw-cm(2.8), cm(2.0), cm(2.6), cm(0.7), tc, adj=0.4)
    set_txt_in_shape(b, badge, size=9, bold=True)
    txb(sl, period, lx+cm(0.3), cm(3.3), bw-cm(0.6), cm(1.0),
        size=11, bold=True, color=tc)
    txb(sl, title, lx+cm(0.3), cm(4.5), bw-cm(0.6), cm(2.0),
        size=13, bold=True, color=tc)
    add_shape(sl, lx+cm(0.3), cm(6.7), bw-cm(0.6), cm(0.04), DGRAY)
    txb(sl, content, lx+cm(0.3), cm(7.0), bw-cm(0.6), cm(8.5),
        size=11, color=DARK)

# =========================================================================
# スライド 4：課題（1〜3）
# =========================================================================
sl = prs.slides.add_slide(BLANK)
add_shape(sl, 0, 0, W, H, RGBColor(0xF8,0xFA,0xFF))
header_bar(sl, '2. 現状の課題（1〜3）', '食事調査・アンケート結果から')

challenges_a = [
    (RED, '課題①', 'エネルギー・栄養素摂取量の最適化',
     ['炭水化物：男性5.1 g/kg BW・女性4.7 g/kg BW\n（健常競技者推奨 3〜10 g/kg BW）',
      'たんぱく質：男女ともに1.4 g/kg BW\n（競技者推奨 1.2〜2.0 g/kg BW）',
      'カルシウム：男性615 mg / 女性596 mg（推奨値に未達）',
      '食物繊維：男性16.3 g / 女性15.9 g（目安量に未達）',
      '→各種目・クラスの最適量を個別サポートで蓄積'],
     '課題①'),
    (ORANGE, '課題②', 'ウエイトコントロールの知識・スキル',
     ['増量・減量に課題を抱える選手が多い（アンケートで関心上位）',
      '目標エネルギー量の設定が難しい\n→食事調査結果からの増減で個別対応',
      '義足が合わなくなるなどパラアスリート特有の課題あり',
      '→基本的なウエイトコントロールを講義で解説'],
     '課題②'),
    (BLUE, '課題③', '試合期・遠征時の食事管理',
     ['アンケートで「試合期の栄養補給」へのニーズが最上位',
      '海外遠征（インド大会）で体重が大幅に減少した選手の実例あり',
      'アジア大会（愛知）では各試合時間に応じた\n食事タイミングの把握が必要',
      '→会場周辺の食環境マップを事前に作成・配布'],
     '課題③'),
]

for i, (col, num, title, items, badge) in enumerate(challenges_a):
    lx = cm(0.8) + i*cm(11.0)
    s = add_rr(sl, lx, cm(2.3), cm(10.5), cm(15.2), WHITE, line=col)
    add_shape(sl, lx, cm(2.3), cm(10.5), cm(0.7), col)
    b = add_rr(sl, lx+cm(7.8), cm(1.75), cm(2.5), cm(0.65), col, adj=0.4)
    set_txt_in_shape(b, badge, size=9, bold=True)
    txb(sl, title, lx+cm(0.25), cm(3.2), cm(10.0), cm(1.3),
        size=12, bold=True, color=col)
    y = cm(4.7)
    for item in items:
        txb(sl, '・'+item, lx+cm(0.25), y, cm(10.0),
            cm(0.5+item.count('\n')*0.45), size=9.5, color=DARK)
        y += cm(0.48+item.count('\n')*0.45) + cm(0.3)

# =========================================================================
# スライド 5：課題（4〜5）
# =========================================================================
sl = prs.slides.add_slide(BLANK)
add_shape(sl, 0, 0, W, H, RGBColor(0xF8,0xFA,0xFF))
header_bar(sl, '2. 現状の課題（4〜5）', '食事調査・アンケート結果から')

challenges_b = [
    (GREEN, '課題④', 'コンディション記録の活用方法が不明確',
     ['2026年4月からコンディション×食事の記録を開始',
      '→ データの見方・活かし方の指導が未実施',
      '選手自身がデータを解釈→\n食事調整できる自立が長期的目標',
      '→ 6月にExcelテンプレートと分析方法を提供'],
     'コンディション'),
    (PURPLE, '課題⑤', 'サプリメントの適正使用',
     ['9割以上の選手がサプリメントを使用',
      '情報源：指導者・チームメイト・SNSに偏る\n（管理栄養士から情報提供の機会が少ない）',
      'アンチドーピング対応製品の選び方や\n使用タイミング・用量の知識が不足',
      '→ 12月講義でサプリメント適正使用を指導'],
     'サプリメント'),
]

for i, (col, num, title, items, badge) in enumerate(challenges_b):
    lx = cm(1.5) + i*cm(16.0)
    s = add_rr(sl, lx, cm(2.3), cm(15.0), cm(15.2), WHITE, line=col)
    add_shape(sl, lx, cm(2.3), cm(15.0), cm(0.7), col)
    b = add_rr(sl, lx+cm(11.5), cm(1.75), cm(3.2), cm(0.65), col, adj=0.4)
    set_txt_in_shape(b, badge, size=9, bold=True)
    txb(sl, f'{num}　{title}', lx+cm(0.3), cm(3.2), cm(14.4), cm(1.3),
        size=13, bold=True, color=col)
    y = cm(4.7)
    for item in items:
        txb(sl, '・'+item, lx+cm(0.3), y, cm(14.2),
            cm(0.55+item.count('\n')*0.45), size=11, color=DARK)
        y += cm(0.55+item.count('\n')*0.45) + cm(0.35)

# =========================================================================
# スライド 6：年間計画 タイムライン
# =========================================================================
sl = prs.slides.add_slide(BLANK)
add_shape(sl, 0, 0, W, H, RGBColor(0xF8,0xFA,0xFF))
header_bar(sl, '3. 年間サポート計画', '2026年6月〜2027年3月')

# タイムライン軸
AXIS_Y = cm(13.5)
add_shape(sl, cm(0.5), AXIS_Y, W-cm(1.0), cm(0.2), NAVY)

timeline_items = [
    # (表示月, color, 上下, バブルテキスト, 高さcm)
    ('6月',    GREEN,  'up',   'PDF送付\nコンディション\n記録活用',      3.5),
    ('7月',    GREEN,  'down', 'PDF送付\nアジア大会\n栄養戦略',          3.5),
    ('8月',    GREEN,  'up',   'PDF送付\n直前食事\n計画',                3.0),
    ('9/16-20',ORANGE, 'down', '★強化合宿\n直接指導\n試合プロトコル',    4.0),
    ('10/18-24',RED,   'up',   '🏆アジア\n大会\n（愛知）',               3.5),
    ('10月後半',GREEN, 'down', 'PDF送付\n大会後\n回復栄養',              3.5),
    ('11月',   GREEN,  'up',   'PDF送付\nオフシーズン\n体組成管理',      3.5),
    ('12月',   ORANGE, 'down', '★研修会\n直接指導\n記録FB',              4.0),
    ('1〜2月', ORANGE, 'up',   '★合宿\n直接指導\n個人計画',             3.5),
    ('3月',    GREEN,  'down', 'PDF送付\n新シーズン\n準備',              3.0),
]

N = len(timeline_items)
cell_w = (W - cm(1.0)) / N
bub_w  = cell_w - cm(0.3)

for i, (month, col, direction, label, bh) in enumerate(timeline_items):
    cx = cm(0.5) + cell_w * i + cell_w / 2
    lx = cx - bub_w / 2

    # 月ラベル
    m_shape = add_rr(sl, cx-cell_w/2+cm(0.15), AXIS_Y+cm(0.25),
                     cell_w-cm(0.3), cm(0.9), col, adj=0.3)
    set_txt_in_shape(m_shape, month, size=8, bold=True)

    if direction == 'up':
        bubble_t = AXIS_Y - cm(bh) - cm(0.9)
        conn_y1  = bubble_t + cm(bh)
        conn_y2  = AXIS_Y
    else:
        bubble_t = AXIS_Y + cm(1.2)
        conn_y1  = AXIS_Y + cm(1.15)
        conn_y2  = bubble_t

    # コネクタ
    add_shape(sl, cx-cm(0.04), min(conn_y1,conn_y2),
              cm(0.08), abs(conn_y2-conn_y1), col)

    # バブル
    b = add_rr(sl, lx, bubble_t, bub_w, cm(bh), col, adj=0.07)
    set_txt_in_shape(b, label, size=8, bold=True, align=PP_ALIGN.CENTER)

# 凡例
leg_items = [
    (ORANGE, '★ 直接指導（研修会・合宿）'),
    (GREEN,  'PDF資料送付'),
    (RED,    '🏆 アジア大会'),
]
lx = cm(1.0)
for col, lbl in leg_items:
    s = add_rr(sl, lx, H-cm(1.0), cm(0.6), cm(0.6), col, adj=0.3)
    txb(sl, lbl, lx+cm(0.7), H-cm(1.1), cm(5.0), cm(0.8),
        size=9, color=DARK)
    lx += cm(6.0)

# =========================================================================
# スライド 7：年間計画 詳細（前半）
# =========================================================================
sl = prs.slides.add_slide(BLANK)
add_shape(sl, 0, 0, W, H, RGBColor(0xF8,0xFA,0xFF))
header_bar(sl, '3. 年間計画 詳細（前半）', '2026年6月〜10月')

plan_a = [
    ('2026年\n6月', GREEN,  'PDF送付', 'コンディション記録\n活用ガイド',
     '①食事調査結果の活かし方・コンディション記録の分析方法\n②個人目標の設定（体重管理・コンディション）', '③④'),
    ('2026年\n7月', GREEN,  'PDF送付', 'アジア大会\n栄養戦略',
     '①大会に向けた月別栄養計画\n②試合前後の食事の基礎\n③夏季・高温環境の水分・電解質管理', '①③'),
    ('2026年\n8月', GREEN,  'PDF送付', '大会直前\n食事計画',
     '①週別カウントダウン食事計画\n②コンビニ・外食の上手な使い方\n③腸内環境ケア（食物繊維・発酵食品）', '①③'),
    ('9/16-20\n強化合宿', ORANGE, '★直接指導', '試合プロトコル\n食環境整備',
     '①試合当日の食事タイムライン\n②補食リスト・会場周辺食環境マップ（愛知）\n③水分・電解質管理（体重測定による脱水チェック）', '③'),
    ('10/18-24\nアジア大会', RED, '大会期間', '食環境整備\n個別サポート',
     '①個別サポート選手のコンディション確認\n②緊急相談窓口（現地または遠隔）', '③'),
]

cols_w = [cm(3.2), cm(2.8), cm(3.0), cm(12.5), cm(2.0)]
headers = ['時期', '方法', 'テーマ', '内容', '課題']
COL_POS = [cm(0.3)]
for w in cols_w[:-1]: COL_POS.append(COL_POS[-1]+w)

# ヘッダー行
for j, (h, w) in enumerate(zip(headers, cols_w)):
    s = add_shape(sl, COL_POS[j], cm(2.1), w, cm(0.65), NAVY)
    txb(sl, h, COL_POS[j]+cm(0.1), cm(2.15), w-cm(0.2), cm(0.55),
        size=9, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

row_h = cm(3.1)
for ri, (period, col, method, theme, content, kadai) in enumerate(plan_a):
    ry = cm(2.8) + ri * row_h
    bg = LORANG if '直接' in method else (LRED if '大会' in method else LGREEN)
    for j, (val, w) in enumerate(zip(
            [period, method, theme, content, kadai], cols_w)):
        s = add_rr(sl, COL_POS[j], ry, w, row_h-cm(0.08), bg if j>0 else col, adj=0.02)
        if j == 0:
            set_txt_in_shape(s, val, size=9, bold=True)
        else:
            fc = col if j==1 else (DARK if j==3 else BLUE)
            txb(sl, val, COL_POS[j]+cm(0.12), ry+cm(0.1), w-cm(0.24),
                row_h-cm(0.2), size=9 if j==3 else 10,
                bold=(j==1 or j==2), color=fc)

# =========================================================================
# スライド 8：年間計画 詳細（後半）
# =========================================================================
sl = prs.slides.add_slide(BLANK)
add_shape(sl, 0, 0, W, H, RGBColor(0xF8,0xFA,0xFF))
header_bar(sl, '3. 年間計画 詳細（後半）', '2026年10月〜2027年3月')

plan_b = [
    ('2026年\n10月', GREEN,  'PDF送付', '大会後回復栄養\nコンディション中間分析',
     '①大会後の疲労・炎症回復食（抗酸化・たんぱく質）\n②4〜9月の記録の中間集計・個人フィードバック\n③オフシーズン移行期のエネルギー量見直し', '①④'),
    ('2026年\n11月', GREEN,  'PDF送付', 'オフシーズン\n体組成管理',
     '①増量・体組成管理戦略（筋量↑・体脂肪↓）\n②冬季の免疫栄養（ビタミンD・C・亜鉛）\n③カルシウム・ビタミンD摂取ガイド（骨強化）', '①②'),
    ('2026年\n12月\n研修会・合宿', ORANGE, '★直接指導', '記録データ活用講義\n個人栄養評価',
     '①4〜12月の記録の分析・全体フィードバック\n②データの読み方・パターン発見（疲労×体重×食事）\n③個人別課題の特定とアクションプラン\n④サプリメント見直し（アンチドーピング確認）', '④⑤'),
    ('2027年\n1〜2月\n合宿', ORANGE, '★直接指導', '次シーズン\n個人栄養計画立案',
     '①個人データを使った栄養計画立案ワーク\n②試合期・オフ期の食事切り替えロードマップ\n③自炊スキルアップ実践ワーク', '①②⑤'),
    ('2027年\n3月', GREEN,  'PDF送付', '新シーズン\n開幕準備',
     '①シーズンイン時の食事チェックリスト\n②春季大会に向けた短期コンディション調整\n③年間振り返りレポート・次年度提案書', '全課題'),
]

for j, (h, w) in enumerate(zip(headers, cols_w)):
    s = add_shape(sl, COL_POS[j], cm(2.1), w, cm(0.65), NAVY)
    txb(sl, h, COL_POS[j]+cm(0.1), cm(2.15), w-cm(0.2), cm(0.55),
        size=9, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

for ri, (period, col, method, theme, content, kadai) in enumerate(plan_b):
    ry = cm(2.8) + ri * row_h
    bg = LORANG if '直接' in method else LGREEN
    for j, (val, w) in enumerate(zip(
            [period, method, theme, content, kadai], cols_w)):
        s = add_rr(sl, COL_POS[j], ry, w, row_h-cm(0.08), bg if j>0 else col, adj=0.02)
        if j == 0:
            set_txt_in_shape(s, val, size=9, bold=True)
        else:
            fc = col if j==1 else (DARK if j==3 else BLUE)
            txb(sl, val, COL_POS[j]+cm(0.12), ry+cm(0.1), w-cm(0.24),
                row_h-cm(0.2), size=9 if j==3 else 10,
                bold=(j==1 or j==2), color=fc)

# =========================================================================
# スライド 9：コンディション×食事記録の活用
# =========================================================================
sl = prs.slides.add_slide(BLANK)
add_shape(sl, 0, 0, W, H, RGBColor(0xF8,0xFA,0xFF))
header_bar(sl, '4. コンディション×食事記録の活用方法', '選手が自分でデータを分析・食事調整できる自立を目指す')

steps = [
    (GREEN,  'STEP 1\n記録する',
     '体重・疲労度（0〜10）・睡眠時間\n睡眠の質（0〜5）・練習時間・RPE\n主食量（茶碗換算）・水分量(mL)\n補食・サプリメント内容'),
    (BLUE,   'STEP 2\n週次セルフチェック',
     '体重が2日以上↓ → 主食を追加\n高疲労（7以上）＋前日の主食少→炭水化物補給\n高負荷翌日に体重-1kg→回復食・水分強化\n就寝2h前の食事→睡眠の質と照合'),
    (ORANGE, 'STEP 3\n月次グラフで確認',
     '【グラフ①】体重推移＋疲労度\n→エネルギー不足の時期を特定\n\n【グラフ②】週練習負荷＋主食量\n→炭水化物が負荷に追いついているか確認'),
    (PURPLE, 'STEP 4\n管理栄養士に共有',
     '月1回LINEで体重グラフ・\n高疲労週の食事内容を送付\n→個別フィードバックを返す\n\n合宿時に記録データを持参\n→直接分析ワークを実施'),
]

for i, (col, title, content) in enumerate(steps):
    lx = cm(0.6) + i*cm(8.2)
    # 矢印（最後以外）
    if i < 3:
        txb(sl, '▶', lx+cm(7.6), cm(8.5), cm(0.8), cm(1.5),
            size=20, color=DGRAY, align=PP_ALIGN.CENTER)
    s = add_rr(sl, lx, cm(2.3), cm(7.8), cm(15.0), col, adj=0.04)
    add_shape(sl, lx, cm(2.3), cm(7.8), cm(1.8), col)
    set_txt_in_shape(add_rr(sl, lx, cm(2.3), cm(7.8), cm(1.8), col),
                     title, size=11, bold=True)
    txb(sl, content, lx+cm(0.2), cm(4.4), cm(7.4), cm(12.0),
        size=10, color=DARK)

# Excelツール案内
s_tool = add_rr(sl, cm(0.5), H-cm(1.2), W-cm(1.0), cm(1.0),
                LBLUE, line=BLUE)
txb(sl, '📊 Excelテンプレート（体重×疲労グラフ自動生成）は6月に選手全員へ配布予定',
    cm(1.0), H-cm(1.15), W-cm(2.0), cm(0.9),
    size=11, bold=True, color=BLUE, align=PP_ALIGN.LEFT)

# =========================================================================
# スライド 10：アジア大会 食環境整備
# =========================================================================
sl = prs.slides.add_slide(BLANK)
add_shape(sl, 0, 0, W, H, RGBColor(0xF8,0xFA,0xFF))
header_bar(sl, '5. アジア大会（愛知）食環境整備', '10月18〜24日 ｜ 9月16〜20日 強化合宿で直接指導')

# 左：事前準備
s_pre = add_rr(sl, cm(0.5), cm(2.2), cm(16.0), cm(15.5), WHITE, line=ORANGE)
add_shape(sl, cm(0.5), cm(2.2), cm(16.0), cm(0.8), ORANGE)
txb(sl, '〜8月 事前準備', cm(0.7), cm(2.25), cm(15.6), cm(0.7),
    size=13, bold=True, color=WHITE)

pre_items = [
    ('📍 食環境マップ作成', '会場（ポートメッセなごや）周辺の\nコンビニ・スーパー・飲食店マップをPDF化'),
    ('🍱 補食リスト作成',   '持参推奨食品リスト\nおにぎり・バナナ・カステラ・ゼリー飲料・スポーツドリンク等'),
    ('⏰ 食事タイムライン', '試合スケジュール別の食事タイムライン例\n（1日1試合・複数試合・勝ち上がり想定）を作成'),
    ('⚠️ 個別対応確認',     'アレルギー・宗教上の食事制限がある\n選手への対応リストを指導者と連携して確認'),
]
y = cm(3.3)
for icon_title, desc in pre_items:
    s = add_rr(sl, cm(0.8), y, cm(15.4), cm(2.8), RGBColor(0xFF,0xF7,0xED), line=ORANGE)
    txb(sl, icon_title, cm(1.0), y+cm(0.15), cm(15.0), cm(0.9),
        size=10, bold=True, color=ORANGE)
    txb(sl, desc, cm(1.0), y+cm(0.95), cm(15.0), cm(1.6),
        size=9.5, color=DARK)
    y += cm(3.0)

# 右：大会中サポート
s_dur = add_rr(sl, cm(17.0), cm(2.2), cm(16.3), cm(15.5), WHITE, line=RED)
add_shape(sl, cm(17.0), cm(2.2), cm(16.3), cm(0.8), RED)
txb(sl, '10/18〜24 大会期間中サポート', cm(17.2), cm(2.25), cm(16.0), cm(0.7),
    size=13, bold=True, color=WHITE)

dur_items = [
    (ORANGE, '★帯同できる場合',
     ['試合間の補食提供・水分補給の確認', 'コンディション記録のサポート', '翌試合に向けた食事アドバイスを個別提供']),
    (BLUE, '遠隔サポートの場合',
     ['LINEグループで随時相談受付', '体重チェックを毎朝促す（メッセージ送信）', '翌日の食事アドバイスをLINEで送信']),
    (RED, '体重管理ルール',
     ['毎朝起床後・排尿後に体重測定', '前日比 −1 kg超 → 積極的な水分・電解質補給']),
    (GREEN, '試合後の回復食',
     ['たんぱく質 20〜30 g + 炭水化物 60 g以上', '試合終了後 30〜60分以内に摂取']),
]
y = cm(3.3)
for col, title, items in dur_items:
    bh = cm(0.6 + len(items) * 0.85)
    s = add_rr(sl, cm(17.3), y, cm(15.7), bh, RGBColor(0xFF,0xEE,0xEE) if col==RED else WHITE, line=col)
    add_shape(sl, cm(17.3), y, cm(15.7), cm(0.55), col)
    txb(sl, title, cm(17.5), y+cm(0.05), cm(15.3), cm(0.5),
        size=10, bold=True, color=WHITE)
    yi = y + cm(0.65)
    for item in items:
        txb(sl, '・'+item, cm(17.5), yi, cm(15.3), cm(0.75), size=9.5, color=DARK)
        yi += cm(0.8)
    y += bh + cm(0.2)

# =========================================================================
# スライド 11：課題別解決策まとめ
# =========================================================================
sl = prs.slides.add_slide(BLANK)
add_shape(sl, 0, 0, W, H, RGBColor(0xF8,0xFA,0xFF))
header_bar(sl, '6. 課題別 解決策まとめ', '5つの課題に対する具体的なアクション')

solutions = [
    (RED,    '課題①\n栄養素不足',
     ['主食量の目安（g/kg BW）を個人別に提示（6月PDF）',
      'Ca・VitD：鮭・乳製品・小魚レシピ集（11月PDF）',
      '食物繊維：副菜の選び方ガイドを各PDF資料に掲載']),
    (ORANGE, '課題②\n体重管理',
     ['増量・減量の月別計画テンプレート（11月PDF）',
      '急速減量のリスクを講義で解説（筋量↓・疲労骨折等）',
      '体重×疲労グラフで個人フィードバック（12月講義）']),
    (BLUE,   '課題③\n試合期・遠征',
     ['大会カウントダウン食事計画（7〜8月PDF）',
      '愛知会場周辺の食環境マップ・補食リスト（8月PDF）',
      '大会中：遠隔サポート（LINE）または帯同で対応']),
    (GREEN,  '課題④\n記録の活用',
     ['コンディション記録の分析方法（6月PDF）',
      'Excelテンプレート（体重×疲労グラフ）を6月配布',
      '12月講義で全員の記録データをフィードバック']),
    (PURPLE, '課題⑤\nサプリメント',
     ['サプリメント適正使用・再教育（12月講義）',
      'アンチドーピング認証製品リストを12月PDF付録で配布',
      '管理栄養士への相談窓口の活用を促進']),
]

card_w = (W - cm(1.5)) / 5
for i, (col, title, items) in enumerate(solutions):
    lx = cm(0.5) + i * card_w
    s = add_rr(sl, lx+cm(0.1), cm(2.2), card_w-cm(0.2), cm(15.3), WHITE, line=col)
    add_shape(sl, lx+cm(0.1), cm(2.2), card_w-cm(0.2), cm(1.5), col)
    set_txt_in_shape(add_rr(sl, lx+cm(0.1), cm(2.2),
                            card_w-cm(0.2), cm(1.5), col),
                     title, size=10, bold=True)
    y = cm(4.0)
    for item in items:
        txb(sl, '・'+item, lx+cm(0.25), y, card_w-cm(0.4),
            cm(0.5+item.count('\n')*0.4), size=9, color=DARK)
        y += cm(0.52+item.count('\n')*0.4) + cm(0.3)

# =========================================================================
# スライド 12：まとめ
# =========================================================================
sl = prs.slides.add_slide(BLANK)
add_shape(sl, 0, 0, W, H, NAVY)
add_shape(sl, 0, 0, cm(0.8), H, RED)

txb(sl, 'まとめ', cm(1.5), cm(1.0), W-cm(2), cm(1.5),
    size=26, bold=True, color=WHITE)

summary_items = [
    (RED,    '🏆 最大目標',     'アジア大会（愛知・10月18〜24日）での\nベストパフォーマンスを食事からサポート'),
    (ORANGE, '★ 直接指導3回',  '9月強化合宿・12月研修会・1〜2月合宿\n→試合プロトコル・記録分析・個人計画立案'),
    (GREEN,  '📄 PDF送付 毎月', '6〜8月・10〜11月・3月\n→実践的な情報を毎月届け、日常で活かせるサポートを継続'),
    (BLUE,   '📊 記録の継続',   '4月開始のコンディション×食事記録を継続\n→蓄積データをもとに個人に合った食事戦略を構築'),
    (PURPLE, '🔬 研究・論文化', 'この競技団体初のデータとして複数論文化を予定\n（実態調査・介入研究・コンディション縦断分析等）'),
]

for i, (col, badge, content) in enumerate(summary_items):
    lx = cm(1.5) if i < 3 else cm(17.5)
    ty = cm(3.0) + (i%3) * cm(4.8)
    s = add_rr(sl, lx, ty, cm(15.0), cm(4.4),
               RGBColor(0x1E+0x10, 0x3A+0x10, 0x5F+0x10), adj=0.05, line=col)
    add_shape(sl, lx, ty, cm(0.5), cm(4.4), col)
    b = add_rr(sl, lx+cm(0.6), ty+cm(0.3), cm(4.5), cm(0.65), col, adj=0.4)
    set_txt_in_shape(b, badge, size=9, bold=True)
    txb(sl, content, lx+cm(0.7), ty+cm(1.2), cm(14.0), cm(2.8),
        size=11, color=WHITE)

txb(sl, 'ご質問・ご意見をお聞かせください',
    cm(1.0), H-cm(1.2), W-cm(2.0), cm(1.0),
    size=12, color=RGBColor(0x93,0xC5,0xFD), align=PP_ALIGN.CENTER)

# ── 保存 ─────────────────────────────────────────────────────
out = '/home/user/AK/nutrition_support_presentation.pptx'
prs.save(out)
print(f"完了: {out}")
