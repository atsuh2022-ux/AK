"""
create_proposal.py
食事調査・食意識アンケート結果に基づく 1年間栄養サポート計画 提案書を生成。
Word文書（.docx）と年間タイムライン図（.png）を出力する。
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib import font_manager
from docx import Document
from docx.shared import Pt, RGBColor, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

font_path = '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf'
fp = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.family'] = fp.get_name()
plt.rcParams['axes.unicode_minus'] = False

# =========================================================================
# ① 年間タイムライン図
# =========================================================================
months = ['9月\n2025', '10月', '11月', '12月', '1月\n2026', '2月', '3月', '4月', '5月', '6月', '7月', '8月']
n = len(months)

# 活動定義: (月インデックス0-11, ラベル, 方法, 色)
# 方法: 'direct'=直接指導, 'pdf'=PDF送付, 'both'=両方
CDIRECT = '#2563EB'   # 直接指導
CPDF    = '#16A34A'   # PDF送付
CBOTH   = '#9333EA'   # 両方

activities = [
    # (月, ラベル, color, y位置)
    (0,  '★キックオフ講義\n食事調査フィードバック\nエネルギー・PFCの基礎\n個人目標設定', CDIRECT, 3.5),
    (1,  '自炊レシピ集\n（PDF送付）',             CPDF,    2.2),
    (2,  '秋季試合期\n栄養ガイド（PDF）',          CPDF,    3.5),
    (3,  'ウエイトコントロール\n年間計画書（PDF）', CPDF,    2.2),
    (4,  '年始・冬季\n食事管理（PDF）',            CPDF,    3.5),
    (5,  '★試合期栄養戦略\nカーボローディング\nサプリメント適正使用',CDIRECT, 2.2),
    (6,  '海外遠征\n食事計画書（PDF）',            CPDF,    3.5),
    (7,  '免疫・腸内環境\n栄養（PDF）',            CPDF,    2.2),
    (8,  '★夏季強化合宿\n暑熱下水分管理\nコンディション講義', CDIRECT, 3.5),
    (9,  '夏季大会\n栄養戦略（PDF）',              CPDF,    2.2),
    (10, '暑熱・電解質\n管理（PDF）',              CPDF,    3.5),
    (11, '年間振り返り\n次年度計画（PDF）',        CPDF,    2.2),
]

fig_tl, ax = plt.subplots(figsize=(20, 8))
ax.set_xlim(-0.5, n - 0.5)
ax.set_ylim(0, 5.5)
ax.axis('off')

# 月ラベル背景
for i, m in enumerate(months):
    color = '#1E3A5F' if i % 2 == 0 else '#2E4F7F'
    ax.add_patch(mpatches.FancyBboxPatch((i-0.45, 4.8), 0.9, 0.6,
                  boxstyle='round,pad=0.02', fc=color, ec='none', zorder=2))
    ax.text(i, 5.1, m, ha='center', va='center', fontsize=8.5,
            fontproperties=fp, color='white', fontweight='bold', zorder=3)

# タイムライン軸
ax.hlines(4.75, -0.5, n-0.5, colors='#1E3A5F', lw=3, zorder=1)

# 活動バブル
for (mi, lbl, col, y) in activities:
    ax.annotate('', xy=(mi, 4.72), xytext=(mi, y+0.5),
                arrowprops=dict(arrowstyle='->', color=col, lw=1.5))
    ax.add_patch(mpatches.FancyBboxPatch((mi-0.44, y-0.05), 0.88, 0.6+lbl.count('\n')*0.32,
                  boxstyle='round,pad=0.06', fc=col, ec='white', lw=1.5,
                  alpha=0.92, zorder=3))
    ax.text(mi, y + 0.3 + lbl.count('\n')*0.16, lbl,
            ha='center', va='center', fontsize=7.5,
            fontproperties=fp, color='white', fontweight='bold',
            zorder=4, linespacing=1.35)

# 凡例
handles = [
    mpatches.Patch(fc=CDIRECT, label='★ 直接指導（強化研修会・合宿）'),
    mpatches.Patch(fc=CPDF,    label='PDF資料送付'),
]
ax.legend(handles=handles, prop=fp, fontsize=10,
          loc='lower center', bbox_to_anchor=(0.5, -0.02),
          ncol=2, frameon=True, edgecolor='gray')

ax.set_title('年間栄養サポート計画　タイムライン（2025年9月〜2026年8月）',
             fontproperties=fp, fontsize=14, fontweight='bold', pad=14)

fig_tl.tight_layout()
fig_tl.savefig('/home/user/AK/proposal_timeline.png', dpi=150, bbox_inches='tight')
plt.close(fig_tl)
print("タイムライン図 完了")

# =========================================================================
# ② Word 提案書
# =========================================================================
doc = Document()

# ── ページ設定 ──────────────────────────────────────────────
section = doc.sections[0]
section.page_width  = Cm(21)
section.page_height = Cm(29.7)
section.top_margin    = Cm(2.0)
section.bottom_margin = Cm(2.0)
section.left_margin   = Cm(2.5)
section.right_margin  = Cm(2.5)

# ── スタイルヘルパー ─────────────────────────────────────────
def set_font(run, size, bold=False, color=None):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = 'メイリオ'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'メイリオ')
    if color:
        run.font.color.rgb = RGBColor(*color)

def add_heading(doc, text, level=1):
    colors = {1: (30, 58, 95), 2: (37, 99, 235), 3: (22, 163, 74)}
    sizes  = {1: 16, 2: 13, 3: 11}
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after  = Pt(4)
    if level == 1:
        p.paragraph_format.space_before = Pt(6)
        # 背景色付きブロック風
        run = p.add_run(f'■ {text}')
    elif level == 2:
        run = p.add_run(f'▶ {text}')
    else:
        run = p.add_run(f'◆ {text}')
    set_font(run, sizes[level], bold=True, color=colors[level])
    return p

def add_bullet(doc, text, indent=0):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.left_indent = Cm(0.5 + indent * 0.8)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(text)
    set_font(run, 10)
    return p

def add_body(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(3)
    run = p.add_run(text)
    set_font(run, 10)
    return p

def set_cell_bg(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def add_cell_text(cell, text, size=9, bold=False, color=None, align='left'):
    cell.text = ''
    p = cell.paragraphs[0]
    p.alignment = {'left': WD_ALIGN_PARAGRAPH.LEFT,
                   'center': WD_ALIGN_PARAGRAPH.CENTER}.get(align, WD_ALIGN_PARAGRAPH.LEFT)
    run = p.add_run(text)
    set_font(run, size, bold=bold, color=color)

# ── 表紙 ────────────────────────────────────────────────────
p_title = doc.add_paragraph()
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_title.paragraph_format.space_before = Pt(30)
p_title.paragraph_format.space_after  = Pt(6)
run = p_title.add_run('栄養サポート計画 提案書')
set_font(run, 22, bold=True, color=(30, 58, 95))

p_sub = doc.add_paragraph()
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_sub.paragraph_format.space_after = Pt(4)
run = p_sub.add_run('〜食事調査・食意識アンケート結果に基づく年間栄養サポートの提案〜')
set_font(run, 12, color=(71, 85, 105))

p_date = doc.add_paragraph()
p_date.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_date.paragraph_format.space_before = Pt(6)
run = p_date.add_run('作成：管理栄養士　　2025年9月')
set_font(run, 10, color=(100, 116, 139))

doc.add_paragraph()

# ── 1. 調査概要 ─────────────────────────────────────────────
add_heading(doc, '1．調査概要', 1)
add_body(doc, '本提案は、以下2つの調査から得られた結果を踏まえて作成した年間栄養サポート計画です。')

tbl0 = doc.add_table(rows=3, cols=3)
tbl0.style = 'Table Grid'
tbl0.alignment = WD_TABLE_ALIGNMENT.CENTER
headers0 = ['調査名', '対象', '主な内容']
for j, h in enumerate(headers0):
    set_cell_bg(tbl0.rows[0].cells[j], '1E3A5F')
    add_cell_text(tbl0.rows[0].cells[j], h, size=10, bold=True, color=(255,255,255), align='center')
rows0 = [
    ('食環境・食意識アンケート', '競技団体所属選手（男女）', '食事環境・意識・サプリメント・コンディション'),
    ('食事調査（3日間食事記録）', '同上（A〜Iの9グループ）', 'エネルギー・栄養素摂取量、食品群別摂取量'),
]
for i, row_data in enumerate(rows0, 1):
    bg = 'FFFFFF' if i % 2 == 1 else 'EFF6FF'
    for j, val in enumerate(row_data):
        set_cell_bg(tbl0.rows[i].cells[j], bg)
        add_cell_text(tbl0.rows[i].cells[j], val, size=9)

doc.add_paragraph()

# ── 2. 現状と課題 ──────────────────────────────────────────
add_heading(doc, '2．現状分析と競技団体全体の課題', 1)

# 課題1
add_heading(doc, '課題① エネルギー・炭水化物・微量栄養素の摂取不足', 2)
add_body(doc, '食事調査の結果、以下の栄養素で摂取量が食事摂取基準2025年版の推奨量・目安量を下回る、'
              'または競技者として不十分な傾向が認められました。')
items1 = [
    '炭水化物：男性平均 5.2 g/kg BW、女性平均 4.6 g/kg BW。'
     '競技者の推奨量（6〜10 g/kg BW）に対して不足している可能性がある。',
    'カルシウム：男性 推奨量800 mg に対し平均610 mg、女性 推奨量650 mg に対し平均589 mg。'
     '骨強度・筋収縮への影響が懸念される。',
    'ビタミンD：全グループの平均摂取量が食事摂取基準2025年版目安量（12.0 µg）を下回る。'
     '免疫機能・骨代謝・筋機能への影響が懸念される。',
    'ビタミンB1：女性の一部グループで推奨量（1.1 mg）を下回る。'
     'エネルギー代謝効率の低下につながる可能性がある。',
    '食物繊維：多くのグループで目安量（男性21 g、女性18 g）を下回る。'
     '腸内環境・免疫機能への影響がある。',
    '食塩相当量：全グループが目標量（男性 7.5 g、女性 6.5 g）を超過。'
     '高強度トレーニング時の電解質管理の観点から個別指導が必要。',
]
for it in items1:
    add_bullet(doc, it)

# 課題2
add_heading(doc, '課題② ウエイトコントロールの知識・スキル不足', 2)
items2 = [
    'アンケートで「ウエイトコントロール」への学習意欲が最上位グループに入っており、'
     '増量・減量に課題を抱える選手が多いと推察される。',
    '食事調査では体重あたりのエネルギー・たんぱく質摂取量にグループ間差が見られ、'
     '個人の競技目標に合った食事計画が必要である。',
    '不適切な減量（急速減量・栄養欠乏）はパフォーマンス低下・怪我リスク増大につながる。',
]
for it in items2:
    add_bullet(doc, it)

# 課題3
add_heading(doc, '課題③ 試合期・海外遠征時の食事管理', 2)
items3 = [
    'アンケートで「試合期の栄養補給」「合宿・大会帯同・補食提供」へのニーズが高い。',
    '実際にインド大会で大幅な体重減少（脱水・エネルギー不足の可能性）を来した選手がいた。',
    '海外遠征では食材・衛生環境が変わるため、事前の食事計画と現地での実践スキルが必要。',
    '競技前のカーボローディング、試合中の補食・水分補給、試合後の回復栄養など、'
     '試合周辺期の戦略を選手自身が実行できるレベルに引き上げることが重要。',
]
for it in items3:
    add_bullet(doc, it)

# 課題4
add_heading(doc, '課題④ サプリメントの情報源とリスク管理', 2)
items4 = [
    '9割以上の選手がサプリメントを使用しており、プロテイン・アミノ酸が最多。',
    '情報源の上位は「指導者・チームメイト」「SNS」であり、科学的根拠に基づく情報提供が不足している。',
    'アンチドーピングの観点から、製品選択・使用タイミング・用量に関する正確な知識が不可欠。',
]
for it in items4:
    add_bullet(doc, it)

# 課題5
add_heading(doc, '課題⑤ 自炊スキル・実践的な食事づくりのサポート不足', 2)
items5 = [
    'アンケートより、自炊で食事を担当する選手が多数を占める。',
    'アンケートで「レシピ等の実践的な情報提供」へのニーズが最も高かった。',
    '食事に対する意識・意欲は高いものの、具体的な知識・スキルの不足が栄養摂取の課題につながっている可能性がある。',
]
for it in items5:
    add_bullet(doc, it)

# ── 3. 年間計画 ────────────────────────────────────────────
add_heading(doc, '3．年間栄養サポート計画（2025年9月〜2026年8月）', 1)
add_body(doc, '直接指導（強化研修会・強化合宿）とPDF資料送付を組み合わせ、'
              '選手が日常的に栄養を実践できる環境を段階的に整えます。')

# 年間計画表
plan_data = [
    # (時期, 方法, テーマ, 内容・解決する課題)
    ('2025年\n9月中旬',
     '★直接指導\n（強化研修会・合宿）',
     'キックオフ：\n調査結果FB＋基礎講義',
     '① 食事調査・アンケート結果のフィードバック（全体）\n'
     '② 競技者のエネルギー・PFC・炭水化物の考え方\n'
     '③ 個人別食事目標の設定ワーク\n'
     '④ カルシウム・ビタミンD不足対策の食選び\n'
     '→ 課題①⑤に対応'),
    ('2025年\n10月',
     'PDF送付',
     '自炊選手向け\n実践レシピ集',
     '① 高炭水化物・高カルシウムレシピ10選\n'
     '② 1週間献立モデル（自炊版）\n'
     '③ 時短調理のコツ・食材の使い回し術\n'
     '→ 課題①⑤に対応'),
    ('2025年\n11月',
     'PDF送付',
     '秋季試合期\n栄養ガイド',
     '① 試合前日・当日の食事プロトコル\n'
     '② 補食の選び方・タイミング（コンビニ活用含む）\n'
     '③ 試合後の回復食（たんぱく質・炭水化物の組み合わせ）\n'
     '→ 課題③に対応'),
    ('2025年\n12月',
     'PDF送付',
     'ウエイトコントロール\n年間計画書',
     '① 増量・減量の基本原則（エネルギーバランス）\n'
     '② 月別体重管理スケジュール作成テンプレート\n'
     '③ 急速減量のリスクと安全な減量ペース\n'
     '→ 課題②に対応'),
    ('2026年\n1月',
     'PDF送付',
     '冬季トレーニング期\n栄養管理',
     '① 冬季の免疫維持（ビタミンD・C・亜鉛）\n'
     '② 寒冷環境での水分補給\n'
     '③ 年始の食生活リセットガイド\n'
     '→ 課題①に対応'),
    ('2026年\n2〜3月',
     '★直接指導\n（強化研修会・合宿）\n※開催があれば',
     '試合期栄養戦略＋\nサプリメント講義',
     '① カーボローディングの実践法\n'
     '② 競技中の水分・電解質・補食戦略\n'
     '③ サプリメント適正使用（アンチドーピング含む）\n'
     '④ プロテイン・アミノ酸の効果的な使い方\n'
     '→ 課題③④に対応'),
    ('2026年\n3〜4月',
     'PDF送付',
     '海外遠征\n食事計画ガイド',
     '① 遠征前の準備チェックリスト（持参食材・サプリ）\n'
     '② 現地での食事選択のポイント（食の安全・衛生）\n'
     '③ 水分・電解質管理（脱水・体重変動の防止）\n'
     '④ 個人別遠征食事計画テンプレート\n'
     '→ 課題③に対応'),
    ('2026年\n5〜6月',
     '★直接指導\n（強化合宿）\n※開催があれば',
     '夏季強化期\nコンディション管理',
     '① 暑熱環境下の水分・電解質補給\n'
     '② 腸内環境・免疫栄養（食物繊維・発酵食品）\n'
     '③ 合宿中の食事セルフチェックワーク\n'
     '→ 課題①③に対応'),
    ('2026年\n7〜8月',
     'PDF送付',
     '夏季大会\n栄養戦略',
     '① 高温多湿下のパフォーマンス維持栄養\n'
     '② 試合スケジュール別の食事タイムライン\n'
     '③ 夏季の食欲低下・胃腸トラブル対策\n'
     '→ 課題③に対応'),
    ('2026年\n9月',
     'PDF送付\n（次回合宿準備）',
     '年間振り返り＆\n次年度計画',
     '① 1年間の取り組みの振り返りアンケート\n'
     '② 個人別達成度評価\n'
     '③ 次年度栄養サポート方針の提示\n'
     '→ 全課題の総括'),
]

tbl = doc.add_table(rows=len(plan_data)+1, cols=4)
tbl.style = 'Table Grid'
tbl.alignment = WD_TABLE_ALIGNMENT.CENTER

# 列幅設定
col_widths = [Cm(2.2), Cm(3.0), Cm(3.8), Cm(7.8)]
for row in tbl.rows:
    for j, w in enumerate(col_widths):
        row.cells[j].width = w

# ヘッダー
headers = ['時期', '実施方法', 'テーマ', '内容（対応課題）']
for j, h in enumerate(headers):
    set_cell_bg(tbl.rows[0].cells[j], '1E3A5F')
    add_cell_text(tbl.rows[0].cells[j], h, size=9, bold=True,
                  color=(255,255,255), align='center')

# データ行
for i, (jiki, method, theme, content) in enumerate(plan_data, 1):
    bg = 'FFFFFF' if i % 2 == 1 else 'EFF6FF'
    is_direct = '★' in method
    if is_direct:
        bg = 'FFF7ED'  # 直接指導は薄オレンジ
    cells = tbl.rows[i].cells
    for j in range(4):
        set_cell_bg(cells[j], bg)
    add_cell_text(cells[0], jiki,    size=9, bold=is_direct, align='center')
    col = (180, 50, 20) if is_direct else (22, 101, 52)
    add_cell_text(cells[1], method,  size=9, bold=is_direct, color=col)
    add_cell_text(cells[2], theme,   size=9, bold=True)
    add_cell_text(cells[3], content, size=8.5)

doc.add_paragraph()
p_note = doc.add_paragraph()
run = p_note.add_run('※ 橙色行：直接指導（強化研修会・合宿）　青色行：PDF資料送付')
set_font(run, 8.5, color=(100, 116, 139))
run2 = p_note.add_run('\n※ 直接指導の機会は開催日程に応じて調整します。PDF送付は原則月1回を目安とします。')
set_font(run2, 8.5, color=(100, 116, 139))

# ── 4. 各課題と対策のまとめ ───────────────────────────────────
add_heading(doc, '4．課題別 解決策まとめ', 1)

solution_data = [
    ('課題①\nエネルギー・微量\n栄養素の不足',
     '・炭水化物の量と質（主食の摂り方）を講義で指導\n'
     '・カルシウム食品（乳製品・小魚・大豆）の積極的活用レシピを提供\n'
     '・ビタミンD向上のため、鮭・さんまなどの脂肪魚料理をレシピ集に掲載\n'
     '・食物繊維を意識した副菜選びガイドをPDFで提供'),
    ('課題②\nウエイトコントロール',
     '・増量・減量の基本原則を講義で解説\n'
     '・月別体重管理スケジュールテンプレートを提供し自己管理を促す\n'
     '・急速減量のリスク教育（骨格筋量の低下・免疫低下など）\n'
     '・食事調査データを用いた個人フィードバック（エネルギー摂取量の適正化）'),
    ('課題③\n試合期・海外遠征',
     '・試合前・中・後の食事プロトコルをPDFで提供\n'
     '・海外遠征食事計画テンプレート（現地食品のポイント・持参食品リスト）の配布\n'
     '・水分・電解質管理の実践的な方法（体重測定での脱水チェックなど）を指導\n'
     '・強化合宿での補食実演・試食を実施'),
    ('課題④\nサプリメント管理',
     '・サプリメント講義でエビデンスに基づく情報提供（効果・副作用・タイミング）\n'
     '・アンチドーピング対応製品の見分け方（INFORMEDsport等の認証マーク）\n'
     '・プロテイン・アミノ酸の適切な用量・タイミングの個別指導\n'
     '・情報源としての管理栄養士活用を促進（相談窓口の設置を提案）'),
    ('課題⑤\n自炊スキル',
     '・簡単・時短・高栄養のレシピ集PDF（月1回更新）を配布\n'
     '・コンビニ・スーパーでの食品選択ガイドを提供\n'
     '・1週間分の献立モデルを季節ごとに作成\n'
     '・選手の食環境（一人暮らし・寮・自宅）に合わせた個別アドバイスを合宿時に実施'),
]

tbl2 = doc.add_table(rows=len(solution_data)+1, cols=2)
tbl2.style = 'Table Grid'
tbl2.alignment = WD_TABLE_ALIGNMENT.CENTER

for j, h in enumerate(['課題', '具体的な解決策']):
    set_cell_bg(tbl2.rows[0].cells[j], '1E3A5F')
    add_cell_text(tbl2.rows[0].cells[j], h, size=10, bold=True,
                  color=(255,255,255), align='center')

tbl2.rows[0].cells[0].width = Cm(3.2)
tbl2.rows[0].cells[1].width = Cm(13.6)

for i, (kadai, kaiketsu) in enumerate(solution_data, 1):
    bg = 'FFFFFF' if i % 2 == 1 else 'F0FDF4'
    for j in range(2):
        set_cell_bg(tbl2.rows[i].cells[j], bg)
    tbl2.rows[i].cells[0].width = Cm(3.2)
    tbl2.rows[i].cells[1].width = Cm(13.6)
    add_cell_text(tbl2.rows[i].cells[0], kadai, size=9, bold=True, align='center')
    add_cell_text(tbl2.rows[i].cells[1], kaiketsu, size=9)

doc.add_paragraph()

# ── 5. 優先的に取り組む短期目標 ─────────────────────────────
add_heading(doc, '5．優先的に取り組む短期目標（最初の3ヶ月）', 1)
add_body(doc, '9月の強化研修会・合宿を最初の重要な機会として、以下3点を最優先目標とします。')

priority = [
    ('目標①', '主食（炭水化物）の量を意識した食事づくりの習慣化',
     '→ 炭水化物不足はトレーニング効果・回復速度に直結するため最優先'),
    ('目標②', 'カルシウム・ビタミンD不足の解消',
     '→ 骨ストレス骨折・疲労骨折リスク低減のため早期対応が必要'),
    ('目標③', 'サプリメントの情報ソースを管理栄養士・信頼できる資料に切り替える',
     '→ アンチドーピング違反リスクの排除と最大限の効果発揮のため'),
]
for num, target, reason in priority:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(2)
    run1 = p.add_run(f'{num}　{target}\n')
    set_font(run1, 10, bold=True, color=(30, 58, 95))
    run2 = p.add_run(f'　　{reason}')
    set_font(run2, 9, color=(71, 85, 105))

doc.add_paragraph()

# ── 末尾メモ ─────────────────────────────────────────────────
add_heading(doc, '6．備考・今後の検討事項', 1)
bullets_last = [
    '本計画は2025年9月現在の情報をもとに作成しており、大会スケジュールや合宿日程の変更に応じて柔軟に修正します。',
    '個人対応が必要な選手（体重管理・怪我・食物アレルギー等）については、個別相談の機会を別途設けることを推奨します。',
    '食事調査は今後も定期的（年1回以上）に実施し、栄養サポートの効果を継続的に評価・改善します。',
    'PDF資料はLINEグループ・メール等で配布し、選手がいつでも参照できるよう保管を依頼します。',
    '指導者・コーチへの情報共有も並行して行い、練習環境と栄養サポートの連携を強化します。',
]
for b in bullets_last:
    add_bullet(doc, b)

# ── 保存 ────────────────────────────────────────────────────
out_docx = '/home/user/AK/nutrition_support_proposal.docx'
doc.save(out_docx)
print(f"提案書（Word）完了: {out_docx}")
