import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import numpy as np
from matplotlib import font_manager

font_path = '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf'
fp = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.family'] = fp.get_name()
plt.rcParams['axes.unicode_minus'] = False

CM = '#3A7FC1'   # male blue
CF = '#E05C7A'   # female pink
CM2 = '#A8C8E8'
CF2 = '#F0AABB'

parts_m = ['A','B','C','D','E']
parts_f = ['F','G','H','I']
all_parts = parts_m + parts_f
gender_color = [CM]*5 + [CF]*4

# ── Raw data ──────────────────────────────────────────────────────────────
energy    = {'m':[2414,2102,2189,2223,2407], 'f':[1776,1737,1686,1711]}
energy_kg = {'m':[42,32,32,39,39],           'f':[39,35,28,32]}
water     = {'m':[2767,2674,2710,2654,2594], 'f':[2870,2521,2443,2463]}
protein   = {'m':[94.8,82.7,84.7,86.3,93.7],'f':[72.4,74.0,67.8,70.5]}
prot_kg   = {'m':[1.6,1.2,1.2,1.5,1.5],     'f':[1.6,1.5,1.1,1.3]}
fat       = {'m':[73.33,61.67,68.62,65.56,76.78],'f':[58.17,57.01,54.39,55.98]}
carb      = {'m':[336.10,298.55,297.75,316.44,323.06],'f':[259.96,248.86,243.10,245.23]}
carb_kg   = {'m':[5.8,4.5,4.3,5.6,5.2],     'f':[5.8,5.0,4.1,4.6]}

prot_pct  = {'m':[13.6,13.7,13.5,13.5,13.5],'f':[14.1,14.8,14.0,14.3]}
fat_pct   = {'m':[25.2,24.3,26.1,24.4,26.4],'f':[27.2,27.2,26.8,27.2]}
carb_pct  = {'m':[61.2,62.0,60.4,62.1,60.2],'f':[58.7,58.0,59.2,58.5]}

fiber     = {'m':[17,14,16,16,17], 'f':[20,18,15,16]}
sodium    = {'m':[4727,4253,4268,4459,5010],'f':[4366,4181,3679,3838]}
salt      = {'m':[12,11,11,11,13], 'f':[11,11,9,10]}
potassium = {'m':[3507,2933,2978,3124,3244],'f':[3251,3144,2704,2869]}
calcium   = {'m':[688,589,557,618,595],     'f':[574,650,540,590]}
magnesium = {'m':[372,309,319,329,335],     'f':[331,323,280,295]}
phosphorus= {'m':[1451,1228,1231,1284,1354],'f':[1102,1131,1010,1075]}
iron      = {'m':[10.4,8.8,9.5,9.5,10.1],  'f':[10.1,9.8,8.4,8.9]}
zinc      = {'m':[11.9,9.9,10.3,10.4,11.4],'f':[8.4,8.5,7.6,8.0]}
copper    = {'m':[1.6,1.3,1.4,1.5,1.5],    'f':[1.4,1.3,1.2,1.2]}
manganese = {'m':[4.8,4.6,4.6,4.5,4.6],    'f':[5.6,4.8,4.0,4.1]}
cholesterol={'m':[378,347,351,351,382],     'f':[292,297,278,285]}

retinol   = {'m':[810,660,738,701,861],     'f':[725,680,533,594]}
vitD      = {'m':[12.4,10.8,10.5,11.2,13.1],'f':[9.7,10.9,7.8,8.9]}
tocopherol= {'m':[10,8,9,9,10],             'f':[9,9,8,8]}
vitK      = {'m':[380.96,264.35,275.08,347.89,308.65],'f':[324.65,343.28,328.76,329.85]}
vitB1     = {'m':[1.60,1.20,1.39,1.30,1.55],'f':[1.18,1.11,0.96,1.03]}
vitB2     = {'m':[2,2,2,2,2],               'f':[1,2,1,1]}
niacin    = {'m':[24.2,21.0,22.5,21.7,25.7],'f':[19.0,18.7,17.6,18.1]}
vitB6     = {'m':[2.2,1.6,1.9,1.8,2.3],    'f':[1.9,1.6,1.3,1.5]}
vitB12    = {'m':[11.6,9.5,9.2,10.0,11.3], 'f':[7.7,8.9,6.5,7.2]}
folate    = {'m':[486.1,409.0,450.6,441.0,484.4],'f':[519.7,479.2,408.4,432.9]}
pantothenic={'m':[8.6,6.8,6.9,7.4,7.7],    'f':[6.3,6.4,5.8,6.1]}
vitC      = {'m':[142.5,108.3,170.5,129.0,148.3],'f':[185.3,141.6,119.5,129.1]}

def avg(d): return np.mean(d['m']), np.mean(d['f'])
def all_vals(d): return d['m'] + d['f']

# =========================================================================
# Fig A: エネルギーと主要栄養素の男女比較
# =========================================================================
figA, axes = plt.subplots(2, 3, figsize=(15, 9))
figA.suptitle('エネルギー・主要栄養素の男女グループ比較', fontproperties=fp, fontsize=15, fontweight='bold')

datasets = [
    (energy,    'エネルギー (kcal/日)', 'kcal'),
    (energy_kg, 'エネルギー (kcal/kg BW)', 'kcal/kg'),
    (protein,   'たんぱく質 (g/日)', 'g'),
    (fat,       '脂質 (g/日)', 'g'),
    (carb,      '炭水化物 (g/日)', 'g'),
    (carb_kg,   '炭水化物 (g/kg BW)', 'g/kg'),
]

for ax, (dat, title, unit) in zip(axes.flat, datasets):
    x = np.arange(9)
    vals = dat['m'] + dat['f']
    bars = ax.bar(x, vals, color=gender_color, zorder=3, edgecolor='white', linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(all_parts, fontproperties=fp, fontsize=10)
    ax.set_title(title, fontproperties=fp, fontsize=11, fontweight='bold')
    ax.set_ylabel(unit, fontproperties=fp, fontsize=9)
    ax.axvline(4.5, color='gray', lw=1.5, ls='--', alpha=0.7)
    ax.grid(axis='y', ls='--', alpha=0.35, zorder=0)
    # mean lines
    ax.hlines(np.mean(dat['m']), -0.4, 4.4, colors=CM, lw=2, ls=':', label=f'男平均 {np.mean(dat["m"]):.1f}')
    ax.hlines(np.mean(dat['f']),  4.6, 8.4, colors=CF, lw=2, ls=':', label=f'女平均 {np.mean(dat["f"]):.1f}')
    ax.legend(prop=fp, fontsize=8, loc='upper right')

figA.tight_layout()
figA.savefig('/home/user/AK/figA_macronutrients.png', dpi=150, bbox_inches='tight')
plt.close(figA)
print("figA done")

# =========================================================================
# Fig B: PFCバランス（積み上げ帯グラフ）
# =========================================================================
figB, ax = plt.subplots(figsize=(13, 5))
figB.suptitle('PFCエネルギー比率（各グループ）', fontproperties=fp, fontsize=14, fontweight='bold')

p_vals = prot_pct['m'] + prot_pct['f']
f_vals = fat_pct['m']  + fat_pct['f']
c_vals = carb_pct['m'] + carb_pct['f']

x = np.arange(9)
bp = ax.bar(x, p_vals, color='#E67E22', label='たんぱく質', zorder=3)
bf = ax.bar(x, f_vals, bottom=p_vals, color='#E74C3C', label='脂質', zorder=3)
bc = ax.bar(x, c_vals, bottom=[p+f for p,f in zip(p_vals,f_vals)], color='#3498DB', label='炭水化物', zorder=3)

# labels inside bars
for i,(p,f,c) in enumerate(zip(p_vals, f_vals, c_vals)):
    ax.text(i, p/2,           f'{p:.1f}%', ha='center', va='center', fontsize=8.5, color='white', fontweight='bold')
    ax.text(i, p+f/2,         f'{f:.1f}%', ha='center', va='center', fontsize=8.5, color='white', fontweight='bold')
    ax.text(i, p+f+c/2,       f'{c:.1f}%', ha='center', va='center', fontsize=8.5, color='white', fontweight='bold')

ax.set_xticks(x)
ax.set_xticklabels(all_parts, fontproperties=fp, fontsize=11)
ax.set_ylabel('%エネルギー', fontproperties=fp, fontsize=11)
ax.set_ylim(0, 108)
ax.axvline(4.5, color='black', lw=2, ls='--', alpha=0.6)
ax.text(2.0, 104, '男性', ha='center', fontproperties=fp, fontsize=11, color=CM, fontweight='bold')
ax.text(6.5, 104, '女性', ha='center', fontproperties=fp, fontsize=11, color=CF, fontweight='bold')
ax.legend(prop=fp, fontsize=10, loc='lower right')
ax.grid(axis='y', ls='--', alpha=0.3, zorder=0)

figB.tight_layout()
figB.savefig('/home/user/AK/figB_pfc_ratio.png', dpi=150, bbox_inches='tight')
plt.close(figB)
print("figB done")

# =========================================================================
# Fig C: ミネラル レーダーチャート
# =========================================================================
min_cats = ['カルシウム\n(mg)', 'カリウム\n(mg)', '鉄\n(mg)', '亜鉛\n(mg)', 'マグネシウム\n(mg)', 'リン\n(mg/10)']
avg_m_min = [np.mean(calcium['m']), np.mean(potassium['m']), np.mean(iron['m'])*50,
             np.mean(zinc['m'])*50, np.mean(magnesium['m']), np.mean(phosphorus['m'])/10]
avg_f_min = [np.mean(calcium['f']), np.mean(potassium['f']), np.mean(iron['f'])*50,
             np.mean(zinc['f'])*50, np.mean(magnesium['f']), np.mean(phosphorus['f'])/10]

angles = np.linspace(0, 2*np.pi, len(min_cats), endpoint=False).tolist()
angles += angles[:1]
vm_r = avg_m_min + avg_m_min[:1]
vf_r = avg_f_min + avg_f_min[:1]

figC, ax2 = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
ax2.plot(angles, vm_r, 'o-', color=CM, lw=2.5, label='男性平均')
ax2.fill(angles, vm_r, alpha=0.2, color=CM)
ax2.plot(angles, vf_r, 's-', color=CF, lw=2.5, label='女性平均')
ax2.fill(angles, vf_r, alpha=0.2, color=CF)
ax2.set_thetagrids(np.degrees(angles[:-1]), labels=min_cats, fontproperties=fp, fontsize=11)
ax2.set_yticklabels([])
ax2.set_title('ミネラル摂取バランス（レーダーチャート）\n※鉄・亜鉛は×50、リンは÷10でスケール調整',
              fontproperties=fp, fontsize=13, fontweight='bold', pad=30)
ax2.legend(loc='upper right', bbox_to_anchor=(1.35, 1.15), prop=fp, fontsize=11)
figC.tight_layout()
figC.savefig('/home/user/AK/figC_minerals_radar.png', dpi=150, bbox_inches='tight')
plt.close(figC)
print("figC done")

# =========================================================================
# Fig D: ビタミン 男女平均比較（横棒）
# =========================================================================
vit_data = {
    'ビタミンA\n(µg RE)': (retinol, 1),
    'ビタミンD\n(µg)':     (vitD,    1),
    'ビタミンE\n(mg)':     (tocopherol,1),
    'ビタミンB1\n(mg)':    (vitB1,   1),
    'ナイアシン\n(mg)':    (niacin,  1),
    'ビタミンB6\n(mg)':    (vitB6,   1),
    'ビタミンB12\n(µg)':   (vitB12,  1),
    '葉酸\n(µg)':          (folate,  1),
    'ビタミンC\n(mg)':     (vitC,    1),
}

cats_v = list(vit_data.keys())
avgs_m = [np.mean(vit_data[c][0]['m']) * vit_data[c][1] for c in cats_v]
avgs_f = [np.mean(vit_data[c][0]['f']) * vit_data[c][1] for c in cats_v]

figD, ax3 = plt.subplots(figsize=(11, 7))
y = np.arange(len(cats_v))
h = 0.35
bm = ax3.barh(y+h/2, avgs_m, h, color=CM, label='男性平均', zorder=3)
bf2 = ax3.barh(y-h/2, avgs_f, h, color=CF, label='女性平均', zorder=3)
ax3.set_yticks(y)
ax3.set_yticklabels(cats_v, fontproperties=fp, fontsize=11)
ax3.set_xlabel('摂取量', fontproperties=fp, fontsize=11)
ax3.set_title('ビタミン摂取量の男女比較（グループ平均）', fontproperties=fp, fontsize=14, fontweight='bold')
ax3.legend(prop=fp, fontsize=11)
ax3.grid(axis='x', ls='--', alpha=0.4, zorder=0)
for bar in bm:
    ax3.text(bar.get_width()+0.5, bar.get_y()+bar.get_height()/2,
             f'{bar.get_width():.1f}', va='center', ha='left', fontsize=8, color=CM)
for bar in bf2:
    ax3.text(bar.get_width()+0.5, bar.get_y()+bar.get_height()/2,
             f'{bar.get_width():.1f}', va='center', ha='left', fontsize=8, color=CF)
figD.tight_layout()
figD.savefig('/home/user/AK/figD_vitamins.png', dpi=150, bbox_inches='tight')
plt.close(figD)
print("figD done")

# =========================================================================
# Fig E: 注目指標サマリー（塩分・食物繊維・コレステロール・水分）
# =========================================================================
figE, axes2 = plt.subplots(2, 2, figsize=(13, 9))
figE.suptitle('注目指標：塩分・食物繊維・コレステロール・水分', fontproperties=fp, fontsize=14, fontweight='bold')

spot_data = [
    (salt,        '食塩相当量 (g/日)', 'g',  8.0,  'WHO目標: 8g以下'),
    (fiber,       '食物繊維総量 (g/日)', 'g', 18.0, '目安量(成人): 18–21g'),
    (cholesterol, 'コレステロール (mg/日)', 'mg', None, None),
    (water,       '水分 (g/日)', 'g',       None, None),
]

for ax_s, (dat, title, unit, ref, ref_label) in zip(axes2.flat, spot_data):
    vals = dat['m'] + dat['f']
    x = np.arange(9)
    ax_s.bar(x, vals, color=gender_color, zorder=3, edgecolor='white', linewidth=0.8)
    ax_s.set_xticks(x)
    ax_s.set_xticklabels(all_parts, fontproperties=fp, fontsize=10)
    ax_s.set_title(title, fontproperties=fp, fontsize=12, fontweight='bold')
    ax_s.set_ylabel(unit, fontproperties=fp, fontsize=10)
    ax_s.axvline(4.5, color='gray', lw=1.5, ls='--', alpha=0.6)
    ax_s.grid(axis='y', ls='--', alpha=0.35, zorder=0)
    ax_s.hlines(np.mean(dat['m']), -0.4, 4.4, colors=CM, lw=2, ls=':', label=f'男平均 {np.mean(dat["m"]):.1f}')
    ax_s.hlines(np.mean(dat['f']),  4.6, 8.4, colors=CF, lw=2, ls=':', label=f'女平均 {np.mean(dat["f"]):.1f}')
    if ref is not None:
        ax_s.axhline(ref, color='red', lw=1.8, ls='--', alpha=0.8, label=ref_label)
    ax_s.legend(prop=fp, fontsize=8.5, loc='upper right')

figE.tight_layout()
figE.savefig('/home/user/AK/figE_spotlight.png', dpi=150, bbox_inches='tight')
plt.close(figE)
print("figE done")

# =========================================================================
# Fig F: 全ミネラル 全グループ ヒートマップ
# =========================================================================
import matplotlib.colors as mcolors

min_items = {
    'ナトリウム(mg)': sodium,
    'カリウム(mg)':   potassium,
    'カルシウム(mg)': calcium,
    'マグネシウム(mg)':magnesium,
    'リン(mg)':       phosphorus,
    '鉄(mg)':         iron,
    '亜鉛(mg)':       zinc,
    '銅(mg)':         copper,
    'マンガン(mg)':   manganese,
    'コレステロール(mg)': cholesterol,
}

matrix = []
for key, dat in min_items.items():
    row = dat['m'] + dat['f']
    matrix.append(row)

matrix = np.array(matrix, dtype=float)
# z-score per row for color comparison
matrix_z = (matrix - matrix.mean(axis=1, keepdims=True)) / (matrix.std(axis=1, keepdims=True) + 1e-9)

figF, ax4 = plt.subplots(figsize=(12, 7))
im = ax4.imshow(matrix_z, aspect='auto', cmap='RdYlBu_r', vmin=-2, vmax=2)
ax4.set_xticks(np.arange(9))
ax4.set_xticklabels(all_parts, fontproperties=fp, fontsize=12)
ax4.set_yticks(np.arange(len(min_items)))
ax4.set_yticklabels(list(min_items.keys()), fontproperties=fp, fontsize=11)

for i in range(len(min_items)):
    for j in range(9):
        raw = matrix[i, j]
        fmt = f'{raw:.0f}' if raw >= 10 else f'{raw:.1f}'
        ax4.text(j, i, fmt, ha='center', va='center', fontsize=8.5,
                 color='white' if abs(matrix_z[i,j]) > 1.2 else 'black')

ax4.axvline(4.5, color='black', lw=2.5)
ax4.set_title('ミネラル摂取量 ヒートマップ（行内Zスコアで色付け）',
              fontproperties=fp, fontsize=13, fontweight='bold')
cbar = figF.colorbar(im, ax=ax4, orientation='vertical', fraction=0.03)
cbar.set_label('Zスコア（行内）', fontproperties=fp, fontsize=10)

# gender labels above
ax4.text(2.0, -0.8, '男性', ha='center', fontproperties=fp, fontsize=11, color=CM, fontweight='bold')
ax4.text(6.5, -0.8, '女性', ha='center', fontproperties=fp, fontsize=11, color=CF, fontweight='bold')

figF.tight_layout()
figF.savefig('/home/user/AK/figF_mineral_heatmap.png', dpi=150, bbox_inches='tight')
plt.close(figF)
print("figF done")

print("\nAll figures saved.")
