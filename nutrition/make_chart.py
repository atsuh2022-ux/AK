"""献立の栄養素充足率（1日の基準値に対する割合）を積み上げ棒グラフで描く。"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

font_manager.fontManager.addfont("/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf")
plt.rcParams["font.family"] = "IPAPGothic"

NUTRIENTS = ["エネルギー", "たんぱく質", "脂質", "炭水化物", "カルシウム", "鉄",
             "ビタミンA", "ビタミンB1", "ビタミンB2", "ビタミンC", "食物繊維"]

# 料理ごとの栄養量（日本食品標準成分表 八訂より算出）
DISHES = {
    "ご飯":             [234, 3.8, 0.5, 55.7, 5, 0.2, 0, 0.03, 0.02, 0, 2.3],
    "豚の生姜焼き":     [274, 16.8, 19.5, 7.5, 26, 0.6, 23, 0.58, 0.16, 23, 1.1],
    "ほうれん草の胡麻和え": [54, 2.8, 3.0, 5.5, 102, 1.1, 270, 0.05, 0.09, 11, 2.8],
    "豆腐の味噌汁":     [46, 3.9, 1.8, 4.5, 51, 1.0, 0, 0.03, 0.04, 1, 1.4],
    "オレンジ":         [42, 1.0, 0.1, 9.8, 21, 0.3, 10, 0.10, 0.03, 40, 0.8],
    "牛乳":             [122, 6.6, 7.6, 9.6, 220, 0.0, 76, 0.08, 0.30, 2, 0],
}

# 日本人の食事摂取基準（2020年版）男性・身体活動レベルⅡ
# 脂質・炭水化物は目標量（エネルギー比 20〜30%・50〜65%）の中央値をグラム換算
def standards(kcal, protein, ca, fe, va, b1, b2, vc, fiber):
    return [kcal, protein, kcal * 0.25 / 9, kcal * 0.575 / 4,
            ca, fe, va, b1, b2, vc, fiber]

AGES = {
    "12-14": ("12〜14歳", standards(2600, 60, 1000, 10.0, 800, 1.4, 1.6, 100, 17)),
    "15-17": ("15〜17歳", standards(2800, 65, 800, 10.0, 900, 1.5, 1.7, 100, 19)),
}

# 積み上げ順（下から）に固定順で色を割り当てる
COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"]
TEXT, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"


def draw(key):
    label, std = AGES[key]
    fig, ax = plt.subplots(figsize=(13, 7.2), dpi=150)
    x = range(len(NUTRIENTS))
    bottom = [0.0] * len(NUTRIENTS)
    for (name, vals), color in zip(DISHES.items(), COLORS):
        pct = [v / s * 100 for v, s in zip(vals, std)]
        ax.bar(x, pct, 0.6, bottom=bottom, color=color, label=name,
               edgecolor="white", linewidth=1.5)
        bottom = [b + p for b, p in zip(bottom, pct)]

    for i, total in enumerate(bottom):
        ax.text(i, total + 1.2, f"{total:.0f}%", ha="center", va="bottom",
                fontsize=11, color=TEXT)

    ax.axhline(100 / 3, color="#e34948", linestyle=(0, (4, 3)), linewidth=2)
    ax.text(1.01, 100 / 3, "1食分に\n必要な量\n（33%）",
            transform=ax.get_yaxis_transform(), ha="left", va="center",
            fontsize=11, color=TEXT, clip_on=False)

    ax.set_xticks(list(x), NUTRIENTS, rotation=40, ha="right", fontsize=12, color=TEXT)
    ax.set_ylabel("1日に必要な量に対する割合（%）", fontsize=12, color=MUTED)
    ax.set_ylim(0, max(max(bottom) + 10, 60))
    ax.tick_params(axis="y", colors=MUTED)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc="upper left", frameon=False, fontsize=11)
    ax.set_title(f"献立の栄養素充足率（思春期男性 {label}）", fontsize=16, color=TEXT, pad=14)
    fig.text(0.01, 0.01,
             "基準値：日本人の食事摂取基準（2020年版）男性・身体活動レベルⅡ。"
             "脂質・炭水化物は目標量（エネルギー比20〜30%・50〜65%）の中央値、食物繊維は目標量。",
             fontsize=9, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    out = f"/home/user/AK/nutrition/nutrient_chart_{key}.png"
    fig.savefig(out, facecolor="white")
    print(out)


for k in AGES:
    draw(k)
