import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib import font_manager

font_path = '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf'
font_prop = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()
plt.rcParams['axes.unicode_minus'] = False

# ---- Data ----------------------------------------------------------------
parts_m = ['A', 'B', 'C', 'D', 'E']
parts_f = ['F', 'G', 'H', 'I']

age_m   = [16.8, 45.5, 26.0, 39.5, 22.2]
age_f   = [17.0, 22.0, 26.3, 25.3]
ht_m    = [168.0, 176.3, 173.7, 169.5, 172.2]
ht_f    = [151.0, 159.0, 163.3, 159.3]
wt_m    = [58.2, 66.3, 69.0, 57.0, 62.2]
wt_f    = [45.0, 50.0, 60.7, 54.0]

data = {
    '穀類':          {'m': [536.4,516.0,509.6,523.8,539.3], 'f': [382.1,350.7,334.9,341.7]},
    'いも類':        {'m': [48.6,37.9,41.2,39.6,43.9],      'f': [72.8,48.7,46.2,46.5]},
    '豆類':          {'m': [90.5,58.3,75.1,67.0,63.6],      'f': [71.3,76.7,74.7,90.7]},
    '野菜類':        {'m': [335.1,311.5,308.5,318.7,341.5], 'f': [515.7,331.2,265.6,300.9]},
    '果物':          {'m': [114.8,45.5,197.4,101.0,116.1],  'f': [114.2,106.9,116.9,116.3]},
    '魚介類':        {'m': [110.7,100.7,98.7,103.0,119.9],  'f': [84.4,95.8,73.0,79.0]},
    '肉類':          {'m': [111.2,84.6,116.3,88.0,132.0],   'f': [71.4,67.7,62.0,66.2]},
    '卵類':          {'m': [40.8,39.6,39.3,40.3,40.6],      'f': [32.8,32.8,31.3,31.6]},
    '乳類':          {'m': [188.0,137.1,104.8,153.9,125.5], 'f': [119.1,186.6,126.8,144.7]},
    '菓子類':        {'m': [31.8,31.6,31.5,32.5,40.4],      'f': [43.5,39.3,47.1,43.2]},
    '非アルコール飲料':{'m':[581.7,597.3,476.0,551.4,505.1],'f': [607.7,762.5,698.8,554.5]},
    '海藻類':        {'m': [13.9,10.1,9.0,13.0,8.8],        'f': [18.8,11.5,8.4,10.0]},
}

categories = list(data.keys())
avg_m = [np.mean(data[c]['m']) for c in categories]
avg_f = [np.mean(data[c]['f']) for c in categories]

COLOR_M = '#3A7FC1'
COLOR_F = '#E05C7A'
COLOR_M_LIGHT = '#A8C8E8'
COLOR_F_LIGHT = '#F0AABB'

# =========================================================================
# Figure 1: 男女平均比較 (横棒グラフ)
# =========================================================================
fig1, ax = plt.subplots(figsize=(12, 8))
y = np.arange(len(categories))
h = 0.35

bars_m = ax.barh(y + h/2, avg_m, h, color=COLOR_M, label='男性 (A–E 平均)', zorder=3)
bars_f = ax.barh(y - h/2, avg_f, h, color=COLOR_F, label='女性 (F–I 平均)', zorder=3)

ax.set_yticks(y)
ax.set_yticklabels(categories, fontproperties=font_prop, fontsize=12)
ax.set_xlabel('摂取量 (g/日)', fontproperties=font_prop, fontsize=11)
ax.set_title('食品群別 摂取量の男女比較（グループ平均）', fontproperties=font_prop, fontsize=15, fontweight='bold', pad=14)
ax.legend(prop=font_prop, fontsize=11)
ax.grid(axis='x', linestyle='--', alpha=0.4, zorder=0)
ax.set_axisbelow(True)

for bar in bars_m:
    ax.text(bar.get_width()+5, bar.get_y()+bar.get_height()/2,
            f'{bar.get_width():.0f}', va='center', ha='left', fontsize=8.5, color=COLOR_M)
for bar in bars_f:
    ax.text(bar.get_width()+5, bar.get_y()+bar.get_height()/2,
            f'{bar.get_width():.0f}', va='center', ha='left', fontsize=8.5, color=COLOR_F)

fig1.tight_layout()
fig1.savefig('/home/user/AK/fig1_gender_comparison.png', dpi=150, bbox_inches='tight')
plt.close(fig1)
print("fig1 done")

# =========================================================================
# Figure 2: レーダーチャート（男女バランス比較）
# =========================================================================
radar_cats = ['穀類', '野菜類', '果物', '魚介類', '肉類', '乳類', '豆類', '卵類', '菓子類']
vals_m = [np.mean(data[c]['m']) for c in radar_cats]
vals_f = [np.mean(data[c]['f']) for c in radar_cats]
all_max = [max(m, f)*1.15 for m, f in zip(vals_m, vals_f)]

angles = np.linspace(0, 2*np.pi, len(radar_cats), endpoint=False).tolist()
angles += angles[:1]
vals_m_r = vals_m + vals_m[:1]
vals_f_r = vals_f + vals_f[:1]
all_max_r = all_max + all_max[:1]

fig2, ax2 = plt.subplots(figsize=(8,8), subplot_kw=dict(polar=True))
ax2.plot(angles, vals_m_r, 'o-', color=COLOR_M, linewidth=2, label='男性平均')
ax2.fill(angles, vals_m_r, alpha=0.2, color=COLOR_M)
ax2.plot(angles, vals_f_r, 's-', color=COLOR_F, linewidth=2, label='女性平均')
ax2.fill(angles, vals_f_r, alpha=0.2, color=COLOR_F)

ax2.set_thetagrids(np.degrees(angles[:-1]),
                   labels=radar_cats,
                   fontproperties=font_prop, fontsize=12)
ax2.set_yticklabels([])
ax2.set_title('食品バランス レーダーチャート\n（男女グループ平均）',
              fontproperties=font_prop, fontsize=14, fontweight='bold', pad=25)
ax2.legend(loc='upper right', bbox_to_anchor=(1.3, 1.15), prop=font_prop, fontsize=11)
fig2.tight_layout()
fig2.savefig('/home/user/AK/fig2_radar.png', dpi=150, bbox_inches='tight')
plt.close(fig2)
print("fig2 done")

# =========================================================================
# Figure 3: 各グループの摂取量詳細（スタック棒グラフ）
# =========================================================================
all_parts = parts_m + parts_f
stack_cats = ['穀類', '野菜類', '肉類', '魚介類', '乳類', '豆類', '果物', '卵類', 'いも類', '菓子類']
stack_colors = ['#F4A620','#5BA85A','#C0392B','#2980B9','#F0E0A0','#8E44AD','#E67E22','#F39C12','#95A5A6','#E91E8C']

vals_by_part = []
for i, part in enumerate(all_parts):
    row = []
    for cat in stack_cats:
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
for j, cat in enumerate(stack_cats):
    vals = [vals_by_part[i][j] for i in range(len(all_parts))]
    ax3.bar(x, vals, bottom=bottoms, color=stack_colors[j], label=cat, zorder=3)
    bottoms += np.array(vals)

ax3.set_xticks(x)
xticklabels = [('男' if p in parts_m else '女') + '\n' + p for p in all_parts]
ax3.set_xticklabels(xticklabels, fontproperties=font_prop, fontsize=12)
ax3.set_ylabel('摂取量 (g/日)', fontproperties=font_prop, fontsize=11)
ax3.set_title('グループ別 食品摂取量（積み上げ棒グラフ）', fontproperties=font_prop, fontsize=14, fontweight='bold')
ax3.axvline(x=4.5, color='black', linewidth=2, linestyle='--', alpha=0.6)
ax3.text(2.0, ax3.get_ylim()[1]*0.98 if ax3.get_ylim()[1]>0 else 2500,
         '男性グループ', ha='center', fontproperties=font_prop, fontsize=11, color=COLOR_M, fontweight='bold')
ax3.text(6.5, ax3.get_ylim()[1]*0.98 if ax3.get_ylim()[1]>0 else 2500,
         '女性グループ', ha='center', fontproperties=font_prop, fontsize=11, color=COLOR_F, fontweight='bold')
ax3.legend(prop=font_prop, fontsize=9, loc='upper right', ncol=2)
ax3.grid(axis='y', linestyle='--', alpha=0.4, zorder=0)
ax3.set_axisbelow(True)
fig3.tight_layout()
fig3.savefig('/home/user/AK/fig3_stacked.png', dpi=150, bbox_inches='tight')
plt.close(fig3)
print("fig3 done")

# =========================================================================
# Figure 4: 身体特性（年齢・身長・体重）散布図
# =========================================================================
fig4, axes = plt.subplots(1, 3, figsize=(14, 5))

metrics = [
    ('年齢 (歳)', age_m, age_f),
    ('身長 (cm)', ht_m, ht_f),
    ('体重 (kg)', wt_m, wt_f),
]

for ax4, (label, vm, vf) in zip(axes, metrics):
    jitter_m = np.random.uniform(-0.08, 0.08, len(vm))
    jitter_f = np.random.uniform(-0.08, 0.08, len(vf))
    ax4.scatter([1+j for j in jitter_m], vm, s=120, color=COLOR_M, zorder=4, edgecolors='white', linewidths=1.2)
    ax4.scatter([2+j for j in jitter_f], vf, s=120, color=COLOR_F, zorder=4, edgecolors='white', linewidths=1.2, marker='s')

    # mean lines
    ax4.hlines(np.mean(vm), 0.7, 1.3, colors=COLOR_M, linewidths=2.5, linestyles='-', zorder=3)
    ax4.hlines(np.mean(vf), 1.7, 2.3, colors=COLOR_F, linewidths=2.5, linestyles='-', zorder=3)

    # box
    for x_pos, vals, col in [(1, vm, COLOR_M), (2, vf, COLOR_F)]:
        q1, q3 = np.percentile(vals, [25, 75])
        ax4.vlines(x_pos, q1, q3, colors=col, linewidths=8, alpha=0.25, zorder=2)

    for i, (part, v) in enumerate(zip(parts_m, vm)):
        ax4.annotate(part, (1+jitter_m[i], v), textcoords='offset points',
                     xytext=(6,0), fontsize=8, color=COLOR_M, fontproperties=font_prop)
    for i, (part, v) in enumerate(zip(parts_f, vf)):
        ax4.annotate(part, (2+jitter_f[i], v), textcoords='offset points',
                     xytext=(6,0), fontsize=8, color=COLOR_F, fontproperties=font_prop)

    ax4.set_xticks([1, 2])
    ax4.set_xticklabels(['男性', '女性'], fontproperties=font_prop, fontsize=12)
    ax4.set_ylabel(label, fontproperties=font_prop, fontsize=11)
    ax4.set_title(label, fontproperties=font_prop, fontsize=12, fontweight='bold')
    ax4.set_xlim(0.5, 2.7)
    ax4.grid(axis='y', linestyle='--', alpha=0.4)

    ax4.text(1, np.mean(vm), f'  平均\n  {np.mean(vm):.1f}', va='center',
             fontsize=8.5, color=COLOR_M, fontproperties=font_prop)
    ax4.text(2, np.mean(vf), f'  平均\n  {np.mean(vf):.1f}', va='center',
             fontsize=8.5, color=COLOR_F, fontproperties=font_prop)

fig4.suptitle('グループ別 身体特性（年齢・身長・体重）', fontproperties=font_prop, fontsize=14, fontweight='bold')
m_patch = mpatches.Patch(color=COLOR_M, label='男性 (A–E)')
f_patch = mpatches.Patch(color=COLOR_F, label='女性 (F–I)')
fig4.legend(handles=[m_patch, f_patch], prop=font_prop, fontsize=11,
            loc='upper right', bbox_to_anchor=(0.99, 0.95))
fig4.tight_layout()
fig4.savefig('/home/user/AK/fig4_body_metrics.png', dpi=150, bbox_inches='tight')
plt.close(fig4)
print("fig4 done")

# =========================================================================
# Figure 5: 注目ポイント（男女差が大きい食品群）
# =========================================================================
diffs = {c: np.mean(data[c]['m']) - np.mean(data[c]['f']) for c in categories}
sorted_cats = sorted(diffs, key=lambda c: abs(diffs[c]), reverse=True)[:8]
sorted_diffs = [diffs[c] for c in sorted_cats]
colors_diff = [COLOR_M if d > 0 else COLOR_F for d in sorted_diffs]

fig5, ax5 = plt.subplots(figsize=(10, 6))
bars = ax5.barh(sorted_cats[::-1], sorted_diffs[::-1], color=colors_diff[::-1], zorder=3, edgecolor='white')
ax5.axvline(0, color='black', linewidth=1.2)
ax5.set_xlabel('男性平均 − 女性平均 (g/日)', fontproperties=font_prop, fontsize=11)
ax5.set_title('男女差が大きい食品群\n（＋：男性が多い　−：女性が多い）',
              fontproperties=font_prop, fontsize=13, fontweight='bold')
ax5.set_yticklabels(sorted_cats[::-1], fontproperties=font_prop, fontsize=12)
for bar, val in zip(bars, sorted_diffs[::-1]):
    offset = 5 if val >= 0 else -5
    ha = 'left' if val >= 0 else 'right'
    ax5.text(val + offset, bar.get_y()+bar.get_height()/2,
             f'{val:+.0f}g', va='center', ha=ha, fontsize=9,
             color=COLOR_M if val > 0 else COLOR_F, fontweight='bold')
ax5.grid(axis='x', linestyle='--', alpha=0.4, zorder=0)
m_patch = mpatches.Patch(color=COLOR_M, label='男性が多い')
f_patch = mpatches.Patch(color=COLOR_F, label='女性が多い')
ax5.legend(handles=[m_patch, f_patch], prop=font_prop, fontsize=10)
fig5.tight_layout()
fig5.savefig('/home/user/AK/fig5_gender_diff.png', dpi=150, bbox_inches='tight')
plt.close(fig5)
print("fig5 done")

print("All figures saved.")
