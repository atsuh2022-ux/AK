const pptxgen = require("pptxgenjs");

const NAVY = "21295C";
const DEEPBLUE = "065A82";
const TEAL = "1C7293";
const WHITE = "FFFFFF";
const INK = "1A1A1A";
const MUTED = "5C6570";
const CARDBG = "F4F7F9";

const C_SOLID = "2A78D6";
const C_SMOOTHIE = "EB6834";
const C_ONIGISMO = "1BAF7A";
const C_LOWSUGAR = "EDA100";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: "Cambria", bodyFontFace: "Calibri" };
const W = 13.33, H = 7.5, MARGIN = 0.6;

function addFooter(slide, note, dark) {
  slide.addText(note, { x: MARGIN, y: H - 0.4, w: W - MARGIN * 2, h: 0.28, fontFace: "Calibri", fontSize: 9.5, color: dark ? "9AA6C4" : MUTED, align: "left" });
}
function titleBlock(slide, kicker, title, dark) {
  slide.addText(kicker, { x: MARGIN, y: 0.42, w: W - MARGIN * 2, h: 0.34, fontFace: "Calibri", fontSize: 12.5, bold: true, color: dark ? "8FB7E0" : TEAL, charSpacing: 1, isTextBox: true });
  slide.addText(title, { x: MARGIN, y: 0.74, w: W - MARGIN * 2, h: 0.6, fontFace: "Cambria", fontSize: 26, bold: true, color: dark ? WHITE : NAVY, isTextBox: true });
}

// ================= 1: Title =================
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addShape("rect", { x: 0, y: 0, w: W, h: H, fill: { color: NAVY } });
  s.addShape("oval", { x: 10.6, y: -1.6, w: 5.5, h: 5.5, fill: { color: DEEPBLUE, transparency: 55 }, line: { type: "none" } });
  s.addShape("oval", { x: -2.0, y: 4.6, w: 4.6, h: 4.6, fill: { color: TEAL, transparency: 60 }, line: { type: "none" } });

  s.addText("パイロット結果を踏まえた", { x: MARGIN, y: 2.0, w: 11, h: 0.4, fontFace: "Calibri", fontSize: 15, bold: true, color: "8FB7E0", charSpacing: 1, isTextBox: true });
  s.addText("今後の研究計画", { x: MARGIN, y: 2.45, w: 11.5, h: 1.0, fontFace: "Cambria", fontSize: 40, bold: true, color: WHITE, isTextBox: true });
  s.addText("新たな課題の整理と、練習量を揃えた再検証プラン", { x: MARGIN, y: 3.45, w: 11, h: 0.5, fontFace: "Calibri", fontSize: 16, color: "CADCFC", isTextBox: true });

  const items = ["新たな課題（6項目）", "再検証プラン A〜D", "生理指標の測定方法（血圧 vs 心拍数）", "優先順位のまとめ"];
  let y = 4.5;
  items.forEach(it => {
    s.addShape("oval", { x: MARGIN, y: y + 0.06, w: 0.1, h: 0.1, fill: { color: TEAL }, line: { type: "none" } });
    s.addText(it, { x: MARGIN + 0.3, y, w: 9, h: 0.4, fontFace: "Calibri", fontSize: 14, color: "E8EDF7", isTextBox: true, margin: 0 });
    y += 0.55;
  });
  s.addText("対象：高位脊髄損傷（SCI）車いす陸上選手 1名を対象としたパイロット研究の結果から", {
    x: MARGIN, y: 6.85, w: 10.5, h: 0.35, fontFace: "Calibri", fontSize: 10.5, italic: true, color: "9AA6C4", isTextBox: true
  });
}

function challengeItem(s, y, num, title, desc, color) {
  s.addShape("oval", { x: MARGIN, y, w: 0.42, h: 0.42, fill: { color }, line: { type: "none" } });
  s.addText(num, { x: MARGIN, y, w: 0.42, h: 0.42, align: "center", valign: "middle", fontFace: "Cambria", fontSize: 13, bold: true, color: WHITE, isTextBox: true, margin: 0 });
  s.addText(title, { x: MARGIN + 0.6, y: y - 0.02, w: 11.3, h: 0.32, fontFace: "Calibri", fontSize: 13.5, bold: true, color: NAVY, isTextBox: true, margin: 0 });
  s.addText(desc, { x: MARGIN + 0.6, y: y + 0.29, w: 11.3, h: 0.5, fontFace: "Calibri", fontSize: 11, color: MUTED, isTextBox: true, margin: 0 });
}

// ================= 2: 新たな課題① =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "NEW QUESTIONS", "新たな課題①（Q1・Q2から）", false);

  const items = [
    { t: "摂取直前（8:00）血糖値のばらつき", d: "条件間で60〜70 mg/dL異なる原因が未解明。前日の運動量・睡眠・センサー校正等の切り分けが必要。", c: C_SOLID },
    { t: "血圧を一度も直接測定していない", d: "「食後低血圧」という核心仮説を、頭痛の有無という間接指標だけで判断してきた。", c: C_SMOOTHIE },
    { t: "スムージーの一過性スパイクの意味", d: "45分でピーク→90分でベースライン付近に戻る挙動が、より短いリードタイムでの摂取でも同じ影響を持つかは未検証。", c: C_SMOOTHIE },
    { t: "タイミングの中間点・他レシピでの再現性", d: "「同時」と「2.5〜3時間ずらし」の2点しか比較しておらず、間の用量反応関係や別の食材構成での再現性が未確認。", c: C_ONIGISMO },
  ];
  let y = 1.9;
  items.forEach((it, i) => { challengeItem(s, y, String(i + 1), it.t, it.d, it.c); y += 1.15; });
}

// ================= 3: 新たな課題② =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "NEW QUESTIONS", "新たな課題②（Q3・横断的な課題）", false);

  const items = [
    { t: "血糖は良好なのに持久力の体感は最低という矛盾（最重要）", d: "糖質減条件で血糖・燃料供給・睡眠は良好だが、持久力・爆発力の自己評価が4条件中最低。未解決の中心課題。", c: C_LOWSUGAR },
    { t: "「糖質減」の正確なレシピ量が未記録", d: "何gの糖質をカットしたかが記録に残っておらず、再現性がない。", c: C_LOWSUGAR },
    { t: "単一選手・低n・順序固定・対照群なし", d: "各条件n=3日で統計的検定ができず、条件順序も固定（ランダム化なし）。健常選手の対照群もなく、SCI特有の反応か一般的な反応かを区別できない。", c: MUTED },
  ];
  let y = 2.0;
  items.forEach((it, i) => { challengeItem(s, y, String(i + 1), it.t, it.d, it.c); y += 1.3; });
  addFooter(s, "これらの課題に対応する具体策を次ページ以降にまとめる。", false);
}

function planCard(s, x, y, w, h, tag, title, purpose, design, effect, color) {
  s.addShape("roundRect", { x, y, w, h, rectRadius: 0.1, fill: { color: CARDBG }, line: { type: "none" } });
  s.addShape("roundRect", { x: x + 0.25, y: y + 0.2, w: 0.55, h: 0.3, rectRadius: 0.06, fill: { color }, line: { type: "none" } });
  s.addText(tag, { x: x + 0.25, y: y + 0.2, w: 0.55, h: 0.3, align: "center", valign: "middle", fontFace: "Cambria", fontSize: 12, bold: true, color: WHITE, isTextBox: true, margin: 0 });
  s.addText(title, { x: x + 0.9, y: y + 0.17, w: w - 1.15, h: 0.4, valign: "middle", fontFace: "Calibri", fontSize: 14, bold: true, color: NAVY, isTextBox: true, margin: 0 });

  let ty = y + 0.65;
  const rows = [["目的", purpose], ["デザイン", design], ["効果", effect]];
  rows.forEach(([label, text]) => {
    s.addText(label, { x: x + 0.25, y: ty, w: 1.0, h: 0.24, fontFace: "Calibri", fontSize: 10, bold: true, color: color, isTextBox: true, margin: 0 });
    s.addText(text, { x: x + 0.25, y: ty + 0.22, w: w - 0.5, h: 0.62, fontFace: "Calibri", fontSize: 10, color: INK, isTextBox: true, margin: 0 });
    ty += 0.86;
  });
}

// ================= 4: プランA・B =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "RE-VERIFICATION PLAN", "再検証プラン A・B", false);
  s.addText("最優先：練習量の交絡を取り除く2つの一手", { x: MARGIN, y: 1.55, w: W - MARGIN * 2, h: 0.35, fontFace: "Calibri", fontSize: 13, color: MUTED, isTextBox: true, margin: 0 });

  const colW = (W - MARGIN * 2 - 0.4) / 2;
  planCard(s, MARGIN, 2.0, colW, 4.6, "A", "固定トレーニングメニュー法",
    "これまで最大の交絡だった「60〜180分のばらつき」を排除する。",
    "全条件・全日で同一メニュー（例：ウォームアップ15分＋メインセット60分＋クールダウン15分）を実施。",
    "RPE・持久力・爆発力・運動後疲労を、練習量の影響を受けずに食事の効果として評価できる。最も費用対効果が高い一手。",
    DEEPBLUE);
  planCard(s, MARGIN + colW + 0.4, 2.0, colW, 4.6, "B", "客観的パフォーマンステストの追加",
    "自己評価だけに頼らず、Q3で見つかった「血糖は良いのに体感は悪い」矛盾の真偽を客観データで確認する。",
    "毎回の練習内に、同一コース・同一距離のタイムトライアル（例：直線200m×3本）やパワーメーター・心拍数記録を固定タイミングで挿入。",
    "体感の悪化が実際のパフォーマンス低下を伴うのか、主観的なズレなのかを切り分けられる。",
    TEAL);
}

// ================= 5: プランC・D =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "RE-VERIFICATION PLAN", "再検証プラン C・D", false);
  s.addText("研究デザインの妥当性を高める2つの拡張", { x: MARGIN, y: 1.55, w: W - MARGIN * 2, h: 0.35, fontFace: "Calibri", fontSize: 13, color: MUTED, isTextBox: true, margin: 0 });

  const colW = (W - MARGIN * 2 - 0.4) / 2;
  planCard(s, MARGIN, 2.0, colW, 4.6, "C", "ランダム化クロスオーバーデザイン",
    "条件の順序効果（トレーニング適応・季節・モチベーションの変化）を排除する。",
    "4条件を週1回ずつ、複数週にわたりランダムな順序で実施（例：4条件×4週）。条件間に最低1日のウォッシュアウト日を設ける。",
    "プランA・Bと組み合わせれば「いつ測っても同じ結果か」を検証でき、固定順序だった点への批判に答えられる。",
    C_ONIGISMO);
  planCard(s, MARGIN + colW + 0.4, 2.0, colW, 4.6, "D", "糖質量の段階的検証（用量反応）",
    "Q3の矛盾を解消するため、「通常」と「今回の糖質減」の2点だけでなく間の段階も見る。",
    "通常量を基準に−10%／−20%／−30%の3段階（レシピの糖質グラム数を明記し再現性を確保）を、A・Bと同じ固定メニューで比較。",
    "血糖の安定性とパフォーマンスの両方が両立する「最適点」を特定できる可能性がある。",
    C_LOWSUGAR);
}

// ================= 6: 生理指標の測定方法（血圧 vs 心拍数） =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "PHYSIOLOGICAL MEASURES", "生理指標の測定方法：血圧 vs 心拍数", false);

  s.addShape("roundRect", { x: MARGIN, y: 1.65, w: W - MARGIN * 2, h: 1.55, rectRadius: 0.12, fill: { color: "FDF3E2" }, line: { color: "EDA100", width: 1 } });
  s.addText("⚠ 心拍数だけでは血圧の代わりになりにくい", { x: MARGIN + 0.3, y: 1.8, w: W - MARGIN * 2 - 0.6, h: 0.3, fontFace: "Calibri", fontSize: 13, bold: true, color: "6B4B00", isTextBox: true, margin: 0 });
  s.addText(
    "健常者なら血圧低下時に心拍数が代償的に上がるが、この代償反応自体が高位SCIで遮断される交感神経の機能。心拍数が上がらないのが「血圧が下がっていない」からか「代償反応が壊れて見えていないだけ」かを、心拍数だけでは区別できない。",
    { x: MARGIN + 0.3, y: 2.14, w: W - MARGIN * 2 - 0.6, h: 1.0, fontFace: "Calibri", fontSize: 12, color: "6B4B00", isTextBox: true, margin: 0 }
  );

  const colW = (W - MARGIN * 2 - 0.4) / 2;
  function infoCard(x, title, lines, color) {
    s.addShape("roundRect", { x, y: 3.45, w: colW, h: 2.55, rectRadius: 0.1, fill: { color: CARDBG }, line: { type: "none" } });
    s.addShape("rect", { x: x + 0.3, y: 3.62, w: 0.16, h: 0.4, fill: { color }, line: { type: "none" } });
    s.addText(title, { x: x + 0.58, y: 3.58, w: colW - 0.9, h: 0.5, fontFace: "Calibri", fontSize: 14, bold: true, color: NAVY, isTextBox: true, margin: 0, valign: "middle" });
    let ly = 4.18;
    lines.forEach(l => {
      s.addText("•  " + l, { x: x + 0.3, y: ly, w: colW - 0.6, h: 0.42, fontFace: "Calibri", fontSize: 10.5, color: INK, isTextBox: true, margin: 0 });
      ly += 0.46;
    });
  }
  infoCard(MARGIN, "心拍数だけでも価値はある", [
    "元の研究計画書でも「自律神経の変動・運動強度」の指標として明記",
    "心拍変動（HRV）まで見れば交感・副交感バランスの変化を捉えられる",
    "ウェアラブルで連続測定が容易",
    "練習強度が揃っているかの確認（プランA・Bの補強）に直接役立つ",
  ], TEAL);
  infoCard(MARGIN + colW + 0.4, "現実的な折衷案", [
    "血圧は数点だけスポット測定（8:00・8:30・9:30・練習直前）",
    "心拍数はウェアラブルで連続測定し、間を補完",
    "連続血圧測定（高価・運動中は困難）を避けつつ実測値で裏付けられる",
    "大きな負担なく、核心仮説に直接答えられる設計になる",
  ], C_ONIGISMO);

  addFooter(s, "心拍数は血圧の代用ではなく補完指標として位置づけ、血圧のスポット測定と組み合わせるのが現実的。", false);
}

// ================= 7: 優先順位・まとめ =================
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  titleBlock(s, "PRIORITY", "優先順位のまとめ", true);

  const rows = [
    ["1", "プランA：固定トレーニングメニュー法", "最優先。労力に対して得られる情報量が最大", DEEPBLUE],
    ["2", "プランB：客観的パフォーマンステストの追加", "Aとセットで、Q3の矛盾にかなり近づける", TEAL],
    ["3", "血圧スポット測定＋心拍数の連続測定", "核心仮説（食後低血圧）に直接答えられる", C_ONIGISMO],
    ["4", "プランC：ランダム化クロスオーバー", "余力があれば。順序効果を排除し妥当性を高める", C_LOWSUGAR],
    ["5", "プランD：糖質量の段階的検証", "血糖とパフォーマンスの最適点を探る発展形", "8B6FB0"],
  ];
  let y = 1.75;
  rows.forEach(([num, title, note, color]) => {
    s.addShape("oval", { x: MARGIN, y, w: 0.42, h: 0.42, fill: { color }, line: { type: "none" } });
    s.addText(num, { x: MARGIN, y, w: 0.42, h: 0.42, align: "center", valign: "middle", fontFace: "Cambria", fontSize: 14, bold: true, color: WHITE, isTextBox: true, margin: 0 });
    s.addText(title, { x: MARGIN + 0.65, y: y - 0.02, w: 6.6, h: 0.5, valign: "middle", fontFace: "Calibri", fontSize: 13.5, bold: true, color: WHITE, isTextBox: true, margin: 0 });
    s.addText(note, { x: MARGIN + 7.4, y: y - 0.02, w: 4.9, h: 0.5, valign: "middle", fontFace: "Calibri", fontSize: 11.5, color: "CADCFC", isTextBox: true, margin: 0 });
    y += 0.68;
  });

  s.addShape("roundRect", { x: MARGIN, y: 5.55, w: W - MARGIN * 2, h: 1.3, rectRadius: 0.1, fill: { color: "1A2350" }, line: { type: "none" } });
  s.addText("まず①②（練習量・パフォーマンス測定の標準化）だけでも実施できれば、今回パイロットで残った最大の疑問「糖質減は本当に持久力を下げるのか」にかなり近づける。余力に応じて③以降を積み増す段階的なアプローチを推奨。", {
    x: MARGIN + 0.3, y: 5.7, w: W - MARGIN * 2 - 0.6, h: 1.0, valign: "middle", fontFace: "Calibri", fontSize: 12.5, color: "E8EDF7", isTextBox: true, margin: 0
  });
  addFooter(s, "データ出典：これまでのパイロット分析（for_AI_.xlsx／0824スケジュール.xlsx／condition_app_2026-08-25_2026-09-07.xlsx）", true);
}

pres.writeFile({ fileName: "output_future_plan.pptx" }).then(() => console.log("done"));
