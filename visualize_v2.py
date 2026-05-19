"""
visualize_v2.py  ─  食品群データの可視化（図1〜図5）
凡例・タイトル・軸ラベルはすべて legends.xlsx から読み込みます。
テキストを変更したい場合は legends.xlsx を編集してから再実行してください。
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

def load_sheet_as_dict(sheet_name, key_col=1, val_col=2, skip_header=True):
    ws = wb[sheet_name]
    d = {}
    for row in ws.iter_rows(min_row=2 if skip_header else 1, values_only=True):
        if row[key_col-1] is not None:
            d[str(row[key_col-1])] = row[val_col-1]
    return d

# グループ設定
ws_grp = wb["グループ設定"]
parts_info = {}
for row in ws_grp.iter_rows(min_row=2, values_only=True):
    if row[0]:
        parts_info[row[0]] = {"label": row[1], "gender": row[2], "color": row[3]}

parts_m = [k for k,v in parts_info.items() if v["gender"] == "男性"]
parts_f = [k for k,v in parts_info.items() if v["gender"] == "女性"]
all_parts = parts_m + parts_f
gender_color = [parts_info[p]["color"] for p in all_parts]
CM = parts_info[parts_m[0]]["color"]
CF = parts_info[parts_f[0]]["color"]

# 図1 凡例設定
L1 = load_sheet_as_dict("図1_食品群比較")

# 食品群ラベル（図1用 / レーダー用 / 積み上げ用）
ws_food = wb["食品群ラベル"]
food_labels_fig1   = {}
food_labels_radar  = {}
food_labels_stack  = {}
for row in ws_food.iter_rows(min_row=2, values_only=True):
    if row[0]:
        food_labels_fig1[row[0]]  = row[1]
        food_labels_radar[row[0]] = row[2]
        food_labels_stack[row[0]] = row[3]

# ── データ ──────────────────────────────────────────────────
data = {
    '穀類':             {'m': [536.4,516.0,509.6,523.8,539.3], 'f': [382.1,350.7,334.9,341.7]},
    'いも類':           {'m': [48.6,37.9,41.2,39.6,43.9],      'f': [72.8,48.7,46.2,46.5]},
    '豆類':             {'m': [90.5,58.3,75.1,67.0,63.6],      'f': [71.3,76.7,74.7,90.7]},
    '野菜類':           {'m': [335.1,311.5,308.5,318.7,341.5], 'f': [515.7,331.2,265.6,300.9]},
    '果物':             {'m': [114.8,45.5,197.4,101.0,116.1],  'f': [114.2,106.9,116.9,116.3]},
    '魚介類':           {'m': [110.7,100.7,98.7,103.0,119.9],  'f': [84.4,95.8,73.0,79.0]},
    '肉類':             {'m': [111.2,84.6,116.3,88.0,132.0],   'f': [71.4,67.7,62.0,66.2]},
    '卵類':             {'m': [40.8,39.6,39.3,40.3,40.6],      'f': [32.8,32.8,31.3,31.6]},
    '乳類':             {'m': [188.0,137.1,104.8,153.9,125.5], 'f': [119.1,186.6,126.8,144.7]},
    '菓子類':           {'m': [31.8,31.6,31.5,32.5,40.4],      'f': [43.5,39.3,47.1,43.2]},
    '非アルコール飲料': {'m': [581.7,597.3,476.0,551.4,505.1], 'f': [607.7,762.5,698.8,554.5]},
    '海藻類':           {'m': [13.9,10.1,9.0,13.0,8.8],        'f': [18.8,11.5,8.4,10.0]},
}

age_m=[16.8,45.5,26.0,39.5,22.2]; age_f=[17.0,22.0,26.3,25.3]
ht_m =[168.0,176.3,173.7,169.5,172.2]; ht_f=[151.0,159.0,163.3,159.3]
wt_m =[58.2,66.3,69.0,57.0,62.2];  wt_f=[45.0,50.0,60.7,54.0]

categories = list(data.keys())
avg_m_list = [np.mean(data[c]['m']) for c in categories]
avg_f_list = [np.mean(data[c]['f']) for c in categories]

cat_labels_fig1 = [food_labels_fig1.get(c, c) for c in categories]

# =========================================================================
# 図1: 男女平均比較 (横棒グラフ)
# =========================================================================
fig1, ax = plt.subplots(figsize=(12, 8))
y = np.arange(len(categories))
h = 0.35

bars_m = ax.barh(y+h/2, avg_m_list, h, color=CM,
                 label=L1.get("legend_male", "男性平均"), zorder=3)
bars_f = ax.barh(y-h/2, avg_f_list, h, color=CF,
                 label=L1.get("legend_female", "女性平均"), zorder=3)

ax.set_yticks(y)
ax.set_yticklabels(cat_labels_fig1, fontproperties=fp, fontsize=12)
ax.set_xlabel(L1.get("xlabel_fig1", "摂取量 (g/日)"), fontproperties=fp, fontsize=11)
ax.set_title(L1.get("title_fig1", "食品群別 摂取量の男女比較"), fontproperties=fp,
             fontsize=15, fontweight='bold', pad=14)
ax.legend(prop=fp, fontsize=11)
ax.grid(axis='x', linestyle='--', alpha=0.4, zorder=0)
ax.set_axisbelow(True)

for bar in bars_m:
    ax.text(bar.get_width()+5, bar.get_y()+bar.get_height()/2,
            f'{bar.get_width():.0f}', va='center', ha='left', fontsize=8.5, color=CM)
for bar in bars_f:
    ax.text(bar.get_width()+5, bar.get_y()+bar.get_height()/2,
            f'{bar.get_width():.0f}', va='center', ha='left', fontsize=8.5, color=CF)

fig1.tight_layout()
fig1.savefig('/home/user/AK/fig1_gender_comparison.png', dpi=150, bbox_inches='tight')
plt.close(fig1)
print("図1 完了")

# =========================================================================
# 図2: レーダーチャート
# =========================================================================
radar_keys = ['穀類','野菜類','果物','魚介類','肉類','乳類','豆類','卵類','菓子類']
radar_labels = [food_labels_radar.get(k, k) for k in radar_keys]
vals_m = [np.mean(data[c]['m']) for c in radar_keys]
vals_f = [np.mean(data[c]['f']) for c in radar_keys]

angles = np.linspace(0, 2*np.pi, len(radar_keys), endpoint=False).tolist()
angles += angles[:1]
vals_m_r = vals_m + vals_m[:1]
vals_f_r = vals_f + vals_f[:1]

fig2, ax2 = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
ax2.plot(angles, vals_m_r, 'o-', color=CM, linewidth=2,
         label=L1.get("legend_male_radar", "男性平均"))
ax2.fill(angles, vals_m_r, alpha=0.2, color=CM)
ax2.plot(angles, vals_f_r, 's-', color=CF, linewidth=2,
         label=L1.get("legend_female_radar", "女性平均"))
ax2.fill(angles, vals_f_r, alpha=0.2, color=CF)

ax2.set_thetagrids(np.degrees(angles[:-1]), labels=radar_labels,
                   fontproperties=fp, fontsize=12)
ax2.set_yticklabels([])
ax2.set_title(L1.get("title_fig2", "食品バランス レーダーチャート"),
              fontproperties=fp, fontsize=14, fontweight='bold', pad=25)
ax2.legend(loc='upper right', bbox_to_anchor=(1.3, 1.15), prop=fp, fontsize=11)
fig2.tight_layout()
fig2.savefig('/home/user/AK/fig2_radar.png', dpi=150, bbox_inches='tight')
plt.close(fig2)
print("図2 完了")

# =========================================================================
# 図3: 積み上げ棒グラフ
# =========================================================================
stack_keys = ['穀類','野菜類','肉類','魚介類','乳類','豆類','果物','卵類','いも類','菓子類']
stack_labels = [food_labels_stack.get(k, k) for k in stack_keys]
stack_colors = ['#F4A620','#5BA85A','#C0392B','#2980B9','#F0E0A0',
                '#8E44AD','#E67E22','#F39C12','#95A5A6','#E91E8C']

vals_by_part = []
for part in all_parts:
    row = []
    for cat in stack_keys:
        if part in parts_m:
            idx = parts_m.index(part)
            row.append(data[cat]['m'][idx])
        else:
            idx = parts_f.index(part)
            row.append(data[cat]['f'][idx])
    vals_by_part.append(row)

fig3, ax3 = plt.subplots(figsize=(13, 7))
x = np.arange(len(all_parts))
bottoms = np.zeros(len(all_parts))
for j, (cat, lbl) in enumerate(zip(stack_keys, stack_labels)):
    vals = [vals_by_part[i][j] for i in range(len(all_parts))]
    ax3.bar(x, vals, bottom=bottoms, color=stack_colors[j], label=lbl, zorder=3)
    bottoms += np.array(vals)

ax3.set_xticks(x)
xticklabels = [('男\n' if p in parts_m else '女\n') + parts_info[p]["label"] for p in all_parts]
ax3.set_xticklabels(xticklabels, fontproperties=fp, fontsize=12)
ax3.set_ylabel('摂取量 (g/日)', fontproperties=fp, fontsize=11)
ax3.set_title(L1.get("title_fig3", "グループ別 食品摂取量"), fontproperties=fp,
              fontsize=14, fontweight='bold')
ax3.axvline(x=4.5, color='black', linewidth=2, linestyle='--', alpha=0.6)

ylim_top = ax3.get_ylim()[1]
ax3.text(2.0, ylim_top*0.97, L1.get("label_male_group", "男性グループ"),
         ha='center', fontproperties=fp, fontsize=11, color=CM, fontweight='bold')
ax3.text(6.5, ylim_top*0.97, L1.get("label_female_group", "女性グループ"),
         ha='center', fontproperties=fp, fontsize=11, color=CF, fontweight='bold')
ax3.legend(prop=fp, fontsize=9, loc='upper right', ncol=2)
ax3.grid(axis='y', linestyle='--', alpha=0.4, zorder=0)
ax3.set_axisbelow(True)
fig3.tight_layout()
fig3.savefig('/home/user/AK/fig3_stacked.png', dpi=150, bbox_inches='tight')
plt.close(fig3)
print("図3 完了")

# =========================================================================
# 図4: 身体特性
# =========================================================================
fig4, axes = plt.subplots(1, 3, figsize=(14, 5))
metrics = [
    ('年齢 (歳)', age_m, age_f),
    ('身長 (cm)', ht_m,  ht_f),
    ('体重 (kg)', wt_m,  wt_f),
]
for ax4, (label, vm, vf) in zip(axes, metrics):
    jm = np.random.uniform(-0.08, 0.08, len(vm))
    jf = np.random.uniform(-0.08, 0.08, len(vf))
    ax4.scatter([1+j for j in jm], vm, s=120, color=CM, zorder=4, edgecolors='white', lw=1.2)
    ax4.scatter([2+j for j in jf], vf, s=120, color=CF, zorder=4, edgecolors='white', lw=1.2, marker='s')
    ax4.hlines(np.mean(vm), 0.7, 1.3, colors=CM, lw=2.5)
    ax4.hlines(np.mean(vf), 1.7, 2.3, colors=CF, lw=2.5)
    for xp, vals, col in [(1, vm, CM), (2, vf, CF)]:
        q1, q3 = np.percentile(vals, [25, 75])
        ax4.vlines(xp, q1, q3, colors=col, lw=8, alpha=0.25, zorder=2)
    for i, (part, v) in enumerate(zip(parts_m, vm)):
        ax4.annotate(parts_info[part]["label"], (1+jm[i], v),
                     textcoords='offset points', xytext=(6,0), fontsize=8,
                     color=CM, fontproperties=fp)
    for i, (part, v) in enumerate(zip(parts_f, vf)):
        ax4.annotate(parts_info[part]["label"], (2+jf[i], v),
                     textcoords='offset points', xytext=(6,0), fontsize=8,
                     color=CF, fontproperties=fp)
    ax4.set_xticks([1, 2])
    ax4.set_xticklabels(['男性', '女性'], fontproperties=fp, fontsize=12)
    ax4.set_ylabel(label, fontproperties=fp, fontsize=11)
    ax4.set_title(label, fontproperties=fp, fontsize=12, fontweight='bold')
    ax4.set_xlim(0.5, 2.7)
    ax4.grid(axis='y', ls='--', alpha=0.4)
    ax4.text(1, np.mean(vm), f'  平均\n  {np.mean(vm):.1f}', va='center',
             fontsize=8.5, color=CM, fontproperties=fp)
    ax4.text(2, np.mean(vf), f'  平均\n  {np.mean(vf):.1f}', va='center',
             fontsize=8.5, color=CF, fontproperties=fp)

fig4.suptitle(L1.get("title_fig4", "グループ別 身体特性"), fontproperties=fp,
              fontsize=14, fontweight='bold')
m_patch = mpatches.Patch(color=CM, label=L1.get("legend_male_body", "男性 (A–E)"))
f_patch = mpatches.Patch(color=CF, label=L1.get("legend_female_body", "女性 (F–I)"))
fig4.legend(handles=[m_patch, f_patch], prop=fp, fontsize=11,
            loc='upper right', bbox_to_anchor=(0.99, 0.95))
fig4.tight_layout()
fig4.savefig('/home/user/AK/fig4_body_metrics.png', dpi=150, bbox_inches='tight')
plt.close(fig4)
print("図4 完了")

# =========================================================================
# 図5: 男女差
# =========================================================================
diffs = {c: np.mean(data[c]['m']) - np.mean(data[c]['f']) for c in categories}
sorted_cats = sorted(diffs, key=lambda c: abs(diffs[c]), reverse=True)[:8]
sorted_diffs = [diffs[c] for c in sorted_cats]
colors_diff = [CM if d > 0 else CF for d in sorted_diffs]
sorted_labels = [food_labels_fig1.get(c, c) for c in sorted_cats]

fig5, ax5 = plt.subplots(figsize=(10, 6))
bars = ax5.barh(sorted_labels[::-1], sorted_diffs[::-1],
                color=colors_diff[::-1], zorder=3, edgecolor='white')
ax5.axvline(0, color='black', lw=1.2)
ax5.set_xlabel(L1.get("xlabel_fig5", "男性平均 − 女性平均 (g/日)"),
               fontproperties=fp, fontsize=11)
ax5.set_title(L1.get("title_fig5", "男女差が大きい食品群"),
              fontproperties=fp, fontsize=13, fontweight='bold')
ax5.set_yticklabels(sorted_labels[::-1], fontproperties=fp, fontsize=12)
for bar, val in zip(bars, sorted_diffs[::-1]):
    offset = 5 if val >= 0 else -5
    ha = 'left' if val >= 0 else 'right'
    ax5.text(val+offset, bar.get_y()+bar.get_height()/2,
             f'{val:+.0f}g', va='center', ha=ha, fontsize=9,
             color=CM if val > 0 else CF, fontweight='bold')
ax5.grid(axis='x', ls='--', alpha=0.4, zorder=0)
m_patch2 = mpatches.Patch(color=CM, label=L1.get("legend_more_male", "男性が多い"))
f_patch2 = mpatches.Patch(color=CF, label=L1.get("legend_more_female", "女性が多い"))
ax5.legend(handles=[m_patch2, f_patch2], prop=fp, fontsize=10)
fig5.tight_layout()
fig5.savefig('/home/user/AK/fig5_gender_diff.png', dpi=150, bbox_inches='tight')
plt.close(fig5)
print("図5 完了")

print("\n図1〜5 すべて保存完了")
