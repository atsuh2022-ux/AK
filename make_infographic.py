import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.gridspec as gridspec
import numpy as np

# ── Font setup ──────────────────────────────────────────────────────────────
import matplotlib.font_manager as fm

# Explicitly register and use IPA font by file path
IPA_PATHS = [
    "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf",
    "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf",
    "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf",
]
FONT_PROP = None
for fp in IPA_PATHS:
    import os
    if os.path.exists(fp):
        fm.fontManager.addfont(fp)
        FONT_PROP = fm.FontProperties(fname=fp)
        plt.rcParams['font.family'] = FONT_PROP.get_name()
        break

plt.rcParams['axes.unicode_minus'] = False

# ── Data ────────────────────────────────────────────────────────────────────
# Each item: (short_label, cond_A_label, val_A, cond_B_label, val_B, metric, section, note)
items = [
    # Section A
    ("①睡眠時間",        "<7h",      7.25, ">=7h",     6.22, "同日RPE",      "A", ""),
    ("②水分摂取量",      "<1000ml",  3.12, ">=1000ml", 3.65, "同日運動後疲労", "A", ""),
    ("③タンパク質種類数", "1〜2種",   6.62, "3種以上",  6.10, "翌日RPE",      "A", ""),
    ("④補食",            "あり",     3.61, "なし",     3.44, "翌日運動後疲労", "A", ""),
    ("⑤睡眠の質",        "良(<=2)",  3.58, "悪(>=3)", 3.52, "同日運動後疲労", "A", ""),
    # Section B
    ("⑥睡眠の質",        "不良(>=3)", 6.69, "良好(<=2)", 5.94, "翌日RPE",   "B", "p=0.021"),
    ("⑦栄養バランス",    "不良3〜4",6.64, "良好1〜2", 5.94, "翌日RPE",      "B", ""),
    ("⑧起床時コンディション","良好1〜2",3.22,"不調4〜5",4.00,"同日運動後疲労","B",""),
    ("⑨起床時コンディション","良好1〜2",6.33,"不調4〜5",5.00,"同日RPE",      "B", ""),
    # Section C
    ("⑩昼食タンパク質",  "0種",     6.89, "1種以上",  6.00, "翌日RPE",      "C", ""),
    ("⑪夕食タンパク質",  "1〜2種",  6.52, "3種以上",  6.00, "翌日RPE",      "C", ""),
    ("⑫夕食に魚",        "なし",    6.62, "あり",     6.10, "翌日RPE",      "C", ""),
    ("⑬昼食タンパク質",  "0種",     3.68, "1種以上",  3.44, "翌日運動後疲労","C", ""),
    ("⑭夕食タンパク質",  "1〜2種",  3.55, "3種以上",  3.55, "翌日運動後疲労","C", ""),
]

# Compute diffs and classify
# For items where higher condA is "worse" we want diff = condA - condB
# meaning diff > 0  ⟹ condA is higher (bad)
# We always define diff = val_A - val_B so the sign tells direction
diffs = [it[2] - it[4] for it in items]
abs_diffs = [abs(d) for d in diffs]

def classify(ad):
    if ad >= 0.5: return "★"
    if ad >= 0.3: return "◆"
    return "・"

marks = [classify(ad) for ad in abs_diffs]

# ── Colors ───────────────────────────────────────────────────────────────────
BLUE   = "#4472C4"
RED    = "#FF6B6B"
BLUE_L = "#A8C4E8"   # lighter for weak items
RED_L  = "#FFBBBB"
YELLOW_BG = "#FFFACD"
GRAY_BG   = "#404040"
HEADER_TEXT = "white"

# ── Figure layout ─────────────────────────────────────────────────────────────
FIG_W, FIG_H = 12, 18
fig = plt.figure(figsize=(FIG_W, FIG_H), facecolor='white', dpi=150)

# We'll draw everything manually using axes with specific positions
# Top area: title
# Then for each section: a section header + item rows
# Bottom: legend + note

# Total rows = 14 items + 3 section headers + 1 title-block + 1 legend
# Use a tall GridSpec

N_ITEMS = 14
N_HEADERS = 3
N_TITLE = 1
N_LEGEND = 1
N_NOTE = 1
TOTAL_ROWS = N_TITLE + N_ITEMS + N_HEADERS + N_LEGEND + N_NOTE

# Heights (relative)
title_h  = 3
header_h = 1.2
item_h   = 1.5
legend_h = 2.5
note_h   = 1.5

# Build row-height list
row_heights = [title_h]
section_order = ["A", "B", "C"]
section_labels = {
    "A": "Section A: 既存５項目",
    "B": "Section B: 新規追加（４項目）",
    "C": "Section C: タンパク質詳細（５項目）",
}
section_items = {s: [i for i, it in enumerate(items) if it[6] == s] for s in section_order}

for sec in section_order:
    row_heights.append(header_h)
    for _ in section_items[sec]:
        row_heights.append(item_h)

row_heights.append(legend_h)
row_heights.append(note_h)

total_h = sum(row_heights)
row_tops = []
y = total_h
for h in row_heights:
    row_tops.append(y)
    y -= h

def to_frac(val, total=total_h):
    return val / total

# We'll use a single axes spanning the full figure, then draw patches + text
# Actually easier: use axis-less figure with add_axes by fraction

ax_main = fig.add_axes([0, 0, 1, 1])
ax_main.set_xlim(0, 1)
ax_main.set_ylim(0, total_h)
ax_main.axis('off')

def draw_rect(ax, x0, y0_bottom, width, height, color, alpha=1.0, zorder=1):
    rect = mpatches.FancyBboxPatch(
        (x0, y0_bottom), width, height,
        boxstyle="round,pad=0.02",
        facecolor=color, edgecolor='none', alpha=alpha, zorder=zorder
    )
    ax.add_patch(rect)

def draw_plain_rect(ax, x0, y0_bottom, width, height, color, alpha=1.0, zorder=1, ec='none', lw=0):
    rect = mpatches.Rectangle(
        (x0, y0_bottom), width, height,
        facecolor=color, edgecolor=ec, linewidth=lw, alpha=alpha, zorder=zorder
    )
    ax.add_patch(rect)

# ── TITLE BLOCK ──────────────────────────────────────────────────────────────
t_top = row_tops[0]
t_h   = row_heights[0]
t_bot = t_top - t_h

# Background gradient-ish (dark navy)
draw_plain_rect(ax_main, 0, t_bot, 1.0, t_h, "#1B3A6B", zorder=1)
draw_plain_rect(ax_main, 0, t_bot, 1.0, 0.15, "#2E5FA3", zorder=2)  # bottom accent

ax_main.text(0.5, t_bot + t_h * 0.62,
             "TI選手　関連性ヒント",
             ha='center', va='center', fontsize=20, fontweight='bold',
             color='white', zorder=3)
ax_main.text(0.5, t_bot + t_h * 0.32,
             "2026/03/30 〜 05/22　各指標とパフォーマンスの関連性まとめ",
             ha='center', va='center', fontsize=11,
             color='#B8D4F0', zorder=3)

# ── BAR CHART ROWS ────────────────────────────────────────────────────────────
# Layout within each row (in x fraction):
# [0.00-0.02] margin
# [0.02-0.30] label + mark
# [0.30-0.32] gap
# [0.32-0.62] metric label (short)
# [0.62-0.95] bar area
# [0.95-1.00] diff label

BAR_X0   = 0.54
BAR_W    = 0.35
BAR_MAX  = 8.0   # max x-axis value for bars (RPE/fatigue max ≈ 7.5)
LABEL_X  = 0.01
METRIC_X = 0.33

# Track current row index (after title)
row_idx = 1

for sec in section_order:
    # Section header
    s_top = row_tops[row_idx]
    s_h   = row_heights[row_idx]
    s_bot = s_top - s_h
    draw_plain_rect(ax_main, 0, s_bot, 1.0, s_h, GRAY_BG, zorder=1)
    ax_main.text(0.5, s_bot + s_h * 0.5,
                 section_labels[sec],
                 ha='center', va='center', fontsize=12, fontweight='bold',
                 color='white', zorder=2)
    row_idx += 1

    for item_i in section_items[sec]:
        it      = items[item_i]
        label   = it[0]
        cA_lbl  = it[1]
        val_A   = it[2]
        cB_lbl  = it[3]
        val_B   = it[4]
        metric  = it[5]
        note    = it[7]
        diff    = diffs[item_i]
        ad      = abs_diffs[item_i]
        mark    = marks[item_i]

        r_top = row_tops[row_idx]
        r_h   = row_heights[row_idx]
        r_bot = r_top - r_h
        row_idx += 1

        # Row background
        if mark == "★":
            draw_plain_rect(ax_main, 0, r_bot, 1.0, r_h, YELLOW_BG, zorder=1)
        else:
            color_bg = "white" if item_i % 2 == 0 else "#F5F5F5"
            draw_plain_rect(ax_main, 0, r_bot, 1.0, r_h, color_bg, zorder=1)

        # Separator line
        ax_main.plot([0, 1], [r_bot, r_bot], color='#DDDDDD', lw=0.5, zorder=2)

        # Mark + label
        mark_color = "#C8860A" if mark == "★" else ("#555" if mark == "◆" else "#999")
        mark_str = mark + " "
        fw = 'bold' if mark == "★" else 'normal'
        fc = '#222' if mark != "・" else '#666'

        ax_main.text(LABEL_X, r_bot + r_h * 0.5,
                     mark_str + label,
                     ha='left', va='center', fontsize=9.5, fontweight=fw,
                     color=fc, zorder=3)

        # Metric label
        metric_color = "#1B3A6B" if "RPE" in metric else "#8B4513"
        ax_main.text(METRIC_X, r_bot + r_h * 0.5,
                     metric,
                     ha='left', va='center', fontsize=8.5,
                     color=metric_color, zorder=3,
                     style='italic')

        # Bars (two sub-rows within the row)
        bar_total_h = r_h * 0.38
        bar_gap     = r_h * 0.06
        # Bar A top half, Bar B bottom half
        bar_A_bot = r_bot + r_h * 0.5 + bar_gap / 2
        bar_B_bot = r_bot + r_h * 0.5 - bar_gap / 2 - bar_total_h

        # Scale bar widths
        scale = BAR_W / BAR_MAX
        w_A = val_A * scale
        w_B = val_B * scale

        col_A = BLUE   if mark != "・" else BLUE_L
        col_B = RED    if mark != "・" else RED_L

        draw_plain_rect(ax_main, BAR_X0, bar_A_bot, w_A, bar_total_h, col_A, zorder=3)
        draw_plain_rect(ax_main, BAR_X0, bar_B_bot, w_B, bar_total_h, col_B, zorder=3)

        # Value labels on bars
        ax_main.text(BAR_X0 + w_A + 0.003, bar_A_bot + bar_total_h * 0.5,
                     f"{val_A:.2f}  [{cA_lbl}]",
                     ha='left', va='center', fontsize=7.5, color='#333', zorder=4)
        ax_main.text(BAR_X0 + w_B + 0.003, bar_B_bot + bar_total_h * 0.5,
                     f"{val_B:.2f}  [{cB_lbl}]",
                     ha='left', va='center', fontsize=7.5, color='#333', zorder=4)

        # Diff annotation on right
        diff_sign = f"+{diff:.2f}" if diff > 0 else f"{diff:.2f}"
        diff_col = "#CC0000" if abs(diff) >= 0.5 else ("#E87000" if abs(diff) >= 0.3 else "#888")
        ax_main.text(0.975, r_bot + r_h * 0.5,
                     diff_sign,
                     ha='right', va='center', fontsize=9, fontweight='bold',
                     color=diff_col, zorder=4)

        # p-value note
        if note:
            ax_main.text(0.975, r_bot + r_h * 0.18,
                         f"({note})",
                         ha='right', va='center', fontsize=7,
                         color='#8B008B', zorder=4)

        # Axis tick marks (light dotted lines at values 4, 5, 6, 7)
        for tick_val in [4, 5, 6, 7]:
            tx = BAR_X0 + tick_val * scale
            ax_main.plot([tx, tx], [r_bot + r_h * 0.08, r_bot + r_h * 0.92],
                         color='#E0E0E0', lw=0.5, ls=':', zorder=2)

# ── LEGEND ───────────────────────────────────────────────────────────────────
leg_top = row_tops[row_idx]
leg_h   = row_heights[row_idx]
leg_bot = leg_top - leg_h
row_idx += 1

draw_plain_rect(ax_main, 0, leg_bot, 1.0, leg_h, "#F0F4FA", zorder=1)
ax_main.plot([0, 1], [leg_top, leg_top], color='#CCC', lw=1.0, zorder=2)

# Color legend squares
sq_y  = leg_bot + leg_h * 0.65
sq_h  = leg_h * 0.2
sq_w  = 0.025

items_leg = [
    (0.04, BLUE,  "条件A（不良側）"),
    (0.22, RED,   "条件B（良好側）"),
]
for lx, lc, lt in items_leg:
    draw_plain_rect(ax_main, lx, sq_y, sq_w, sq_h, lc, zorder=3)
    ax_main.text(lx + sq_w + 0.01, sq_y + sq_h * 0.5,
                 lt, ha='left', va='center', fontsize=9, color='#333', zorder=4)

# Symbol legend
sym_y = leg_bot + leg_h * 0.28
syms = [
    (0.04, "★", "#C8860A", "|差| >= 0.5（要注目）"),
    (0.30, "◆", "#555555", "|差| >= 0.3（参考）"),
    (0.56, "・", "#999999", "|差| < 0.3（関連弱）"),
]
for sx, sm, sc, st in syms:
    ax_main.text(sx, sym_y, sm, ha='left', va='center', fontsize=12,
                 color=sc, fontweight='bold', zorder=3)
    ax_main.text(sx + 0.035, sym_y, st, ha='left', va='center', fontsize=9,
                 color='#333', zorder=3)

# Metric color legend
ax_main.text(0.72, sq_y + sq_h * 0.5,
             "■ RPE（主観的運動強度）",
             ha='left', va='center', fontsize=8.5, color="#1B3A6B", zorder=3)
ax_main.text(0.72, sym_y,
             "■ 運動後疲労",
             ha='left', va='center', fontsize=8.5, color="#8B4513", zorder=3)

# ── NOTE ────────────────────────────────────────────────────────────────────
note_top = row_tops[row_idx]
note_h_  = row_heights[row_idx]
note_bot = note_top - note_h_

draw_plain_rect(ax_main, 0, note_bot, 1.0, note_h_, "#EEEEEE", zorder=1)
ax_main.plot([0, 1], [note_top, note_top], color='#CCC', lw=0.8, zorder=2)

ax_main.text(0.5, note_bot + note_h_ * 0.65,
             "★ |差| >= 0.5（要注目）　◆ |差| >= 0.3（参考）　・ |差| < 0.3（関連弱）　"
             "　差 = 条件A値 − 条件B値",
             ha='center', va='center', fontsize=8, color='#444', zorder=2)
ax_main.text(0.5, note_bot + note_h_ * 0.28,
             "※ 睡眠の質→翌日RPE は統計的有意差あり（p = 0.021）",
             ha='center', va='center', fontsize=8, color='#8B008B', zorder=2)

# ── X-axis reference bar at bottom of each section visible ───────────────────
# We'll add a single x-axis ruler right below title for reference — skip for cleanliness

# ── Save ─────────────────────────────────────────────────────────────────────
out_png = "/home/user/AK/TI_関連性ヒント_図式化.png"
out_pdf = "/home/user/AK/TI_関連性ヒント_図式化.pdf"

fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor='white')
fig.savefig(out_pdf, bbox_inches='tight', facecolor='white')
plt.close(fig)

import os
sz_png = os.path.getsize(out_png)
sz_pdf = os.path.getsize(out_pdf)
print(f"PNG saved: {out_png}  ({sz_png:,} bytes / {sz_png/1024:.1f} KB)")
print(f"PDF saved: {out_pdf}  ({sz_pdf:,} bytes / {sz_pdf/1024:.1f} KB)")
print("Done.")
