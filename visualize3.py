"""
visualize3.py  ─  指定16項目の縦棒グラフ（4×4グリッド）
凡例・ラベルは legends.xlsx から読み込みます。
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import openpyxl
from matplotlib import font_manager

font_path = '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf'
fp = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.family'] = fp.get_name()
plt.rcParams['axes.unicode_minus'] = False

# ── legends.xlsx 読み込み ────────────────────────────────────
wb = openpyxl.load_workbook('/home/user/AK/legends.xlsx')

ws_grp = wb["グループ設定"]
parts_info = {}
for row in ws_grp.iter_rows(min_row=2, values_only=True):
    if row[0]:
        parts_info[row[0]] = {"label": row[1], "gender": row[2], "color": row[3]}

parts_m = [k for k, v in parts_info.items() if v["gender"] == "男性"]
parts_f = [k for k, v in parts_info.items() if v["gender"] == "女性"]
all_parts = parts_m + parts_f
gender_color = [parts_info[p]["color"] for p in all_parts]
CM = parts_info[parts_m[0]]["color"]
CF = parts_info[parts_f[0]]["color"]

ws_nl = wb["栄養素ラベル"]
NL, NU = {}, {}
for row in ws_nl.iter_rows(min_row=2, values_only=True):
    if row[0]:
        NL[str(row[0])] = row[1]
        NU[str(row[0])] = row[2] if row[2] else ""

ws_l2 = wb["図2_栄養素"]
L2 = {}
for row in ws_l2.iter_rows(min_row=2, values_only=True):
    if row[0]:
        L2[str(row[0])] = row[1]

# ── データ ──────────────────────────────────────────────────
energy     = {'m':[2414,2102,2189,2223,2407], 'f':[1776,1737,1686,1711]}
energy_kg  = {'m':[42,32,32,39,39],           'f':[39,35,28,32]}
protein    = {'m':[94.8,82.7,84.7,86.3,93.7], 'f':[72.4,74.0,67.8,70.5]}
protein_kg = {'m':[1.6,1.2,1.2,1.5,1.5],      'f':[1.6,1.5,1.1,1.3]}
carb       = {'m':[336.10,298.55,297.75,316.44,323.06],'f':[259.96,248.86,243.10,245.23]}
carb_kg    = {'m':[5.8,4.5,4.3,5.6,5.2],      'f':[5.8,5.0,4.1,4.6]}
prot_pct   = {'m':[13.6,13.7,13.5,13.5,13.5], 'f':[14.1,14.8,14.0,14.3]}
fat_pct    = {'m':[25.2,24.3,26.1,24.4,26.4], 'f':[27.2,27.2,26.8,27.2]}
carb_pct   = {'m':[61.2,62.0,60.4,62.1,60.2], 'f':[58.7,58.0,59.2,58.5]}
fiber      = {'m':[17,14,16,16,17],            'f':[20,18,15,16]}
salt       = {'m':[12,11,11,11,13],            'f':[11,11,9,10]}
calcium    = {'m':[688,589,557,618,595],        'f':[574,650,540,590]}
iron       = {'m':[10.4,8.8,9.5,9.5,10.1],    'f':[10.1,9.8,8.4,8.9]}
vitD       = {'m':[12.4,10.8,10.5,11.2,13.1], 'f':[9.7,10.9,7.8,8.9]}
vitB1      = {'m':[1.60,1.20,1.39,1.30,1.55], 'f':[1.18,1.11,0.96,1.03]}
vitB2_raw  = {'m':[2,2,2,2,2],                 'f':[1,2,1,1]}
vitB6      = {'m':[2.2,1.6,1.9,1.8,2.3],      'f':[1.9,1.6,1.3,1.5]}
vitC       = {'m':[142.5,108.3,170.5,129.0,148.3],'f':[185.3,141.6,119.5,129.1]}

# ── 各パネルの定義 ──────────────────────────────────────────
# (データ辞書, タイトル, Y軸ラベル, 参照値, 参照ラベル, パネル種別)
# 種別: 'bar' or 'pfc'
panels = [
    (energy,     NL.get("エネルギー",    "エネルギー"),       "kcal/日",    None,  None,           "bar"),
    (energy_kg,  NL.get("エネルギー_kg", "エネルギー/kg BW"), "kcal/kg BW", None,  None,           "bar"),
    (protein,    NL.get("たんぱく質",    "たんぱく質"),       "g/日",       None,  None,           "bar"),
    (protein_kg, "たんぱく質/kg BW",                          "g/kg BW",    None,  None,           "bar"),
    (carb,       NL.get("炭水化物",      "炭水化物"),         "g/日",       None,  None,           "bar"),
    (carb_kg,    NL.get("炭水化物_kg",   "炭水化物/kg BW"),   "g/kg BW",    None,  None,           "bar"),
    (None,       "PFC エネルギー比率",                         "%E",         None,  None,           "pfc"),
    (fiber,      NL.get("食物繊維総量",  "食物繊維総量"),     "g/日",       18.0,  "目安量 18g",   "bar"),
    (salt,       NL.get("食塩相当量",    "食塩相当量"),       "g/日",       8.0,   "WHO目標 8g",   "bar"),
    (calcium,    NL.get("カルシウム",    "カルシウム"),       "mg/日",      None,  None,           "bar"),
    (iron,       NL.get("鉄",           "鉄"),               "mg/日",      None,  None,           "bar"),
    (vitD,       NL.get("ビタミンD",    "ビタミンD"),        "µg/日",      None,  None,           "bar"),
    (vitB1,      NL.get("ビタミンB1",   "ビタミンB1"),       "mg/日",      None,  None,           "bar"),
    (vitB2_raw,  NL.get("ビタミンB2",   "ビタミンB2 (概算)"),"mg/日",      None,  None,           "bar"),
    (vitB6,      NL.get("ビタミンB6",   "ビタミンB6"),       "mg/日",      None,  None,           "bar"),
    (vitC,       NL.get("ビタミンC",    "ビタミンC"),        "mg/日",      100.0, "推奨量 100mg", "bar"),
]

# ── 描画 ─────────────────────────────────────────────────────
fig, axes = plt.subplots(4, 4, figsize=(20, 20))
fig.suptitle("栄養素摂取量 グループ別比較（縦棒グラフ）",
             fontproperties=fp, fontsize=18, fontweight='bold', y=0.995)

x = np.arange(9)
xtick_labels = [parts_info[p]["label"] for p in all_parts]

avg_lbl_m = L2.get("avg_male_label", "男平均")
avg_lbl_f = L2.get("avg_female_label", "女平均")

for ax, (dat, title, ylabel, ref, ref_lbl, kind) in zip(axes.flat, panels):

    if kind == "pfc":
        # ── PFC 積み上げ棒グラフ ──
        p_vals = prot_pct['m'] + prot_pct['f']
        f_vals = fat_pct['m']  + fat_pct['f']
        c_vals = carb_pct['m'] + carb_pct['f']
        ax.bar(x, p_vals, color='#E67E22',
               label=L2.get("label_protein", "たんぱく質"), zorder=3)
        ax.bar(x, f_vals, bottom=p_vals,
               color='#E74C3C', label=L2.get("label_fat", "脂質"), zorder=3)
        ax.bar(x, c_vals, bottom=[p+f for p,f in zip(p_vals,f_vals)],
               color='#3498DB', label=L2.get("label_carb", "炭水化物"), zorder=3)
        for i, (p, f, c) in enumerate(zip(p_vals, f_vals, c_vals)):
            ax.text(i, p/2,     f'{p:.0f}', ha='center', va='center', fontsize=6.5,
                    color='white', fontweight='bold')
            ax.text(i, p+f/2,   f'{f:.0f}', ha='center', va='center', fontsize=6.5,
                    color='white', fontweight='bold')
            ax.text(i, p+f+c/2, f'{c:.0f}', ha='center', va='center', fontsize=6.5,
                    color='white', fontweight='bold')
        ax.set_ylim(0, 115)
        ax.legend(prop=fp, fontsize=7, loc='upper right', ncol=1)
        ax.axvline(4.5, color='black', lw=1.2, ls='--', alpha=0.5)

    else:
        # ── 通常縦棒 ──
        vals = dat['m'] + dat['f']
        bars = ax.bar(x, vals, color=gender_color, zorder=3,
                      edgecolor='white', linewidth=0.6)

        # 数値ラベル（バー上部）
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                    f'{v:.1f}' if v < 100 else f'{v:.0f}',
                    ha='center', va='bottom', fontsize=6.5, color='#333333')

        mu_m = np.mean(dat['m'])
        mu_f = np.mean(dat['f'])
        ax.hlines(mu_m, -0.5, 4.4, colors=CM, lw=1.8, ls=':',
                  label=f'{avg_lbl_m} {mu_m:.1f}')
        ax.hlines(mu_f,  4.6, 8.5, colors=CF, lw=1.8, ls=':',
                  label=f'{avg_lbl_f} {mu_f:.1f}')

        if ref is not None:
            ax.axhline(ref, color='red', lw=1.5, ls='--', alpha=0.8, label=ref_lbl)

        ax.legend(prop=fp, fontsize=7, loc='upper right')
        ax.axvline(4.5, color='black', lw=1.2, ls='--', alpha=0.5)

    # 共通設定
    ax.set_xticks(x)
    ax.set_xticklabels(xtick_labels, fontproperties=fp, fontsize=9)
    ax.set_ylabel(ylabel, fontproperties=fp, fontsize=9)
    ax.set_title(title, fontproperties=fp, fontsize=11, fontweight='bold', pad=6)
    ax.set_xlim(-0.6, 8.6)
    ax.grid(axis='y', ls='--', alpha=0.35, zorder=0)
    ax.set_axisbelow(True)

    # 男性/女性ゾーン背景（薄色）
    ax.axvspan(-0.6, 4.4, alpha=0.04, color=CM, zorder=0)
    ax.axvspan(4.6, 8.6,  alpha=0.04, color=CF, zorder=0)

# 全体凡例（性別）
m_patch = mpatches.Patch(color=CM, label='男性グループ (A–E)')
f_patch = mpatches.Patch(color=CF, label='女性グループ (F–I)')
fig.legend(handles=[m_patch, f_patch], prop=fp, fontsize=12,
           loc='lower center', ncol=2, bbox_to_anchor=(0.5, -0.005),
           frameon=True, edgecolor='gray')

fig.tight_layout(rect=[0, 0.02, 1, 0.995])
out_path = '/home/user/AK/fig_16items.png'
fig.savefig(out_path, dpi=150, bbox_inches='tight')
plt.close(fig)
print(f"保存完了: {out_path}")
