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
  slide.addText(title, { x: MARGIN, y: 0.74, w: W - MARGIN * 2, h: 0.6, fontFace: "Cambria", fontSize: 25, bold: true, color: dark ? WHITE : NAVY, isTextBox: true });
}

// ================= Title =================
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addShape("rect", { x: 0, y: 0, w: W, h: H, fill: { color: NAVY } });
  s.addShape("oval", { x: 10.6, y: -1.6, w: 5.5, h: 5.5, fill: { color: DEEPBLUE, transparency: 55 }, line: { type: "none" } });
  s.addText("血糖値 × 自覚コンディション × 毎日のコンディション", {
    x: MARGIN, y: 2.4, w: 11.8, h: 0.5, fontFace: "Calibri", fontSize: 16, bold: true, color: "8FB7E0", charSpacing: 1, isTextBox: true
  });
  s.addText("3つの比較の複合評価", {
    x: MARGIN, y: 2.9, w: 11.8, h: 1.0, fontFace: "Cambria", fontSize: 36, bold: true, color: WHITE, isTextBox: true
  });
  s.addText("①スムージー vs 固形　／　②スムージー vs おにぎり＋スムージー　／　③おにぎり＋スムージー vs おにぎり＋糖質減", {
    x: MARGIN, y: 3.85, w: 11.8, h: 0.5, fontFace: "Calibri", fontSize: 14, color: "CADCFC", isTextBox: true
  });
  s.addText("各比較を「血糖値」「自覚コンディション（食後アンケート）」「毎日のコンディション（アプリ記録）」の3軸で評価", {
    x: MARGIN, y: 4.5, w: 10.5, h: 0.4, fontFace: "Calibri", fontSize: 12, italic: true, color: "9AA6C4", isTextBox: true
  });
}

function legendChip(s, x, y, color, label) {
  s.addShape("rect", { x, y: y + 0.03, w: 0.16, h: 0.16, fill: { color }, line: { type: "none" } });
  s.addText(label, { x: x + 0.22, y: y - 0.04, w: 3.0, h: 0.3, fontFace: "Calibri", fontSize: 11.5, bold: true, color: INK, isTextBox: true, margin: 0 });
}

// metric trio: 3 mini comparison cards in a row
function metricRow(s, y, metrics, colorA, colorB) {
  const gap = 0.3;
  const cardW = (W - MARGIN * 2 - gap * (metrics.length - 1)) / metrics.length;
  metrics.forEach((m, i) => {
    const x = MARGIN + i * (cardW + gap);
    s.addShape("roundRect", { x, y, w: cardW, h: 0.95, rectRadius: 0.08, fill: { color: CARDBG }, line: { type: "none" } });
    s.addText(m.label, { x: x + 0.15, y: y + 0.06, w: cardW - 0.3, h: 0.26, fontFace: "Calibri", fontSize: 10.5, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    const halfW = (cardW - 0.3) / 2;
    s.addText(m.valA, { x: x + 0.15, y: y + 0.34, w: halfW, h: 0.5, fontFace: "Cambria", fontSize: 19, bold: true, color: colorA, isTextBox: true, margin: 0 });
    s.addText(m.valB, { x: x + 0.15 + halfW, y: y + 0.34, w: halfW, h: 0.5, fontFace: "Cambria", fontSize: 19, bold: true, color: colorB, isTextBox: true, margin: 0, align: "right" });
    if (m.note) {
      s.addText(m.note, { x: x + 0.15, y: y + 0.72, w: cardW - 0.3, h: 0.2, fontFace: "Calibri", fontSize: 8.5, color: MUTED, isTextBox: true, margin: 0 });
    }
  });
}

function sectionLabel(s, y, text, color) {
  s.addShape("rect", { x: MARGIN, y: y + 0.03, w: 0.1, h: 0.16, fill: { color }, line: { type: "none" } });
  s.addText(text, { x: MARGIN + 0.2, y: y - 0.04, w: 6, h: 0.3, fontFace: "Calibri", fontSize: 12.5, bold: true, color: NAVY, isTextBox: true, margin: 0 });
}

function comparisonSlide(opts) {
  const { kicker, title, nameA, nameB, colorA, colorB, glucose, condition, nightly, nightlyNote, verdict } = opts;
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, kicker, title, false);

  legendChip(s, MARGIN, 1.5, colorA, nameA);
  legendChip(s, MARGIN + 4.2, 1.5, colorB, nameB);

  // --- 血糖値 ---
  sectionLabel(s, 1.85, "血糖値", DEEPBLUE);
  metricRow(s, 2.13, glucose, colorA, colorB);

  // --- 自覚コンディション ---
  sectionLabel(s, 3.25, "自覚コンディション（食後アンケート）", TEAL);
  metricRow(s, 3.53, condition, colorA, colorB);

  // --- 毎日のコンディション ---
  sectionLabel(s, 4.65, "毎日のコンディション（夜のアプリ記録）", C_LOWSUGAR);
  const rows = [
    [{ text: "", options: { fill: { color: NAVY } } },
     { text: nameA, options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: nameB, options: { bold: true, color: WHITE, fill: { color: NAVY } } }],
    ...nightly.map((r, i) => [
      { text: r.label, options: { color: NAVY, bold: true, fill: { color: i % 2 === 0 ? CARDBG : WHITE }, fontSize: 10.5 } },
      { text: r.a, options: { color: INK, fill: { color: i % 2 === 0 ? CARDBG : WHITE }, fontSize: 10.5 } },
      { text: r.b, options: { color: INK, fill: { color: i % 2 === 0 ? CARDBG : WHITE }, fontSize: 10.5 } },
    ])
  ];
  s.addTable(rows, {
    x: MARGIN, y: 4.93, w: 7.6, h: 1.3,
    fontFace: "Calibri", fontSize: 10.5, border: { type: "solid", color: "E3E1DB", pt: 0.5 },
    autoPage: false, valign: "middle", rowH: 0.185,
    colW: [2.6, 2.5, 2.5]
  });
  if (nightlyNote) {
    s.addText(nightlyNote, { x: MARGIN + 7.9, y: 4.95, w: 4.83, h: 1.4, fontFace: "Calibri", fontSize: 10, italic: true, color: MUTED, isTextBox: true, margin: 0 });
  }

  // --- 総合評価 ---
  s.addShape("roundRect", { x: MARGIN, y: 6.4, w: W - MARGIN * 2, h: 0.95, rectRadius: 0.1, fill: { color: "EAF7F0" }, line: { type: "none" } });
  s.addText("✓ 総合評価：" + verdict, { x: MARGIN + 0.25, y: 6.46, w: W - MARGIN * 2 - 0.5, h: 0.83, fontFace: "Calibri", fontSize: 11, bold: true, color: "0F5C3D", isTextBox: true, margin: 0, valign: "middle" });
}

// ================= ① スムージー vs 固形 =================
comparisonSlide({
  kicker: "COMPARISON ①",
  title: "スムージー vs 固形",
  nameA: "スムージー摂取", nameB: "固形摂取",
  colorA: C_SMOOTHIE, colorB: C_SOLID,
  glucose: [
    { label: "Δピーク血糖値 (mg/dL)", valA: "85.0", valB: "53.7" },
    { label: "変動係数 CV", valA: "14.7%", valB: "11.2%" },
    { label: "練習中(11-14h)平均血糖", valA: "222.1", valB: "135.1", note: "mg/dL＝燃料供給の目安" },
  ],
  condition: [
    { label: "満腹感ピーク(8:30)", valA: "3.67", valB: "4.00" },
    { label: "食欲(10:00)", valA: "8.67", valB: "7.67" },
    { label: "頭痛・吐き気", valA: "1・1", valB: "1・1", note: "両条件とも症状なし" },
  ],
  nightly: [
    { label: "起床時コンディション", a: "2.33", b: "2.00" },
    { label: "睡眠の質", a: "2.00", b: "2.00" },
    { label: "RPE", a: "5.67", b: "6.67" },
    { label: "持久力", a: "3.67", b: "3.00" },
    { label: "爆発力", a: "3.67", b: "4.00" },
    { label: "運動後疲労", a: "2.67", b: "3.33" },
  ],
  nightlyNote: "⚠ 練習時間がスムージー60分/日・固形140分/日と大きく異なり、夜間指標には練習量の交絡が強く残る。数値差を食事の効果と断定できない。",
  verdict: "液状化だけでは血糖の乱高下（Δピーク・CV）が明確に悪化する。自覚的な消化器症状・満腹感には大差なく、夜間コンディションも練習量の交絡下では大きな差と言えない。「液状化の単独効果」は血糖面でむしろマイナス。"
});

// ================= ② スムージー vs おにぎり＋スムージー =================
comparisonSlide({
  kicker: "COMPARISON ②",
  title: "スムージー vs おにぎり＋スムージー",
  nameA: "スムージー摂取", nameB: "おにぎり＋スムージー",
  colorA: C_SMOOTHIE, colorB: C_ONIGISMO,
  glucose: [
    { label: "Δピーク血糖値 (mg/dL)", valA: "85.0", valB: "78.0" },
    { label: "変動係数 CV", valA: "14.7%", valB: "10.1%" },
    { label: "練習中(11-14h)平均血糖", valA: "222.1", valB: "220.1", note: "ほぼ同水準（燃料供給は同等）" },
  ],
  condition: [
    { label: "満腹感ピーク(8:30)", valA: "3.67", valB: "7.67" },
    { label: "食欲(10:00)", valA: "8.67", valB: "5.67" },
    { label: "頭痛・吐き気", valA: "1・1", valB: "1・(9:30のみ2)" },
  ],
  nightly: [
    { label: "起床時コンディション", a: "2.33", b: "2.33" },
    { label: "睡眠の質", a: "2.00", b: "2.00" },
    { label: "RPE", a: "5.67", b: "5.50" },
    { label: "持久力", a: "3.67", b: "3.83" },
    { label: "爆発力", a: "3.67", b: "3.50" },
    { label: "運動後疲労", a: "2.67", b: "3.17" },
  ],
  nightlyNote: "練習時間はスムージー60分/日・おにぎり+スムージー80分/日とやや近く、①よりは比較しやすい。起床時コンディション・睡眠の質は同水準。",
  verdict: "おにぎりを同時摂取すると、同水準の血糖燃料供給を保ったままΔピーク・CVが小さくなり、波形がなだらかになる。満腹感は上がるが消化器症状は軽微。夜間コンディションもわずかに良好な傾向で、単独液状化よりバランスが良い。"
});

// ================= ③ おにぎり＋スムージー vs おにぎり＋糖質減 =================
comparisonSlide({
  kicker: "COMPARISON ③",
  title: "おにぎり＋スムージー vs おにぎり＋糖質減",
  nameA: "おにぎり＋スムージー", nameB: "おにぎり＋糖質減",
  colorA: C_ONIGISMO, colorB: C_LOWSUGAR,
  glucose: [
    { label: "iAUC 2h (mg/dL・分)", valA: "5,230", valB: "3,168", note: "糖質減で約39%減" },
    { label: "変動係数 CV", valA: "10.1%", valB: "11.8%" },
    { label: "練習中(11-14h)平均血糖", valA: "220.1", valB: "229.4", note: "糖質減の方がむしろ高い" },
  ],
  condition: [
    { label: "満腹感ピーク(8:30)", valA: "7.67", valB: "9.00" },
    { label: "食欲(10:00)", valA: "5.67", valB: "5.33" },
    { label: "頭痛・吐き気", valA: "1・(9:30のみ2)", valB: "1・1" },
  ],
  nightly: [
    { label: "起床時コンディション", a: "2.33", b: "2.67" },
    { label: "睡眠の質", a: "2.00", b: "2.67" },
    { label: "RPE", a: "5.50", b: "6.33" },
    { label: "持久力", a: "3.83", b: "2.33" },
    { label: "爆発力", a: "3.50", b: "3.33" },
    { label: "運動後疲労", a: "3.17", b: "3.33" },
  ],
  nightlyNote: "⚠ 起床時コンディション・睡眠の質は糖質減が最高だが、持久力・爆発力は糖質減が最低。血糖の燃料供給は良好なのに体感が逆という矛盾があり、練習内容の交絡を含め要検証。",
  verdict: "糖質を減らすとiAUCが約39%減少し血糖の負荷は明確に軽い。練習中の燃料供給も犠牲になっていない。消化器症状も軽微。一方で持久力・爆発力の自己評価は最も低く、血糖データと体感の食い違いが残る最大の論点。"
});

pres.writeFile({ fileName: "output_3comparisons.pptx" }).then(() => console.log("done"));
