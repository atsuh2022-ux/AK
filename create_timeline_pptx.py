"""
create_timeline_pptx.py
年間栄養サポート計画タイムラインをPowerPoint形式で出力する。
"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Cm
import copy

# ── カラー定義 ──────────────────────────────────────────────
CPAST    = RGBColor(0x94, 0xA3, 0xB8)  # グレー（実施済み）
CDIRECT  = RGBColor(0x25, 0x63, 0xEB)  # 青（直接指導）
CPDF     = RGBColor(0x16, 0xA3, 0x4A)  # 緑（PDF）
CEVENT   = RGBColor(0xDC, 0x26, 0x26)  # 赤（大会）
CBGDARK  = RGBColor(0x1E, 0x3A, 0x5F)  # 濃紺（背景）
CWHITE   = RGBColor(0xFF, 0xFF, 0xFF)
CTEXT    = RGBColor(0x1E, 0x29, 0x3B)

# ── スライドサイズ（16:9 ワイド） ───────────────────────────
prs = Presentation()
prs.slide_width  = Cm(33.87)   # 13.33 inch
prs.slide_height = Cm(19.05)   # 7.5  inch

slide_layout = prs.slide_layouts[6]  # 空白レイアウト
slide = prs.slides.add_slide(slide_layout)

W = prs.slide_width   # EMU
H = prs.slide_height

def cm(v): return Cm(v)
def rgb(r,g,b): return RGBColor(r,g,b)

# ── ヘルパー ─────────────────────────────────────────────────
def add_rect(slide, l, t, w, h, fill_color, line_color=None, radius=None):
    shape = slide.shapes.add_shape(
        1,  # MSO_SHAPE_TYPE.RECTANGLE
        l, t, w, h
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if line_color:
        shape.line.color.rgb = line_color
        shape.line.width = Pt(0.75)
    else:
        shape.line.fill.background()
    return shape

def add_text_box(slide, text, l, t, w, h,
                 font_size=11, bold=False, color=CTEXT,
                 align=PP_ALIGN.CENTER, wrap=True, font_name='メイリオ'):
    txBox = slide.shapes.add_textbox(l, t, w, h)
    tf = txBox.text_frame
    tf.word_wrap = wrap
    tf.auto_size = None
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font_name
    return txBox

def add_rounded_rect(slide, l, t, w, h, fill_color, corner_size=Pt(8)):
    from pptx.util import Pt
    from pptx.enum.shapes import MSO_SHAPE_TYPE
    shape = slide.shapes.add_shape(
        5,  # ROUNDED_RECTANGLE
        l, t, w, h
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    # adjust rounding
    shape.adjustments[0] = 0.05
    return shape

def set_text_in_shape(shape, text, font_size=10, bold=False,
                       color=CWHITE, align=PP_ALIGN.CENTER, font_name='メイリオ'):
    tf = shape.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    # clear existing
    for para in tf.paragraphs:
        for run in para.runs:
            run.text = ''
    p = tf.paragraphs[0]
    p.alignment = align
    p.space_before = Pt(0)
    p.space_after  = Pt(0)
    # split lines
    lines = text.split('\n')
    for li, line in enumerate(lines):
        if li == 0:
            run = p.add_run()
        else:
            from pptx.oxml.ns import qn
            from lxml import etree
            br = etree.SubElement(p._p, qn('a:br'))
            rPr = etree.SubElement(br, qn('a:rPr'), attrib={'lang':'ja-JP'})
            run = p.add_run()
        run.text = line
        run.font.size = Pt(font_size)
        run.font.bold = bold
        run.font.color.rgb = color
        run.font.name = font_name

# ── レイアウト定数 ─────────────────────────────────────────
MARGIN_L = cm(0.8)
MARGIN_R = cm(0.8)
CONTENT_W = W - MARGIN_L - MARGIN_R

# タイムライン軸のY位置
AXIS_Y   = cm(9.5)
AXIS_H   = cm(0.18)

# 月ブロックのY
MONTH_Y  = cm(8.0)
MONTH_H  = cm(1.3)

# 月列数と各列幅
months_data = [
    ('12月\n2025',   CPAST,   False),
    ('4月\n2026',    CPAST,   False),
    ('6月',          CDIRECT, False),
    ('7月',          CPDF,    False),
    ('8月',          CPDF,    False),
    ('9月末\nアジア大会', CEVENT, True),
    ('10月',         CPDF,    False),
    ('11月',         CPDF,    False),
    ('12月',         CDIRECT, False),
    ('1〜2月\n2027', CDIRECT, False),
    ('3月',          CPDF,    False),
]
N = len(months_data)
CELL_W = CONTENT_W / N

def col_cx(i):
    """i番目の列の中心X"""
    return MARGIN_L + CELL_W * i + CELL_W / 2

def col_lx(i):
    return MARGIN_L + CELL_W * i

# ── 背景 ──────────────────────────────────────────────────────
bg = add_rect(slide, 0, 0, W, H, rgb(0xF8,0xFA,0xFF))

# 既往ゾーン（薄グレー）
add_rect(slide, MARGIN_L, cm(1.5),
         CELL_W * 2, H - cm(2.0),
         rgb(0xE2,0xE8,0xF0))

# 大会ゾーン（薄赤）
add_rect(slide, col_lx(5), cm(1.5),
         CELL_W, H - cm(2.0),
         rgb(0xFF,0xEE,0xEE))

# ── タイトル ─────────────────────────────────────────────────
title_box = add_rect(slide, 0, 0, W, cm(1.4), CBGDARK)
add_text_box(slide,
    '栄養サポート計画　タイムライン　2025年12月〜2027年3月',
    cm(0.5), cm(0.1), W - cm(1), cm(1.2),
    font_size=18, bold=True, color=CWHITE)

# ゾーンラベル
add_text_box(slide, '【実施済み】', MARGIN_L, cm(1.45), CELL_W*2, cm(0.6),
             font_size=10, bold=True, color=rgb(0x47,0x55,0x69))
add_text_box(slide, '《今後の計画》', col_lx(2), cm(1.45), CELL_W*6, cm(0.6),
             font_size=10, bold=True, color=CDIRECT)
add_text_box(slide, 'アジア大会\n（愛知）', col_lx(5), cm(1.45), CELL_W, cm(0.65),
             font_size=9, bold=True, color=CEVENT)

# ── 軸線 ──────────────────────────────────────────────────────
add_rect(slide, MARGIN_L, AXIS_Y, CONTENT_W, AXIS_H, CBGDARK)

# ── 月ブロック ────────────────────────────────────────────────
for i, (label, color, is_event) in enumerate(months_data):
    lx = col_lx(i) + cm(0.08)
    mw = CELL_W - cm(0.16)
    shape = add_rounded_rect(slide, lx, MONTH_Y, mw, MONTH_H, color)
    set_text_in_shape(shape, label,
                      font_size=10 if '\n' in label else 11,
                      bold=True, color=CWHITE)

# ── 活動バブル定義 ─────────────────────────────────────────────
# (列インデックス, ラベル, 色, 上下方向 'up'/'down', コネクタ長さcm)
activities = [
    (0,  '【既往①】\n食事バランス講義',             CPAST,   'down', 2.0),
    (1,  '【既往②】\nコンディション×\n食事記録を始めよう', CPAST, 'up', 2.5),
    (2,  '★記録FB＋\nアジア大会\n栄養戦略講義',      CDIRECT, 'down', 2.8),
    (3,  'アジア大会\nカウントダウン\n栄養計画（PDF）', CPDF,  'up',  2.5),
    (4,  '試合直前・大会中\nプロトコル\n食環境整備（PDF）', CPDF,'down',2.8),
    (5,  'アジア大会\n（愛知・9月末）',              CEVENT,  'up',  2.0),
    (6,  '大会後回復＆\n記録振り返り\n（PDF）',       CPDF,   'down', 2.8),
    (7,  'オフシーズン\n体組成管理\n（PDF）',         CPDF,   'up',   2.5),
    (8,  '★コンディション\n記録データ活用\n年間振り返り講義', CDIRECT,'down',2.8),
    (9,  '★次シーズン\n個人栄養計画\n立案ワーク',    CDIRECT, 'up',   2.5),
    (10, '新シーズン\n開幕準備\n（PDF）',             CPDF,   'down', 2.0),
]

BUBBLE_W = CELL_W - cm(0.2)
BUBBLE_H_BASE = cm(2.0)  # 1行あたり
LINE_W = cm(0.05)

from pptx.util import Pt as PtU
from lxml import etree
from pptx.oxml.ns import qn, nsmap

def add_connector_line(slide, x, y1, y2, color):
    """縦線を細い矩形で描く"""
    top = min(y1, y2)
    h   = abs(y2 - y1)
    shape = add_rect(slide, x - cm(0.04), top, cm(0.08), h, color)
    return shape

def add_arrow_head(slide, x, y, color, pointing_up=True):
    """▲ or ▼ の三角形（小さい矩形で代替、またはテキスト）"""
    sym = '▲' if pointing_up else '▼'
    add_text_box(slide, sym, x - cm(0.4), y - cm(0.3), cm(0.8), cm(0.4),
                 font_size=9, color=color, bold=True)

for (ci, label, color, direction, conn_len) in activities:
    cx = col_cx(ci)
    bw = BUBBLE_W
    bh = BUBBLE_H_BASE + label.count('\n') * cm(0.38)

    if direction == 'down':
        # バブルは軸の下
        bubble_t = AXIS_Y + AXIS_H + cm(0.0) + cm(conn_len) - bh
        # コネクタ上端: 軸下
        conn_y1 = AXIS_Y + AXIS_H
        conn_y2 = bubble_t
        # 矢印は下向き（バブルへ）
        add_connector_line(slide, cx, conn_y1, conn_y2, color)
        add_arrow_head(slide, cx, conn_y2, color, pointing_up=False)
    else:
        # バブルは軸の上
        bubble_t = AXIS_Y - cm(conn_len)
        conn_y1 = bubble_t + bh
        conn_y2 = AXIS_Y
        add_connector_line(slide, cx, conn_y1, conn_y2, color)
        add_arrow_head(slide, cx, conn_y2, color, pointing_up=True)

    bx = cx - bw/2
    shape = add_rounded_rect(slide, bx, bubble_t, bw, bh, color)
    set_text_in_shape(shape, label,
                      font_size=9.5 if label.count('\n') >= 2 else 10,
                      bold=True, color=CWHITE)

# ── 凡例 ─────────────────────────────────────────────────────
legend_items = [
    (CPAST,   '実施済み'),
    (CDIRECT, '★ 直接指導（強化研修会・合宿）'),
    (CPDF,    'PDF資料送付'),
    (CEVENT,  'アジア大会（愛知・9月末）'),
]
leg_y = H - cm(1.1)
leg_x = MARGIN_L
for (col, label) in legend_items:
    add_rect(slide, leg_x, leg_y + cm(0.1), cm(0.55), cm(0.55), col)
    add_text_box(slide, label,
                 leg_x + cm(0.65), leg_y, cm(3.8), cm(0.75),
                 font_size=10, color=CTEXT, align=PP_ALIGN.LEFT)
    leg_x += cm(4.6)

# ── 保存 ─────────────────────────────────────────────────────
out = '/home/user/AK/proposal_timeline_v2.pptx'
prs.save(out)
print(f"完了: {out}")
