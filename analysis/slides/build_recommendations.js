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

const times = ["08:00","08:15","08:30","08:45","09:00","09:15","09:30","09:45","10:00","10:15","10:30","10:45","11:00","11:15","11:30","11:45","12:00","12:15","12:30","12:45","13:00","13:15","13:30","13:45","14:00"];
const glucose = {
  "固形摂取":            [99.0,112.0,133.3,129.0,113.0,105.3,108.7,108.7,106.0,120.0,130.3,125.3,120.3,135.0,152.7,143.0,139.0,129.7,119.0,131.0,143.0,136.7,138.0,140.3,129.0],
  "スムージー摂取":        [159.3,163.0,182.0,202.7,193.7,163.7,149.0,148.7,154.7,179.3,194.3,226.0,226.3,223.0,239.7,244.3,213.7,225.0,218.3,218.7,224.7,207.0,212.3,222.7,211.0],
  "おにぎり＋スムージー":    [164.3,169.3,208.7,235.0,225.7,219.3,207.3,212.3,207.0,191.3,188.0,185.0,182.7,193.0,208.0,226.3,229.0,227.3,231.3,242.3,236.7,224.7,219.3,218.7,222.3],
  "おにぎり＋糖質減":      [166.0,183.7,217.0,197.0,193.7,193.7,198.7,185.3,174.3,172.3,199.7,217.7,211.0,195.0,218.3,235.0,237.0,225.7,226.7,241.0,245.0,242.3,250.3,241.0,213.7]
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: "Cambria", bodyFontFace: "Calibri" };
const W = 13.33, H = 7.5, MARGIN = 0.6;

function addFooter(slide, note, dark) {
  slide.addText(note, { x: MARGIN, y: H - 0.4, w: W - MARGIN * 2, h: 0.28, fontFace: "Calibri", fontSize: 9.5, color: dark ? "9AA6C4" : MUTED, align: "left" });
}
function titleBlock(slide, kicker, title, dark) {
  slide.addText(kicker, { x: MARGIN, y: 0.42, w: W - MARGIN * 2, h: 0.34, fontFace: "Calibri", fontSize: 12.5, bold: true, color: dark ? "8FB7E0" : TEAL, charSpacing: 1, isTextBox: true });
  slide.addText(title, { x: MARGIN, y: 0.74, w: W - MARGIN * 2, h: 0.65, fontFace: "Cambria", fontSize: 26, bold: true, color: dark ? WHITE : NAVY, isTextBox: true });
}
function questionTag(slide, qnum, qtext) {
  slide.addShape("roundRect", { x: MARGIN, y: 1.42, w: W - MARGIN * 2, h: 0.42, rectRadius: 0.08, fill: { color: CARDBG }, line: { type: "none" } });
  slide.addText(`Q${qnum}`, { x: MARGIN + 0.15, y: 1.42, w: 0.6, h: 0.42, align: "center", valign: "middle", fontFace: "Cambria", fontSize: 14, bold: true, color: TEAL, isTextBox: true, margin: 0 });
  slide.addText(qtext, { x: MARGIN + 0.8, y: 1.42, w: W - MARGIN * 2 - 1.0, h: 0.42, valign: "middle", fontFace: "Calibri", fontSize: 13, color: NAVY, isTextBox: true, margin: 0 });
}
function verdictBox(slide, y, h, answer, color, badge) {
  slide.addShape("roundRect", { x: MARGIN, y, w: W - MARGIN * 2, h, rectRadius: 0.12, fill: { color: "EAF7F0" }, line: { color, width: 1.25 } });
  slide.addText("✓ 答え", { x: MARGIN + 0.3, y: y + 0.12, w: 2, h: 0.3, fontFace: "Calibri", fontSize: 12, bold: true, color: "0F5C3D", isTextBox: true, margin: 0 });
  slide.addText(answer, { x: MARGIN + 0.3, y: y + 0.42, w: W - MARGIN * 2 - 0.6, h: h - 0.55, fontFace: "Cambria", fontSize: 20, bold: true, color: "0F5C3D", isTextBox: true, margin: 0 });
  if (badge) {
    const bc = badge.ok ? "0F5C3D" : "6B4B00";
    const bbg = badge.ok ? WHITE : "FDF3E2";
    slide.addShape("roundRect", { x: W - MARGIN - 4.3, y: y + 0.12, w: 4.3, h: 0.34, rectRadius: 0.07, fill: { color: bbg }, line: { color: bc, width: 0.75 } });
    slide.addText(badge.text, { x: W - MARGIN - 4.2, y: y + 0.12, w: 4.1, h: 0.34, align: "center", valign: "middle", fontFace: "Calibri", fontSize: 9.5, bold: true, color: bc, isTextBox: true, margin: 0 });
  }
}

// ================= 1: Title =================
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addShape("rect", { x: 0, y: 0, w: W, h: H, fill: { color: NAVY } });
  s.addShape("oval", { x: 10.6, y: -1.6, w: 5.5, h: 5.5, fill: { color: DEEPBLUE, transparency: 55 }, line: { type: "none" } });
  s.addShape("oval", { x: -2.0, y: 4.6, w: 4.6, h: 4.6, fill: { color: TEAL, transparency: 60 }, line: { type: "none" } });

  s.addText("血糖値・コンディションデータに基づく", { x: MARGIN, y: 1.7, w: 11, h: 0.4, fontFace: "Calibri", fontSize: 14, bold: true, color: "8FB7E0", charSpacing: 1, isTextBox: true });
  s.addText("この選手への朝食提案", { x: MARGIN, y: 2.15, w: 11.5, h: 1.0, fontFace: "Cambria", fontSize: 38, bold: true, color: WHITE, isTextBox: true });
  s.addText("3つの実践的な問いに、結果と考察で答える", { x: MARGIN, y: 3.15, w: 11, h: 0.5, fontFace: "Calibri", fontSize: 16, color: "CADCFC", isTextBox: true });

  const qs = [
    ["Q1", "固形が良いのか、スムージーが良いのか"],
    ["Q2", "スムージーとおにぎりを食べるタイミングはいつが良いのか"],
    ["Q3", "朝ごはんの糖質（C）は少し減らした方が良いのか"],
  ];
  let y = 4.1;
  qs.forEach(([tag, q]) => {
    s.addShape("oval", { x: MARGIN, y, w: 0.55, h: 0.55, fill: { color: TEAL }, line: { type: "none" } });
    s.addText(tag, { x: MARGIN, y, w: 0.55, h: 0.55, align: "center", valign: "middle", fontFace: "Cambria", fontSize: 15, bold: true, color: WHITE, isTextBox: true, margin: 0 });
    s.addText(q, { x: MARGIN + 0.75, y: y + 0.05, w: 10.5, h: 0.45, valign: "middle", fontFace: "Calibri", fontSize: 15, color: "E8EDF7", isTextBox: true, margin: 0 });
    y += 0.78;
  });
  s.addText("対象：高位脊髄損傷（SCI）車いす陸上選手 1名（反復測定、各条件n=3日）", {
    x: MARGIN, y: 6.85, w: 10, h: 0.35, fontFace: "Calibri", fontSize: 10.5, italic: true, color: "9AA6C4", isTextBox: true
  });
}

// ================= 新知見：血糖ベースラインシフト =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "先にお読みください", "新知見：血糖ベースラインの持続的シフト", false);
  s.addText("14日間の連続CGMデータで、DAY5（8/29）14:50頃から血糖が持続的に上昇し、以後一度も元の水準に戻っていないことが判明しました。夜間平均血糖：DAY1〜4は93〜107 mg/dL→DAY6以降は130〜177 mg/dL。低血糖（70mg/dL未満）は14日間通じて一度も検出されていません。", {
    x: MARGIN, y: 1.7, w: W - MARGIN * 2, h: 1.1, fontFace: "Calibri", fontSize: 13, color: INK, isTextBox: true, margin: 0
  });

  const rows = [
    [{ text: "この提案への影響", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "", options: { bold: true, color: WHITE, fill: { color: NAVY } } }],
    ["Q1（固形 vs スムージー）", "⚠ スムージーはDAY4・5(シフト前)とDAY6(シフト後)が混在。結論は参考値として扱う"],
    ["Q2（食べるタイミング）", "⚠ 同様にスムージー側がシフト前後混在。結論は参考値として扱う"],
    ["Q3（糖質量）", "✓ 両条件ともシフト後で条件が揃っており、結論は維持できる"],
  ].map((r, i) => i === 0 ? r : r.map((c, j) => ({
    text: c, options: { color: j === 0 ? NAVY : (c.startsWith("✓") ? "0F5C3D" : "6B4B00"), bold: j === 0, fill: { color: i % 2 === 0 ? CARDBG : WHITE }, fontSize: 13 }
  })));
  s.addTable(rows, {
    x: MARGIN, y: 3.0, w: W - MARGIN * 2, h: 2.0,
    fontFace: "Calibri", fontSize: 13, border: { type: "solid", color: "E3E1DB", pt: 0.75 },
    autoPage: false, valign: "middle", rowH: 0.5,
    colW: [4.13, 8.6]
  });

  s.addShape("roundRect", { x: MARGIN, y: 5.4, w: W - MARGIN * 2, h: 1.3, rectRadius: 0.1, fill: { color: "FDF3E2" }, line: { color: "EDA100", width: 1 } });
  s.addText("原因はデータからは特定できません。選手・スタッフに8/29 14:30〜15:30頃の状況（補食・体調・ストレス）を確認することを推奨します。原因が判明すればQ1・Q2の結論を再評価できます。", {
    x: MARGIN + 0.3, y: 5.55, w: W - MARGIN * 2 - 0.6, h: 1.0, fontFace: "Calibri", fontSize: 12, bold: true, color: "6B4B00", isTextBox: true, margin: 0
  });
}

// ================= Q1 結果 =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "Q1 – RESULTS", "固形 vs スムージー：結果", false);
  questionTag(s, 1, "固形が良いのか、スムージーが良いのか？");

  s.addChart("line", [
    { name: "固形摂取", labels: times, values: glucose["固形摂取"] },
    { name: "スムージー摂取", labels: times, values: glucose["スムージー摂取"] },
  ], {
    x: MARGIN, y: 2.05, w: 7.6, h: 3.55,
    chartColors: [C_SOLID, C_SMOOTHIE],
    lineSize: 2.25, lineDataSymbol: "none",
    showTitle: false, showLegend: true, legendPos: "b", legendFontSize: 11, legendColor: INK,
    catAxisLabelColor: MUTED, catAxisLabelFontSize: 9, catAxisLabelFrequency: 4,
    valAxisLabelColor: MUTED, valAxisLabelFontSize: 9,
    valAxisTitle: "血糖値 (mg/dL)", showValAxisTitle: true, valAxisTitleFontSize: 10, valAxisTitleColor: MUTED,
    valGridLine: { color: "E3E1DB", size: 0.75 }, catGridLine: { style: "none" },
    catAxisLineColor: "E3E1DB", valAxisLineColor: "E3E1DB"
  });

  const statX = MARGIN + 7.95, statW = W - MARGIN - statX;
  const stats = [
    ["Δピーク血糖値", "85.0", "53.7", "mg/dL"],
    ["変動係数 CV", "14.7%", "11.2%", ""],
    ["練習中(11-14h)平均血糖", "222.1", "135.1", "mg/dL＝燃料供給"],
  ];
  let sy = 2.1;
  stats.forEach(([label, a, b, note]) => {
    s.addText(label, { x: statX, y: sy, w: statW, h: 0.24, fontFace: "Calibri", fontSize: 10.5, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    s.addText(a, { x: statX, y: sy + 0.24, w: statW / 2, h: 0.4, fontFace: "Cambria", fontSize: 18, bold: true, color: C_SMOOTHIE, isTextBox: true, margin: 0 });
    s.addText(b, { x: statX + statW / 2, y: sy + 0.24, w: statW / 2, h: 0.4, fontFace: "Cambria", fontSize: 18, bold: true, color: C_SOLID, isTextBox: true, margin: 0, align: "right" });
    if (note) s.addText(note, { x: statX, y: sy + 0.62, w: statW, h: 0.2, fontFace: "Calibri", fontSize: 8, color: MUTED, isTextBox: true, margin: 0 });
    sy += 1.02;
  });
  s.addText("上＝スムージー／下＝固形", { x: statX, y: sy + 0.02, w: statW, h: 0.3, fontFace: "Calibri", fontSize: 9, color: MUTED, isTextBox: true, margin: 0 });

  s.addShape("roundRect", { x: MARGIN, y: 5.8, w: W - MARGIN * 2, h: 1.05, rectRadius: 0.1, fill: { color: CARDBG }, line: { type: "none" } });
  s.addText("自覚コンディション・毎日のコンディション：頭痛・吐き気はどちらも全時点で最小値、満腹感・食欲もほぼ同水準。夜間コンディション（起床時・睡眠）にも大きな差はない（ただし練習時間がスムージー60分/日・固形140分/日と大きく異なり、RPE等は練習量の交絡を強く受ける）。", {
    x: MARGIN + 0.25, y: 5.9, w: W - MARGIN * 2 - 0.5, h: 0.85, fontFace: "Calibri", fontSize: 11, color: INK, isTextBox: true, margin: 0
  });
  addFooter(s, "15分間隔・条件ごとの平均血糖値（各条件3日間平均）。", false);
}

// ================= Q1 考察 =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "Q1 – DISCUSSION", "固形 vs スムージー：考察と結論", false);
  questionTag(s, 1, "固形が良いのか、スムージーが良いのか？");

  verdictBox(s, 2.05, 1.15, "スムージーの方が良い", C_SMOOTHIE, { ok: false, text: "⚠ 血糖シフトの影響で参考値" });

  const points = [
    "練習中（11:00〜14:00）に使える血糖＝燃料がスムージーの方が圧倒的に多い（222 vs 135 mg/dL）",
    "頭痛・吐き気などの不調は出ておらず、反応性低血糖（急降下）も起きていない",
    "血糖の乱高下（CV・Δピーク）は固形の方が小さいが、実害（症状・クラッシュ）にはつながっていない",
    "選手自身が語っていた「スムージー化で出力が上がった」という体感とも一致する",
  ];
  let y = 3.4;
  points.forEach(p => {
    s.addShape("oval", { x: MARGIN, y: y + 0.06, w: 0.12, h: 0.12, fill: { color: C_SMOOTHIE }, line: { type: "none" } });
    s.addText(p, { x: MARGIN + 0.32, y, w: W - MARGIN * 2 - 0.32, h: 0.5, fontFace: "Calibri", fontSize: 13, color: INK, isTextBox: true, margin: 0 });
    y += 0.62;
  });

  s.addShape("roundRect", { x: MARGIN, y: 6.15, w: W - MARGIN * 2, h: 0.95, rectRadius: 0.1, fill: { color: "FDF3E2" }, line: { color: "EDA100", width: 1 } });
  s.addText("→ ただし最終的には「スムージー単体」よりも「おにぎりと同時に食べる」方がさらに良い結果でした（Q2で解説）。", {
    x: MARGIN + 0.25, y: 6.28, w: W - MARGIN * 2 - 0.5, h: 0.7, fontFace: "Calibri", fontSize: 12.5, bold: true, color: "6B4B00", isTextBox: true, margin: 0
  });
}

// ================= Q2 結果 =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "Q2 – RESULTS", "食べるタイミング：結果", false);
  questionTag(s, 2, "スムージーとおにぎりを食べるタイミングはいつが良いのか？");

  s.addText("4条件とも14:00までの総エネルギーはほぼ同じ。自由摂取が始まる12:00より前（8:00〜11:30）に絞り、「同時に食べる」か「2.5〜3時間ずらして食べる」かを比較。", {
    x: MARGIN, y: 2.0, w: W - MARGIN * 2, h: 0.5, fontFace: "Calibri", fontSize: 12, color: MUTED, isTextBox: true, margin: 0
  });

  const rows = [
    [{ text: "条件", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "タイミング", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "平均血糖(8:00-11:30)", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "CV", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "Δピーク", options: { bold: true, color: WHITE, fill: { color: NAVY } } }],
    ["固形", "分割（おにぎりは2.5〜3h後）", "119.9", "12.0%", "53.7"],
    ["スムージー", "分割（おにぎりは2.5〜3h後）", "187.0", "16.5%", "80.3"],
    ["おにぎり＋スムージー", "同時（8:00に一緒に）", "199.8", "10.1%", "70.7"],
    ["おにぎり＋糖質減", "同時（8:00に一緒に）", "194.9", "8.5%", "52.3"],
  ].map((r, i) => i === 0 ? r : r.map((c, j) => ({
    text: c, options: { color: j === 0 ? NAVY : INK, bold: j === 0, fill: { color: i % 2 === 0 ? CARDBG : WHITE }, fontSize: 12 }
  })));
  s.addTable(rows, {
    x: MARGIN, y: 2.6, w: W - MARGIN * 2, h: 2.0,
    fontFace: "Calibri", fontSize: 12, border: { type: "solid", color: "E3E1DB", pt: 0.75 },
    autoPage: false, valign: "middle", rowH: 0.4,
    colW: [2.3, 3.1, 2.4, 1.63, 1.9]
  });

  s.addShape("roundRect", { x: MARGIN, y: 4.9, w: W - MARGIN * 2, h: 1.95, rectRadius: 0.1, fill: { color: CARDBG }, line: { type: "none" } });
  s.addText("同時摂取にすると、平均血糖はわずかに上がる（187→200、+13程度）ものの、Δピーク・CVはどちらも明確に小さくなる。副食とおにぎりを2.5〜3時間ずらして食べると、それぞれが独立した急峻な山を作るのに対し、同時に食べるとおにぎり（ゆっくり吸収されるデンプン）が副食の急な糖吸収を緩衝し、1つのなだらかな波にまとまると解釈できる。糖質減はこの「なだらかさ」に加えてΔピークも固形並み（52.3 vs 53.7）まで抑えられている。", {
    x: MARGIN + 0.25, y: 5.02, w: W - MARGIN * 2 - 0.5, h: 1.75, fontFace: "Calibri", fontSize: 12, color: INK, isTextBox: true, margin: 0
  });
  addFooter(s, "自覚コンディション：満腹感は同時摂取の方が高いが、頭痛・吐き気には差がない。", false);
}

// ================= Q2 考察 =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "Q2 – DISCUSSION", "食べるタイミング：考察と結論", false);
  questionTag(s, 2, "スムージーとおにぎりを食べるタイミングはいつが良いのか？");

  verdictBox(s, 2.05, 1.15, "8:00に「同時に」食べるのが良い", C_ONIGISMO, { ok: false, text: "⚠ 血糖シフトの影響で参考値" });

  const points = [
    "同時摂取は、練習中の燃料供給をスムージー単独と同水準（220 vs 222 mg/dL）に保ったまま、血糖の乱高下（CV・Δピーク）を明確に小さくする",
    "おにぎり（ゆっくり吸収されるデンプン）が副食の急な糖吸収を緩衝し、波形がなだらかになると解釈できる",
    "満腹感は上がるが、頭痛・吐き気などの消化器症状は軽微で、実害は見られない",
    "夜間コンディション（起床時・睡眠）もスムージー単独よりわずかに良好な傾向",
  ];
  let y = 3.4;
  points.forEach(p => {
    s.addShape("oval", { x: MARGIN, y: y + 0.06, w: 0.12, h: 0.12, fill: { color: C_ONIGISMO }, line: { type: "none" } });
    s.addText(p, { x: MARGIN + 0.32, y, w: W - MARGIN * 2 - 0.32, h: 0.5, fontFace: "Calibri", fontSize: 13, color: INK, isTextBox: true, margin: 0 });
    y += 0.62;
  });

  s.addShape("roundRect", { x: MARGIN, y: 6.15, w: W - MARGIN * 2, h: 0.95, rectRadius: 0.1, fill: { color: "FDF3E2" }, line: { color: "EDA100", width: 1 } });
  s.addText("→ 「おにぎりを崩さず、副食だけをスムージー化して同時に食べる」という部分的液状化のアイデアは、血糖の観点から明確に支持される。", {
    x: MARGIN + 0.25, y: 6.28, w: W - MARGIN * 2 - 0.5, h: 0.7, fontFace: "Calibri", fontSize: 12.5, bold: true, color: "6B4B00", isTextBox: true, margin: 0
  });
}

// ================= Q3 結果 =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "Q3 – RESULTS", "朝ごはんの糖質量：結果", false);
  questionTag(s, 3, "朝ごはんの糖質（C）は少し減らした方が良いのか？");

  s.addText("同時摂取プロトコルの中で、副食の糖質を通常量にした条件（おにぎり＋スムージー）と、少し減らした条件（おにぎり＋糖質減）を比較。", {
    x: MARGIN, y: 1.95, w: W - MARGIN * 2, h: 0.4, fontFace: "Calibri", fontSize: 12, color: MUTED, isTextBox: true, margin: 0
  });

  const glucoseStats = [
    { label: "iAUC 2h (mg/dL・分)", a: "5,230", b: "3,168", note: "糖質減で約39%減" },
    { label: "CV (8:00-11:30)", a: "10.1%", b: "8.5%" },
    { label: "練習中(11-14h)平均血糖", a: "220.1", b: "229.4", note: "糖質減の方がむしろ高い" },
  ];
  s.addText("血糖値", { x: MARGIN, y: 2.45, w: 3, h: 0.3, fontFace: "Calibri", fontSize: 13, bold: true, color: DEEPBLUE, isTextBox: true, margin: 0 });
  const gW = (W - MARGIN * 2 - 0.6) / 3;
  glucoseStats.forEach((m, i) => {
    const x = MARGIN + i * (gW + 0.3);
    s.addShape("roundRect", { x, y: 2.78, w: gW, h: 0.95, rectRadius: 0.08, fill: { color: CARDBG }, line: { type: "none" } });
    s.addText(m.label, { x: x + 0.15, y: 2.84, w: gW - 0.3, h: 0.26, fontFace: "Calibri", fontSize: 10.5, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    s.addText(m.a, { x: x + 0.15, y: 3.1, w: (gW - 0.3) / 2, h: 0.4, fontFace: "Cambria", fontSize: 17, bold: true, color: C_ONIGISMO, isTextBox: true, margin: 0 });
    s.addText(m.b, { x: x + 0.15 + (gW - 0.3) / 2, y: 3.1, w: (gW - 0.3) / 2, h: 0.4, fontFace: "Cambria", fontSize: 17, bold: true, color: C_LOWSUGAR, isTextBox: true, margin: 0, align: "right" });
    if (m.note) s.addText(m.note, { x: x + 0.15, y: 3.5, w: gW - 0.3, h: 0.2, fontFace: "Calibri", fontSize: 8, color: MUTED, isTextBox: true, margin: 0 });
  });

  s.addText("毎日のコンディション（夜のアプリ記録）", { x: MARGIN, y: 3.95, w: 6, h: 0.3, fontFace: "Calibri", fontSize: 13, bold: true, color: C_LOWSUGAR, isTextBox: true, margin: 0 });
  const nightRows = [
    ["", "おにぎり+スムージー", "おにぎり+糖質減"],
    ["起床時コンディション", "2.33", "2.67"],
    ["睡眠の質", "2.00", "2.67"],
    ["RPE", "5.50", "6.33"],
    ["持久力", "3.83", "2.33"],
    ["爆発力", "3.50", "3.33"],
  ];
  s.addTable(nightRows.map((r, i) => i === 0
    ? r.map(c => ({ text: c, options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: 11.5 } }))
    : r.map((c, j) => ({ text: c, options: { color: j === 3 || j === 0 ? (r[0] === "持久力" || r[0] === "爆発力" ? "B23A3A" : INK) : INK, bold: j === 0, fontSize: 11.5, fill: { color: (i === 4 || i === 5) ? "FDECEC" : (i % 2 === 0 ? CARDBG : WHITE) } } }))
  ), { x: MARGIN, y: 4.28, w: 7.3, h: 1.9, fontFace: "Calibri", fontSize: 11.5, border: { type: "solid", color: "E3E1DB", pt: 0.5 }, autoPage: false, valign: "middle", rowH: 0.315, colW: [2.7, 2.3, 2.3] });

  s.addShape("roundRect", { x: MARGIN + 7.6, y: 4.28, w: 4.53, h: 1.9, rectRadius: 0.1, fill: { color: "FDF3E2" }, line: { color: "EDA100", width: 1 } });
  s.addText("⚠ 要注意の矛盾", { x: MARGIN + 7.85, y: 4.42, w: 4, h: 0.28, fontFace: "Calibri", fontSize: 11.5, bold: true, color: "6B4B00", isTextBox: true, margin: 0 });
  s.addText("血糖面はすべて糖質減が優位なのに、持久力・爆発力の自己評価は逆に最低。練習時間も糖質減の方が長め（100分 vs 80分）で交絡の可能性あり。", {
    x: MARGIN + 7.85, y: 4.74, w: 4.05, h: 1.35, fontFace: "Calibri", fontSize: 10.5, color: "6B4B00", isTextBox: true, margin: 0
  });
  addFooter(s, "n=3日／条件。持久力・爆発力は赤字＝糖質減が最も低い値。", false);
}

// ================= Q3 考察 =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "Q3 – DISCUSSION", "朝ごはんの糖質量：考察と結論", false);
  questionTag(s, 3, "朝ごはんの糖質（C）は少し減らした方が良いのか？");

  verdictBox(s, 2.05, 1.15, "血糖面では有望だが、現時点では断定できない", C_LOWSUGAR, { ok: true, text: "✓ シフト後で条件が揃い信頼できる" });

  const points = [
    "糖質を減らすと食後2時間の血糖上昇（iAUC）が約39%減少し、波形もより滑らかになる（CV 8.5%）",
    "練習中の血糖＝燃料供給は減らない（むしろ4条件中最高の229 mg/dL）",
    "起床時コンディション・睡眠の質も4条件中最も良い",
    "一方で持久力・爆発力の自己評価は4条件中最も低く、血糖データと体感が食い違う",
    "練習時間の違い（糖質減100分 vs 通常80分）が体感の悪化を招いた可能性があり、食事の効果と断定できない",
  ];
  let y = 3.4;
  points.forEach((p, i) => {
    const isWarn = i >= 3;
    s.addShape("oval", { x: MARGIN, y: y + 0.06, w: 0.12, h: 0.12, fill: { color: isWarn ? "EDA100" : C_LOWSUGAR }, line: { type: "none" } });
    s.addText(p, { x: MARGIN + 0.32, y, w: W - MARGIN * 2 - 0.32, h: 0.5, fontFace: "Calibri", fontSize: 12.5, color: INK, isTextBox: true, margin: 0 });
    y += 0.56;
  });

  s.addShape("roundRect", { x: MARGIN, y: 6.25, w: W - MARGIN * 2, h: 0.9, rectRadius: 0.1, fill: { color: "FDF3E2" }, line: { color: "EDA100", width: 1 } });
  s.addText("→ 血糖・コンディション面では糖質をやや減らす方向を試す価値があるが、練習内容・時間を揃えた再検証で「持久力低下」が食事の影響かどうかを確認してから本格導入するのが望ましい。", {
    x: MARGIN + 0.25, y: 6.36, w: W - MARGIN * 2 - 0.5, h: 0.7, fontFace: "Calibri", fontSize: 12, bold: true, color: "6B4B00", isTextBox: true, margin: 0
  });
}

// ================= 総合結論 =================
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  titleBlock(s, "CONCLUSION", "この選手への朝食提案（まとめ）", true);

  const answers = [
    { q: "Q1  固形 or スムージー", a: "スムージー ⚠参考値", color: C_SMOOTHIE, note: "血糖シフトの影響あり。練習中の燃料供給は多い" },
    { q: "Q2  食べるタイミング", a: "おにぎりと8:00に同時摂取 ⚠参考値", color: C_ONIGISMO, note: "血糖シフトの影響あり。乱高下を抑え燃料は確保" },
    { q: "Q3  糖質（C）を減らすか", a: "有望だが要検証 ✓信頼できる", color: C_LOWSUGAR, note: "シフト後で条件が揃う。体感との矛盾のみ要検証" },
  ];
  let y = 1.75;
  answers.forEach(a => {
    s.addShape("roundRect", { x: MARGIN, y, w: W - MARGIN * 2, h: 1.15, rectRadius: 0.1, fill: { color: "1A2350" }, line: { type: "none" } });
    s.addShape("rect", { x: MARGIN + 0.3, y: y + 0.24, w: 0.16, h: 0.67, fill: { color: a.color }, line: { type: "none" } });
    s.addText(a.q, { x: MARGIN + 0.65, y: y + 0.14, w: 4.2, h: 0.9, valign: "middle", fontFace: "Calibri", fontSize: 14, color: "9AA6C4", isTextBox: true, margin: 0 });
    s.addText(a.a, { x: MARGIN + 5.0, y: y + 0.14, w: 4.7, h: 0.9, valign: "middle", fontFace: "Cambria", fontSize: 19, bold: true, color: WHITE, isTextBox: true, margin: 0 });
    s.addText(a.note, { x: MARGIN + 9.8, y: y + 0.14, w: 2.9, h: 0.9, valign: "middle", fontFace: "Calibri", fontSize: 10.5, color: "CADCFC", isTextBox: true, margin: 0 });
    y += 1.35;
  });

  s.addShape("roundRect", { x: MARGIN, y: 5.8, w: W - MARGIN * 2, h: 1.05, rectRadius: 0.1, fill: { color: TEAL }, line: { type: "none" } });
  s.addText("最終提案：8:00に「おにぎり＋スムージー（通常糖質量）」を同時摂取。糖質を少し減らす案は、練習量を揃えた追加検証で持久力への影響を確認してから判断する。", {
    x: MARGIN + 0.3, y: 5.9, w: W - MARGIN * 2 - 0.6, h: 0.85, valign: "middle", fontFace: "Calibri", fontSize: 13.5, bold: true, color: WHITE, isTextBox: true, margin: 0
  });
  addFooter(s, "データ出典：for_AI_.xlsx／0824スケジュール.xlsx／condition_app_2026-08-25_2026-09-07.xlsx", true);
}

pres.writeFile({ fileName: "output_recommendations.pptx" }).then(() => console.log("done"));
