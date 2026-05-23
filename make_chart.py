import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm
import numpy as np

# ── Font setup ──────────────────────────────────────────────────────────────
for candidate in ["Noto Sans CJK JP", "IPAexGothic", "IPAPGothic", "IPAGothic",
                  "TakaoPGothic", "VL PGothic"]:
    if any(f.name == candidate for f in fm.fontManager.ttflist):
        plt.rcParams['font.family'] = candidate
        print(f"Using font: {candidate}")
        break
else:
    print("No CJK font found — falling back to romanized labels")
    plt.rcParams['font.family'] = 'DejaVu Sans'

plt.rcParams['axes.unicode_minus'] = False

# ── Data ────────────────────────────────────────────────────────────────────
# Each entry: (section, label, cond_good_label, cond_bad_label, val_good, val_bad, metric_label, p_note)
data = [
    # Section A
    ("A", "①睡眠時間\n(→同日RPE)",
     ">=7h", "<7h",
     6.22, 7.25, "同日RPE", None),
    ("A", "②水分摂取量\n(→同日疲労)",
     ">=1000ml", "<1000ml",
     3.65, 3.12, "同日疲労", None),
    ("A", "③タンパク質種類\n(→翌日RPE)",
     "3種以上", "1〜2種",
     6.10, 6.62, "翌日RPE", None),
    ("A", "④補食\n(→翌日疲労)",
     "はい", "いいえ",
     3.61, 3.44, "翌日疲労", None),
    ("A", "⑤睡眠の質\n(→同日疲労)",
     "良(<=2)", "悪(>=3)",
     3.58, 3.52, "同日疲労", None),
    # Section B
    ("B", "⑥睡眠の質\n(→翌日RPE)",
     "良好(<=2)", "不良(>=3)",
     6.69, 5.94, "翌日RPE", "p=0.021"),
    ("B", "⑦栄養バランス\n(→翌日RPE)",
     "不良3〜4", "良好1〜2",
     6.64, 5.94, "翌日RPE", None),
    ("B", "⑧起床コンディション\n(→同日疲労)",
     "不調4〜5", "良好1〜2",
     4.00, 3.22, "同日疲労", None),
    ("B", "⑨起床コンディション\n(→同日RPE)",
     "良好1〜2", "不調4〜5",
     6.33, 5.00, "同日RPE", None),
    # Section C
    ("C", "⑩昼食タンパク質\n(→翌日RPE)",
     "1種以上", "0種",
     6.00, 6.89, "翌日RPE", None),
    ("C", "⑪夕食タンパク質\n(→翌日RPE)",
     "3種以上", "1〜2種",
     6.00, 6.52, "翌日RPE", None),
    ("C", "⑫夕食に魚\n(→翌日RPE)",
     "あり", "なし",
     6.10, 6.62, "翌日RPE", None),
    ("C", "⑬昼食タンパク質\n(→翌日疲労)",
     "1種以上", "0種",
     3.44, 3.68, "翌日疲労", None),
    ("C", "⑭夕食タンパク質\n(→翌日疲労)",
     "3種以上", "1〜2種",
     3.55, 3.55, "翌日疲労", None),
]

# ── Layout constants ─────────────────────────────────────────────────────────
COLOR_GOOD = "#4472C4"
COLOR_BAD  = "#FF6B6B"
COLOR_GOOD_LIGHT = "#A8C0E8"
COLOR_BAD_LIGHT  = "#FFB5B5"
COLOR_SEC_A = "#2F4F8F"
COLOR_SEC_B = "#8F2F2F"
COLOR_SEC_C = "#2F7A4F"
BG_STAR  = "#FFFACD"
BG_DIA   = "#F0FFF0"

SEC_COLORS = {"A": "#2F4F8F", "B": "#7B3F00", "C": "#1A5C36"}
SEC_BG     = {"A": "#EEF3FB", "B": "#FBF0EE", "C": "#EEFBF4"}
SEC_TITLES = {
    "A": "Section A　既存5項目",
    "B": "Section B　新規追加（4項目）",
    "C": "Section C　タンパク質詳細（5項目）",
}

n = len(data)
figw, figh = 13, 20
fig = plt.figure(figsize=(figw, figh), facecolor='white')

# Title block
fig.text(0.5, 0.975, "TI選手　関連性ヒント（2026/03/30〜05/22）",
         ha='center', va='top', fontsize=18, fontweight='bold', color='#1a1a2e')
fig.text(0.5, 0.957, "各指標とパフォーマンスの関連性まとめ",
         ha='center', va='top', fontsize=12, color='#555555')

# Axes occupying most of the figure
ax = fig.add_axes([0.01, 0.05, 0.98, 0.89])
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

# We'll draw everything manually in axes-fraction coordinates
# Build row positions: sections separated by gaps
section_gap = 0.018
row_h = 0.044       # height per data row
header_h = 0.030    # section header height
margin_top = 0.0    # start from top

# Count rows: 5 + 4 + 5 = 14 rows, 3 headers, 2 gaps between sections
total_height = 3 * header_h + 14 * row_h + 2 * section_gap
scale = 0.97 / total_height   # normalize so everything fits

def norm_h(h):
    return h * scale

# Build list of drawing instructions
instructions = []  # (type, section, item_idx_or_None, y_top)
y = 0.985
sections_order = ["A", "B", "C"]
item_idx = 0
for si, sec in enumerate(sections_order):
    instructions.append(("header", sec, None, y))
    y -= norm_h(header_h)
    for row in data:
        if row[0] == sec:
            instructions.append(("row", sec, item_idx, y))
            y -= norm_h(row_h)
            item_idx += 1
    if si < 2:
        y -= norm_h(section_gap)

# ── Bar chart area ────────────────────────────────────────────────────────────
# x layout (in axes 0-1):
#   0.00–0.32  label
#   0.32–0.62  good bar  (right-anchored at 0.32, grows right to 0.62 max)
#   0.62–0.92  bad bar   (right-anchored at 0.62, grows right to 0.92 max)
#   0.92–1.00  diff annotation

LABEL_X   = 0.00
LABEL_W   = 0.30
BAR_GOOD_START = 0.30
BAR_BAD_START  = 0.61
BAR_MAX_W = 0.29   # max bar width
DIFF_X    = 0.91

# Value ranges for RPE: ~5.0–7.5, fatigue: ~3.0–4.2
# Normalize each row's bars to their metric type
def bar_width(val, metric):
    if "RPE" in metric:
        lo, hi = 4.5, 8.0
    else:
        lo, hi = 2.8, 4.5
    frac = (val - lo) / (hi - lo)
    frac = max(0.05, min(1.0, frac))
    return frac * BAR_MAX_W

row_h_px = norm_h(row_h)

for instr in instructions:
    kind, sec, idx, y_top = instr

    if kind == "header":
        # Draw section header rectangle
        rect = mpatches.FancyBboxPatch(
            (0.00, y_top - norm_h(header_h)), 1.00, norm_h(header_h),
            boxstyle="square,pad=0",
            linewidth=0, facecolor=SEC_COLORS[sec], alpha=0.88,
            transform=ax.transAxes, clip_on=False
        )
        ax.add_patch(rect)
        ax.text(0.015, y_top - norm_h(header_h) / 2, SEC_TITLES[sec],
                transform=ax.transAxes, ha='left', va='center',
                fontsize=11, fontweight='bold', color='white')
        continue

    row = data[idx]
    _, label, cond_good, cond_bad, val_good, val_bad, metric, p_note = row
    diff = val_bad - val_good   # positive means bad is higher (worse if RPE/fatigue)
    abs_diff = abs(val_good - val_bad)

    # Determine significance tier
    if abs_diff >= 0.5:
        tier = "star"
        symbol = "★"
    elif abs_diff >= 0.3:
        tier = "dia"
        symbol = "◆"
    else:
        tier = "low"
        symbol = "・"

    row_y = y_top - row_h_px
    row_center_y = y_top - row_h_px / 2

    # Row background
    if tier == "star":
        bg_color = BG_STAR
    elif tier == "dia":
        bg_color = BG_DIA
    else:
        bg_color = "#FAFAFA" if idx % 2 == 0 else "#F2F2F2"

    bg_rect = mpatches.FancyBboxPatch(
        (0.00, row_y), 1.00, row_h_px,
        boxstyle="square,pad=0",
        linewidth=0, facecolor=bg_color, alpha=1.0,
        transform=ax.transAxes, clip_on=False
    )
    ax.add_patch(bg_rect)

    # Thin separator
    ax.plot([0, 1], [row_y, row_y], transform=ax.transAxes,
            color='#cccccc', linewidth=0.4)

    # Label
    label_color = '#1a1a2e' if tier in ("star", "dia") else '#555555'
    fw = 'bold' if tier == "star" else 'normal'
    ax.text(LABEL_X + 0.01, row_center_y,
            f"{symbol} {label}",
            transform=ax.transAxes, ha='left', va='center',
            fontsize=8.0, fontweight=fw, color=label_color,
            linespacing=1.2)

    # Good bar
    bw_good = bar_width(val_good, metric)
    good_col = COLOR_GOOD if tier != "low" else COLOR_GOOD_LIGHT
    bar_g = mpatches.FancyBboxPatch(
        (BAR_GOOD_START, row_center_y - row_h_px * 0.28),
        bw_good, row_h_px * 0.56,
        boxstyle="round,pad=0.002",
        linewidth=0, facecolor=good_col, alpha=0.92,
        transform=ax.transAxes, clip_on=False
    )
    ax.add_patch(bar_g)
    ax.text(BAR_GOOD_START + bw_good + 0.005, row_center_y,
            f"{val_good:.2f}", transform=ax.transAxes,
            ha='left', va='center', fontsize=7.5, color=good_col,
            fontweight='bold')
    # cond label inside/below good bar
    ax.text(BAR_GOOD_START + 0.003, row_center_y,
            cond_good, transform=ax.transAxes,
            ha='left', va='center', fontsize=6.5, color='white',
            fontweight='bold')

    # Bad bar
    bw_bad = bar_width(val_bad, metric)
    bad_col = COLOR_BAD if tier != "low" else COLOR_BAD_LIGHT
    bar_b = mpatches.FancyBboxPatch(
        (BAR_BAD_START, row_center_y - row_h_px * 0.28),
        bw_bad, row_h_px * 0.56,
        boxstyle="round,pad=0.002",
        linewidth=0, facecolor=bad_col, alpha=0.92,
        transform=ax.transAxes, clip_on=False
    )
    ax.add_patch(bar_b)
    ax.text(BAR_BAD_START + bw_bad + 0.005, row_center_y,
            f"{val_bad:.2f}", transform=ax.transAxes,
            ha='left', va='center', fontsize=7.5, color=bad_col,
            fontweight='bold')
    ax.text(BAR_BAD_START + 0.003, row_center_y,
            cond_bad, transform=ax.transAxes,
            ha='left', va='center', fontsize=6.5, color='white',
            fontweight='bold')

    # Diff annotation
    diff_val = val_good - val_bad   # good minus bad
    diff_str = f"{diff_val:+.2f}"
    if p_note:
        diff_str += f"\n({p_note})"
    diff_color = "#1a6e1a" if abs_diff >= 0.5 else ("#7a5c00" if abs_diff >= 0.3 else "#888888")
    ax.text(DIFF_X, row_center_y, diff_str,
            transform=ax.transAxes, ha='left', va='center',
            fontsize=8, fontweight='bold' if tier != "low" else 'normal',
            color=diff_color, linespacing=1.2)

# Column headers
header_y = 0.989
ax.text(BAR_GOOD_START + 0.01, header_y,
        "■ 良好条件", transform=ax.transAxes,
        ha='left', va='center', fontsize=8, color=COLOR_GOOD, fontweight='bold')
ax.text(BAR_BAD_START + 0.01, header_y,
        "■ 悪条件", transform=ax.transAxes,
        ha='left', va='center', fontsize=8, color=COLOR_BAD, fontweight='bold')
ax.text(DIFF_X, header_y, "差",
        transform=ax.transAxes, ha='left', va='center',
        fontsize=8, color='#333333', fontweight='bold')

# ── Legend & footnotes ───────────────────────────────────────────────────────
note1 = "★ |差| >= 0.5（要注目）　　◆ |差| >= 0.3（参考）　　・|差| < 0.3（関連弱）"
note2 = "※ ⑥睡眠の質→翌日RPEは統計的有意（p=0.021）"
note3 = "「差」= 良好条件 − 悪条件　（負の値 = 良好条件の方が低い = 良好）"

fig.text(0.02, 0.048, note1, ha='left', va='top', fontsize=8.5, color='#333333')
fig.text(0.02, 0.033, note2, ha='left', va='top', fontsize=8.5, color='#AA3333',
         fontstyle='italic')
fig.text(0.02, 0.018, note3, ha='left', va='top', fontsize=7.5, color='#666666')

# Footer
fig.text(0.98, 0.008, "作成日: 2026/05/23",
         ha='right', va='bottom', fontsize=7, color='#aaaaaa')

# ── Save ─────────────────────────────────────────────────────────────────────
out_png = "/home/user/AK/TI_関連性ヒント_図式化.png"
out_pdf = "/home/user/AK/TI_関連性ヒント_図式化.pdf"

fig.savefig(out_png, dpi=150, bbox_inches='tight', facecolor='white')
fig.savefig(out_pdf, bbox_inches='tight', facecolor='white')

import os
png_size = os.path.getsize(out_png)
pdf_size = os.path.getsize(out_pdf)
print(f"PNG saved: {out_png}  ({png_size/1024:.1f} KB)")
print(f"PDF saved: {out_pdf}  ({pdf_size/1024:.1f} KB)")
