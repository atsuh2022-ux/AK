"""
create_proposal_v2.py
2026年6月〜2027年3月 栄養サポート計画 提案書を生成。
・既往実績（2025年12月・2026年4月）を前提に計画を開始
・9月末アジア大会（愛知）を主要ターゲットに設定
・コンディション×食事記録の分析アドバイスを盛り込む
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import numpy as np
from matplotlib import font_manager
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

font_path = '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf'
fp = font_manager.FontProperties(fname=font_path)
plt.rcParams['font.family'] = fp.get_name()
plt.rcParams['axes.unicode_minus'] = False

# =========================================================================
# ① タイムライン図
# =========================================================================
# 過去2回 + 今後10ヶ月
months_all  = ['12月\n2025', '4月\n2026', '6月', '7月', '8月', '9月末\nアジア\n大会',
               '10月', '11月', '12月', '1〜2月\n2027', '3月']
n = len(months_all)

CPAST   = '#94A3B8'   # 既往（グレー）
CDIRECT = '#2563EB'   # 直接指導（青）
CPDF    = '#16A34A'   # PDF（緑）
CEVENT  = '#DC2626'   # 大会（赤）

# (月インデックス, ラベル, color, y位置, 種別)
activities = [
    (0,  '【既往①】\n食事バランス講義',                  CPAST,   3.2, 'past'),
    (1,  '【既往②】\nコンディション×\n食事記録を始めよう', CPAST,  2.0, 'past'),
    (2,  '★記録FB＋\nアジア大会\n栄養戦略講義',           CDIRECT, 3.5, 'direct'),
    (3,  'アジア大会\nカウントダウン\n栄養計画（PDF）',    CPDF,    2.0, 'pdf'),
    (4,  '試合直前・\n大会中プロトコル\n食環境整備（PDF）',CPDF,    3.5, 'pdf'),
    (5,  '🏆アジア大会\n（愛知）',                         CEVENT,  2.5, 'event'),
    (6,  '大会後回復＆\n記録振り返り（PDF）',              CPDF,    3.5, 'pdf'),
    (7,  'オフシーズン\n体組成管理（PDF）',                CPDF,    2.0, 'pdf'),
    (8,  '★記録データ活用\n年間振り返り講義',             CDIRECT, 3.5, 'direct'),
    (9,  '★次シーズン\n個人栄養計画\n立案ワーク',         CDIRECT, 2.0, 'direct'),
    (10, '新シーズン\n開幕準備（PDF）',                    CPDF,    3.5, 'pdf'),
]

fig_tl, ax = plt.subplots(figsize=(22, 8))
ax.set_xlim(-0.6, n - 0.4)
ax.set_ylim(0.8, 6.0)
ax.axis('off')

# 大会ゾーン（背景）
ax.axvspan(4.5, 5.5, alpha=0.08, color=CEVENT, zorder=0)
ax.text(5.0, 5.6, '▼ アジア大会期間', ha='center', fontproperties=fp,
        fontsize=9, color=CEVENT, fontweight='bold')

# 既往ゾーン
ax.axvspan(-0.6, 1.5, alpha=0.06, color=CPAST, zorder=0)
ax.text(0.5, 5.6, '【実施済み】', ha='center', fontproperties=fp,
        fontsize=9, color='#64748B', fontweight='bold')

# 今後ゾーン
ax.axvspan(1.5, n-0.4, alpha=0.03, color=CDIRECT, zorder=0)
ax.text(6.5, 5.6, '《今後の計画》', ha='center', fontproperties=fp,
        fontsize=9, color=CDIRECT, fontweight='bold')

# 月ラベル
for i, m in enumerate(months_all):
    is_event = (i == 5)
    color = '#7F1D1D' if is_event else ('#475569' if i < 2 else '#1E3A5F')
    ax.add_patch(mpatches.FancyBboxPatch((i-0.44, 4.75), 0.88, 0.7,
                  boxstyle='round,pad=0.03', fc=color, ec='none', zorder=2))
    ax.text(i, 5.1, m, ha='center', va='center', fontsize=8,
            fontproperties=fp, color='white', fontweight='bold', zorder=3)

# タイムライン軸
ax.hlines(4.72, -0.6, n-0.4, colors='#334155', lw=3, zorder=1)

# 活動バブル
for (mi, lbl, col, y, kind) in activities:
    lh = 0.5 + lbl.count('\n') * 0.28
    ax.annotate('', xy=(mi, 4.69), xytext=(mi, y + lh),
                arrowprops=dict(arrowstyle='->', color=col, lw=1.5))
    ax.add_patch(mpatches.FancyBboxPatch((mi-0.43, y-0.04), 0.86, lh+0.1,
                  boxstyle='round,pad=0.06', fc=col, ec='white', lw=1.5,
                  alpha=0.9, zorder=3))
    ax.text(mi, y + (lh+0.1)/2 - 0.04, lbl,
            ha='center', va='center', fontsize=7.5,
            fontproperties=fp, color='white', fontweight='bold',
            zorder=4, linespacing=1.3)

handles_legend = [
    mpatches.Patch(fc=CPAST,   label='実施済み講義'),
    mpatches.Patch(fc=CDIRECT, label='★ 直接指導（強化研修会・合宿）'),
    mpatches.Patch(fc=CPDF,    label='PDF資料送付'),
    mpatches.Patch(fc=CEVENT,  label='🏆 アジア大会（愛知・9月末）'),
]
ax.legend(handles=handles_legend, prop=fp, fontsize=9.5,
          loc='lower center', bbox_to_anchor=(0.5, -0.04),
          ncol=4, frameon=True, edgecolor='gray')

ax.set_title('栄養サポート計画 タイムライン　2025年12月〜2027年3月',
             fontproperties=fp, fontsize=13, fontweight='bold', pad=14)

fig_tl.tight_layout()
fig_tl.savefig('/home/user/AK/proposal_timeline_v2.png', dpi=150, bbox_inches='tight')
plt.close(fig_tl)
print("タイムライン図 完了")

# =========================================================================
# ② Word 提案書
# =========================================================================
doc = Document()
section = doc.sections[0]
section.page_width  = Cm(21);  section.page_height = Cm(29.7)
section.top_margin  = Cm(2.0); section.bottom_margin = Cm(2.0)
section.left_margin = Cm(2.5); section.right_margin  = Cm(2.5)

def set_font(run, size, bold=False, color=None):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.name = 'メイリオ'
    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'メイリオ')
    if color:
        run.font.color.rgb = RGBColor(*color)

def add_heading(doc, text, level=1):
    colors = {1:(30,58,95), 2:(37,99,235), 3:(22,163,74), 4:(180,50,20)}
    sizes  = {1:15, 2:12, 3:10.5, 4:10}
    prefixes = {1:'■ ', 2:'▶ ', 3:'◆ ', 4:'● '}
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10 if level==1 else 6)
    p.paragraph_format.space_after  = Pt(3)
    run = p.add_run(prefixes[level] + text)
    set_font(run, sizes[level], bold=True, color=colors[level])
    return p

def add_bullet(doc, text, indent=0):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.5 + indent*0.7)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run('・' + text)
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
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if align=='center' else WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    set_font(run, size, bold=bold, color=color)

# ── 表紙 ─────────────────────────────────────────────────────
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(20)
run = p.add_run('栄養サポート計画 提案書')
set_font(run, 22, bold=True, color=(30,58,95))

p2 = doc.add_paragraph()
p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
run2 = p2.add_run('2026年6月〜2027年3月　アジア大会（愛知・9月末）を見据えた年間計画')
set_font(run2, 11, color=(71,85,105))

p3 = doc.add_paragraph()
p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
run3 = p3.add_run('作成：管理栄養士　　2026年6月')
set_font(run3, 10, color=(100,116,139))
doc.add_paragraph()

# ── 1. これまでの取り組みと本計画の位置づけ ─────────────────
add_heading(doc, '1．これまでの取り組みと本計画の位置づけ', 1)

tbl_history = doc.add_table(rows=4, cols=3)
tbl_history.style = 'Table Grid'
for j, h in enumerate(['時期', 'テーマ', '概要']):
    set_cell_bg(tbl_history.rows[0].cells[j], '475569')
    add_cell_text(tbl_history.rows[0].cells[j], h, 10, True, (255,255,255), 'center')
history_rows = [
    ('2025年12月', '食事バランスに関する講義',
     '食事調査・アンケート結果のフィードバック。PFCバランス・食品群の摂り方を指導。'),
    ('2026年4月', 'コンディションと食事の関連を自分で記録しよう',
     '日々のコンディション（体重・疲労・睡眠・練習負荷）と食事内容を記録する習慣づくりを指導。'),
    ('2026年6月〜\n2027年3月', '本計画（今後）',
     'アジア大会（9月末・愛知）を主要ターゲットとし、試合期対策・記録分析・次シーズン準備を実施。'),
]
for i, (t, th, c) in enumerate(history_rows, 1):
    bg = 'FFFFFF' if i < 3 else 'EFF6FF'
    for j in range(3): set_cell_bg(tbl_history.rows[i].cells[j], bg)
    add_cell_text(tbl_history.rows[i].cells[0], t,  9, i==3)
    add_cell_text(tbl_history.rows[i].cells[1], th, 9, True)
    add_cell_text(tbl_history.rows[i].cells[2], c,  9)
doc.add_paragraph()

# ── 2. 現状と課題 ─────────────────────────────────────────────
add_heading(doc, '2．食事調査・アンケートから見える競技団体全体の課題', 1)

challenges = [
    ('課題①', 'エネルギー・炭水化物・微量栄養素の摂取不足',
     [
       '炭水化物：男性平均5.2 g/kg BW・女性平均4.6 g/kg BW（競技者推奨6〜10 g/kg BWに対し不足）',
       'カルシウム：男性平均約610 mg（推奨800 mg）、女性約589 mg（推奨650 mg）',
       'ビタミンD：全グループが食事摂取基準2025年版目安量（12.0 µg）を下回る',
       '食物繊維：多くのグループで目安量（男21 g・女18 g）に未達',
     ]),
    ('課題②', 'ウエイトコントロールの知識・スキル不足',
     [
       'アンケートで「ウエイトコントロール」への関心が高く、増量・減量に課題を抱える選手が多い',
       '急速減量のリスク（筋量低下・免疫低下・疲労骨折）の理解が不足している可能性',
     ]),
    ('課題③', '試合期・遠征時の食事管理スキルの不足',
     [
       'アンケートで「試合期の栄養補給」「合宿・大会帯同・補食提供」へのニーズが最上位',
       '海外遠征（インド大会）で大幅な体重減少を来した選手の実例あり（脱水・エネルギー不足）',
       '国内大会（愛知・アジア大会）においても、会場周辺の食環境を事前に把握した準備が必要',
     ]),
    ('課題④', 'コンディション記録の活用方法が不明確',
     [
       '2026年4月講義でコンディション×食事の記録を開始しているが、データの見方・活かし方の指導が未実施',
       '選手自身がデータを解釈して食事を調整できるようになることが長期的な自立につながる',
     ]),
    ('課題⑤', 'サプリメントの適正使用',
     [
       '9割以上がサプリメントを使用。情報源が指導者・チームメイト・SNSに偏る',
       'アンチドーピングの観点から認証製品・適切な使用法の知識が必要',
     ]),
]
for num, title, bullets in challenges:
    add_heading(doc, f'{num}　{title}', 2)
    for b in bullets:
        add_bullet(doc, b)

doc.add_paragraph()

# ── 3. 年間計画 ──────────────────────────────────────────────
add_heading(doc, '3．年間栄養サポート計画（2026年6月〜2027年3月）', 1)
add_body(doc, '🏆 アジア大会（愛知・2026年9月末）を主要ターゲットとして、準備期〜大会〜回復・次シーズン準備の流れで構成します。')

plan_data = [
    # (時期, 方法, テーマ, 内容詳細, 対応課題)
    (
        '2026年\n6月\n（強化研修会\n・合宿）',
        '★ 直接指導',
        'コンディション記録の\n振り返り＋アジア大会\n栄養戦略講義',
        '① 4月以降のコンディション×食事記録のフィードバック・分析方法の解説（後述4章参照）\n'
        '② アジア大会（9月末）に向けた月別栄養強化計画の提示\n'
        '③ 試合期の栄養基礎：カーボローディング・試合前後の食事\n'
        '④ 夏季・高温環境下の水分・電解質管理\n'
        '⑤ 体重管理・コンディション調整の個人目標設定',
        '課題③④'
    ),
    (
        '2026年\n7月',
        'PDF送付',
        'アジア大会8週前〜\n直前の食事計画',
        '① 大会8週前〜直前の週別カウントダウン食事計画テンプレート\n'
        '② 炭水化物の摂取量・タイミング調整ガイド\n'
        '③ コンビニ・外食を使った試合期メニューの選び方\n'
        '④ 腸内環境の整え方（食物繊維・発酵食品）',
        '課題①③'
    ),
    (
        '2026年\n8月',
        'PDF送付',
        '試合直前・大会期間中\n食事プロトコル＋\n食環境整備',
        '① 試合当日の食事タイムライン（試合前・試合間・試合後）\n'
        '② 補食リスト・推奨携行食品（場内・アクセス可能なコンビニ情報）\n'
        '③ 愛知会場周辺の食環境マップ（近隣スーパー・コンビニ・飲食店情報）\n'
        '④ 水分・電解質補給計画（体重測定による脱水チェック法）\n'
        '⑤ 試合前夜〜当朝の食事チェックリスト',
        '課題③'
    ),
    (
        '2026年\n9月末\n🏆アジア大会',
        '食環境整備\n（帯同可能な\n場合は対応）',
        '大会期間中の\n食サポート',
        '① 事前配布資料（補食・水分計画シート）の活用確認\n'
        '② 体重・コンディション記録の継続（大会期間中も記録）\n'
        '③ 緊急相談窓口の設置（LINEまたはメール）\n'
        '④ 可能であれば現地帯同または現地情報の随時提供',
        '課題③'
    ),
    (
        '2026年\n10月',
        'PDF送付',
        '大会後の回復栄養＋\nコンディション記録\n中間分析',
        '① 大会後の疲労・炎症回復のための食事（抗酸化栄養素・良質たんぱく質）\n'
        '② 4月〜9月のコンディション×食事記録の中間集計・個人フィードバック\n'
        '③ オフシーズン移行期の食事の考え方（エネルギー量の見直し）\n'
        '④ 免疫低下しやすい大会後〜移行期の注意点',
        '課題①④'
    ),
    (
        '2026年\n11月',
        'PDF送付',
        'オフシーズンの\n体組成管理',
        '① オフシーズンの増量・体組成管理の戦略（筋量↑・体脂肪↓）\n'
        '② 冬季の免疫栄養（ビタミンD・C・亜鉛の食事での補い方）\n'
        '③ 骨強化のためのカルシウム・ビタミンD摂取ガイド\n'
        '④ ウエイトコントロール個人計画テンプレートの提供',
        '課題①②'
    ),
    (
        '2026年\n12月\n（強化研修会\n・合宿）',
        '★ 直接指導',
        'コンディション記録\nデータ活用講義＋\n個人栄養評価',
        '① 4月〜12月のコンディション×食事記録の分析結果を全体フィードバック\n'
        '② データの読み方・パターン発見の方法（疲労・体重・食事の相関）\n'
        '③ 個人別の食事課題の特定とアクションプラン立案\n'
        '④ サプリメント使用状況の見直し（アンチドーピング対応確認）\n'
        '⑤ 次シーズンに向けた栄養目標の設定',
        '課題④⑤'
    ),
    (
        '2027年\n1〜2月\n（強化研修会\n・合宿）',
        '★ 直接指導',
        '次シーズン個人\n栄養計画立案\nワーク',
        '① 個人データ（記録・食事調査・体組成）を用いた個別栄養計画立案\n'
        '② 試合期・オフ期・強化期の食事切り替えロードマップの作成\n'
        '③ 自炊スキルアップ実践ワーク（計量・献立作成）\n'
        '④ 次シーズンの主要大会に向けた食事目標の設定',
        '課題①②⑤'
    ),
    (
        '2027年\n3月',
        'PDF送付',
        '新シーズン開幕\n準備ガイド',
        '① シーズンイン時の食事チェックリスト\n'
        '② 春季大会に向けた短期コンディション調整ガイド\n'
        '③ 年間栄養サポートの振り返りレポートと次年度提案書（別途）',
        '全課題'
    ),
]

# テーブル描画
tbl = doc.add_table(rows=len(plan_data)+1, cols=5)
tbl.style = 'Table Grid'
tbl.alignment = WD_TABLE_ALIGNMENT.CENTER

col_widths = [Cm(2.0), Cm(2.4), Cm(3.2), Cm(7.8), Cm(1.4)]
for row in tbl.rows:
    for j, w in enumerate(col_widths):
        row.cells[j].width = w

for j, h in enumerate(['時期', '実施方法', 'テーマ', '内容', '対応\n課題']):
    set_cell_bg(tbl.rows[0].cells[j], '1E3A5F')
    add_cell_text(tbl.rows[0].cells[j], h, 9, True, (255,255,255), 'center')

for i, (jiki, method, theme, content, kadai) in enumerate(plan_data, 1):
    is_direct = '★' in method
    is_event  = 'アジア大会' in jiki
    if is_event:
        bg = 'FFF1F2'
    elif is_direct:
        bg = 'FFF7ED'
    else:
        bg = 'FFFFFF' if i % 2 == 1 else 'F0FDF4'
    cells = tbl.rows[i].cells
    for j in range(5): set_cell_bg(cells[j], bg)
    col_m = (180,50,20) if is_direct else ((180,0,30) if is_event else (22,101,52))
    add_cell_text(cells[0], jiki,    9,  is_direct or is_event, align='center')
    add_cell_text(cells[1], method,  9,  is_direct or is_event, col_m)
    add_cell_text(cells[2], theme,   9,  True)
    add_cell_text(cells[3], content, 8.5)
    add_cell_text(cells[4], kadai,   8.5, align='center')

p_note = doc.add_paragraph()
run_n = p_note.add_run(
    '※ 橙色行：直接指導　緑色行：PDF送付　赤色行：大会期間中\n'
    '※ 直接指導の開催日程は確定次第調整。PDF送付は月1回を基本とします。')
set_font(run_n, 8.5, color=(100,116,139))

doc.add_paragraph()

# ── 4. コンディション記録の分析アドバイス ────────────────────
add_heading(doc, '4．コンディション×食事記録の分析アドバイス', 1)
add_body(doc,
    '2026年4月の講義で開始したコンディション×食事記録を「見るだけ」で終わらせず、'
    '選手自身が食事調整に活かせるよう、以下の分析手順を提案します。')

add_heading(doc, 'STEP 1　記録すべき項目の確認', 2)
rec_items = [
    '体重（起床後・排尿後）：毎朝測定→3〜7日の移動平均で傾向を把握',
    '主観的疲労度（0〜10点）：前日の練習後と当朝に記録',
    '睡眠時間・睡眠の質（0〜5点）：起床時に記録',
    '練習負荷（RPE×時間[分]＝トレーニング負荷スコア）：練習直後に記録',
    '主食の量（ご飯・パン・麺を「茶碗何杯分」で換算）：炭水化物摂取の目安',
    '水分摂取量（mL）：目標は練習日2,500 mL以上',
    '補食・サプリメントの摂取内容とタイミング',
]
for it in rec_items:
    add_bullet(doc, it)

add_heading(doc, 'STEP 2　週単位での簡易分析（セルフチェック）', 2)
analysis_items = [
    '体重変動と食事量の照合：「体重が2日以上連続して下がっている＝エネルギー不足のサイン」→主食を1品追加',
    '疲労度と前日の炭水化物摂取の照合：「高疲労の翌日に主食が少なかった」→練習前後の炭水化物補給を優先',
    '練習負荷スコアと体重の関係：高負荷の翌日は体重が0.5〜1.0 kg低下しやすい（脱水＋グリコーゲン消耗）→練習後の回復食・水分補給を強化',
    '睡眠の質と夕食タイミング：「就寝2時間前以降の食事が多い日ほど睡眠の質が低い」傾向がある選手は夕食時刻を前倒しに調整',
]
for it in analysis_items:
    add_bullet(doc, it)

add_heading(doc, 'STEP 3　月単位での傾向把握（グラフ化）', 2)
add_body(doc, '以下の2つのグラフをExcelまたはスマートフォンのアプリ（Excelスプレッドシート等）で作成することを推奨します。')
graph_items = [
    '【グラフ①】体重（折れ線）＋疲労度（棒グラフ）を同じ軸に重ね書き\n'
    '　→体重低下と高疲労が重なるタイミングを視覚化し、エネルギー不足の時期を特定',
    '【グラフ②】週ごとの平均「主食量（茶碗換算）」と「練習負荷スコア」の棒グラフ\n'
    '　→高負荷週に炭水化物が追いついているか確認。不足していれば翌週の食事を修正',
]
for it in graph_items:
    add_bullet(doc, it)

add_heading(doc, 'STEP 4　専門家（管理栄養士）との共有ポイント', 2)
share_items = [
    '月1回・LINEまたはメールで「体重推移グラフ」「高疲労が連続した週の食事内容」を送付→個別フィードバックを返す',
    '強化合宿・研修会の際に記録データを持参し、直接分析ワークを実施',
    '「体重が増えない」「疲れが抜けない」「試合前の調整がうまくいかない」など具体的な悩みを記録とともに相談する',
]
for it in share_items:
    add_bullet(doc, it)

# ツール推奨ボックス
doc.add_paragraph()
add_heading(doc, '推奨ツール・アプリ', 3)
tools = [
    ('記録ツール', 'Excelスプレッドシート（Google Sheets）・手帳・専用アプリ（あすけん、MyFitnessPalなど）'),
    ('グラフ作成', 'Google スプレッドシートの折れ線・棒グラフ機能（選手向けテンプレートを別途配布予定）'),
    ('共有方法',   'LINEで管理栄養士へ月1回スクリーンショット送付'),
]
for k, v in tools:
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.5)
    p.paragraph_format.space_after = Pt(2)
    run1 = p.add_run(f'【{k}】')
    set_font(run1, 10, bold=True, color=(37,99,235))
    run2 = p.add_run(f'　{v}')
    set_font(run2, 10)

doc.add_paragraph()

# ── 5. アジア大会 食環境整備の具体策 ────────────────────────
add_heading(doc, '5．アジア大会（愛知・2026年9月末）食環境整備の具体策', 1)

add_heading(doc, '事前準備（〜8月）', 2)
pre_items = [
    '会場（ポートメッセなごや等、会場確定後）周辺のコンビニ・スーパー・飲食店マップを作成しPDF配布',
    '選手向け「大会期間中の補食リスト」作成（持参推奨食品：おにぎり・バナナ・カステラ・ゼリー飲料・スポーツドリンク等）',
    '試合スケジュール別の食事タイムライン例（1日1試合・複数試合・勝ち上がり想定別）を作成',
    'アレルギー・宗教上の食事制限がある選手への個別対応リストの確認（指導者と連携）',
]
for it in pre_items:
    add_bullet(doc, it)

add_heading(doc, '大会期間中（直接帯同または遠隔サポート）', 2)
during_items = [
    '【帯同可能な場合】試合間の補食提供・水分補給確認・コンディション記録のサポート',
    '【遠隔の場合】LINEグループで随時相談受付・体重チェック促し・翌日の食事アドバイス送信',
    '体重測定ルールの徹底：毎朝起床後に測定・前日比−1 kg超で積極的水分補給',
    '試合後の回復食提供または調達ガイド：「たんぱく質20〜30 g＋炭水化物60 g以上」を30〜60分以内に摂取',
]
for it in during_items:
    add_bullet(doc, it)

doc.add_paragraph()

# ── 6. 課題別解決策まとめ ────────────────────────────────────
add_heading(doc, '6．課題別 解決策まとめ', 1)

sol_data = [
    ('課題①\n栄養素不足',
     '・炭水化物：主食量の目安（g/kg BW）を個人別に提示→6月講義＋7月PDF\n'
     '・Ca・VitD：鮭・乳製品・小魚を使ったレシピ集を11月PDFで提供\n'
     '・食物繊維：副菜の選び方ガイドを各PDF資料に1コーナーとして掲載'),
    ('課題②\n体重管理',
     '・増量・減量の月別計画テンプレートを11月PDFで提供\n'
     '・急速減量のリスクを6月講義で解説（筋量低下・疲労骨折等）\n'
     '・体重×疲労の記録グラフを用いた個人フィードバック（12月講義）'),
    ('課題③\n試合期・遠征',
     '・7〜8月のPDFで大会カウントダウン食事計画・プロトコルを提供\n'
     '・8月PDF：愛知会場周辺の食環境マップ・補食リストを配布\n'
     '・大会中は遠隔サポート（LINE）または帯同で対応'),
    ('課題④\n記録の活用',
     '・6月講義でコンディション記録の分析方法を解説（本書4章参照）\n'
     '・Excelテンプレート（体重×疲労グラフ）を6月に配布\n'
     '・12月講義で全員の記録データをフィードバック・パターン分析を実施'),
    ('課題⑤\nサプリメント',
     '・12月講義でサプリメント使用状況の見直しと適正使用の再教育\n'
     '・アンチドーピング対応認証製品リストを12月PDF（付録）として配布\n'
     '・情報源の見直しを促し、相談窓口（管理栄養士）の活用を呼びかける'),
]

tbl2 = doc.add_table(rows=len(sol_data)+1, cols=2)
tbl2.style = 'Table Grid'
tbl2.alignment = WD_TABLE_ALIGNMENT.CENTER
for j, h in enumerate(['課題', '解決策（実施時期）']):
    set_cell_bg(tbl2.rows[0].cells[j], '1E3A5F')
    add_cell_text(tbl2.rows[0].cells[j], h, 10, True, (255,255,255), 'center')
tbl2.rows[0].cells[0].width = Cm(3.2)
tbl2.rows[0].cells[1].width = Cm(13.6)
for i, (k, v) in enumerate(sol_data, 1):
    bg = 'FFFFFF' if i%2==1 else 'F0FDF4'
    for j in range(2): set_cell_bg(tbl2.rows[i].cells[j], bg)
    tbl2.rows[i].cells[0].width = Cm(3.2)
    tbl2.rows[i].cells[1].width = Cm(13.6)
    add_cell_text(tbl2.rows[i].cells[0], k, 9, True, align='center')
    add_cell_text(tbl2.rows[i].cells[1], v, 9)

doc.add_paragraph()

# ── 7. 備考 ──────────────────────────────────────────────────
add_heading(doc, '7．備考・今後の検討事項', 1)
notes = [
    '本計画の実施時期・内容は強化スケジュールの変更に応じて随時調整します。',
    '個人対応が必要な選手（体重管理・怪我・食物アレルギー等）は個別相談の場を別途設けることを推奨します。',
    '愛知会場の詳細が確定した段階で「食環境マップ」を更新し、8月PDF資料として発送します。',
    'コンディション記録のExcelテンプレートは6月の直接指導時に配布します。',
    'PDF資料はLINEグループまたはメールで選手全員に配信し、いつでも参照できるよう保管を依頼します。',
    '指導者・コーチとの情報共有（体重管理・試合スケジュール・選手のコンディション）を継続して行います。',
]
for n in notes:
    add_bullet(doc, n)

out_docx = '/home/user/AK/nutrition_support_proposal_v2.docx'
doc.save(out_docx)
print(f"提案書（Word）完了: {out_docx}")
