const pptxgen = require("pptxgenjs");

// ---- palette ----
const NAVY = "21295C";
const DEEPBLUE = "065A82";
const TEAL = "1C7293";
const WHITE = "FFFFFF";
const INK = "1A1A1A";
const MUTED = "5C6570";
const CARDBG = "F4F7F9";

const C_SOLID = "2A78D6";      // 固形
const C_SMOOTHIE = "EB6834";   // スムージー
const C_ONIGISMO = "1BAF7A";   // おにぎり+スムージー
const C_LOWSUGAR = "EDA100";   // 糖質減

const times = ["08:00","08:15","08:30","08:45","09:00","09:15","09:30","09:45","10:00","10:15","10:30","10:45","11:00","11:15","11:30","11:45","12:00","12:15","12:30","12:45","13:00","13:15","13:30","13:45","14:00"];

const glucose = {
  "固形摂取":            [99.0,112.0,133.3,129.0,113.0,105.3,108.7,108.7,106.0,120.0,130.3,125.3,120.3,135.0,152.7,143.0,139.0,129.7,119.0,131.0,143.0,136.7,138.0,140.3,129.0],
  "スムージー摂取":        [159.3,163.0,182.0,202.7,193.7,163.7,149.0,148.7,154.7,179.3,194.3,226.0,226.3,223.0,239.7,244.3,213.7,225.0,218.3,218.7,224.7,207.0,212.3,222.7,211.0],
  "おにぎり＋スムージー":    [164.3,169.3,208.7,235.0,225.7,219.3,207.3,212.3,207.0,191.3,188.0,185.0,182.7,193.0,208.0,226.3,229.0,227.3,231.3,242.3,236.7,224.7,219.3,218.7,222.3],
  "おにぎり＋糖質減":      [166.0,183.7,217.0,197.0,193.7,193.7,198.7,185.3,174.3,172.3,199.7,217.7,211.0,195.0,218.3,235.0,237.0,225.7,226.7,241.0,245.0,242.3,250.3,241.0,213.7]
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
pres.theme = { headFontFace: "Cambria", bodyFontFace: "Calibri" };

const W = 13.33, H = 7.5, MARGIN = 0.6;

function addFooter(slide, pageNote, dark) {
  slide.addText(pageNote, {
    x: MARGIN, y: H - 0.42, w: W - MARGIN * 2, h: 0.3,
    fontFace: "Calibri", fontSize: 10, color: dark ? "9AA6C4" : MUTED,
    align: "left"
  });
}

function titleBlock(slide, kicker, title, dark) {
  slide.addText(kicker, {
    x: MARGIN, y: 0.5, w: W - MARGIN * 2, h: 0.4,
    fontFace: "Calibri", fontSize: 13, bold: true, color: dark ? "8FB7E0" : TEAL,
    charSpacing: 1, isTextBox: true
  });
  slide.addText(title, {
    x: MARGIN, y: 0.86, w: W - MARGIN * 2, h: 0.7,
    fontFace: "Cambria", fontSize: 27, bold: true, color: dark ? WHITE : NAVY,
    isTextBox: true
  });
}

// ---- reusable: 2-series glucose curve chart ----
function glucoseChartSlide(kicker, title, condA, condB, footNote) {
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, kicker, title, false);

  const chartData = [condA, condB].map(k => ({ name: k, labels: times, values: glucose[k] }));
  const colorMap = { "固形摂取": C_SOLID, "スムージー摂取": C_SMOOTHIE, "おにぎり＋スムージー": C_ONIGISMO, "おにぎり＋糖質減": C_LOWSUGAR };
  const chartColors = [colorMap[condA], colorMap[condB]];

  s.addChart("line", chartData, {
    x: MARGIN, y: 1.7, w: W - MARGIN * 2, h: 4.6,
    chartColors,
    lineSize: 2.5, lineDataSymbol: "none",
    showTitle: false,
    showLegend: true, legendPos: "b", legendFontSize: 12, legendColor: INK,
    catAxisLabelColor: MUTED, catAxisLabelFontSize: 10,
    valAxisLabelColor: MUTED, valAxisLabelFontSize: 10,
    valAxisTitle: "血糖値 (mg/dL)", showValAxisTitle: true, valAxisTitleFontSize: 11, valAxisTitleColor: MUTED,
    valGridLine: { color: "E3E1DB", size: 0.75 },
    catGridLine: { style: "none" },
    catAxisLineColor: "E3E1DB", valAxisLineColor: "E3E1DB",
    catAxisLabelFrequency: 4,
    dataLabelColor: INK
  });
  addFooter(s, footNote, false);
  return s;
}

// ---- reusable: small-multiple bar chart panel row ----
function barPanelsSlide(kicker, title, conds, chartColors, panels, footNote) {
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, kicker, title, false);

  const n = panels.length;
  const panelW = n === 2 ? 5.85 : 3.75;
  const totalW = n === 2 ? panelW * 2 + 0.4 : panelW * 3 + 0.4 * 2;
  const startX = MARGIN + ((W - MARGIN * 2) - totalW) / 2;

  panels.forEach((p, i) => {
    const x = startX + i * (panelW + 0.4);
    s.addText(p.titleMain, { x, y: 1.75, w: panelW, h: 0.3, fontFace: "Calibri", fontSize: 13, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    s.addText(p.titleSub, { x, y: 2.05, w: panelW, h: 0.26, fontFace: "Calibri", fontSize: 10.5, color: MUTED, isTextBox: true, margin: 0 });
    s.addChart("bar", [{ name: p.titleMain, labels: conds, values: p.values }], {
      x, y: 2.42, w: panelW, h: 3.6,
      barDir: "col",
      chartColors, chartColorsOpacity: 100,
      showTitle: false, showLegend: false,
      showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 11, dataLabelColor: INK,
      dataLabelFormatCode: p.fmt || "0.0",
      catAxisLabelColor: MUTED, catAxisLabelFontSize: 10, catAxisLabelRotate: n === 2 ? 0 : 20,
      valAxisHidden: true,
      catGridLine: { style: "none" }, valGridLine: { style: "none" },
      catAxisLineColor: "E3E1DB", valAxisLineColor: "E3E1DB",
      barGapWidthPct: 40
    });
  });
  addFooter(s, footNote, false);
  return s;
}

// ---- reusable: section divider slide ----
function sectionDivider(kicker, title, sub, num) {
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addShape("rect", { x: 0, y: 0, w: W, h: H, fill: { color: NAVY } });
  s.addShape("oval", { x: 10.6, y: -1.6, w: 5.5, h: 5.5, fill: { color: DEEPBLUE, transparency: 55 }, line: { type: "none" } });
  s.addText(num, { x: MARGIN, y: 2.6, w: 3, h: 1.3, fontFace: "Cambria", fontSize: 64, bold: true, color: "3A4A8F", isTextBox: true, margin: 0 });
  s.addText(kicker, { x: MARGIN, y: 3.75, w: 10.5, h: 0.4, fontFace: "Calibri", fontSize: 14, bold: true, color: "8FB7E0", charSpacing: 1.5, isTextBox: true });
  s.addText(title, { x: MARGIN, y: 4.15, w: 11.5, h: 1.0, fontFace: "Cambria", fontSize: 34, bold: true, color: WHITE, isTextBox: true });
  s.addText(sub, { x: MARGIN, y: 5.05, w: 11.0, h: 0.9, fontFace: "Calibri", fontSize: 14, color: "CADCFC", isTextBox: true });
  return s;
}

// ================= 1: Title =================
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addShape("rect", { x: 0, y: 0, w: W, h: H, fill: { color: NAVY } });
  s.addShape("oval", { x: 10.6, y: -1.6, w: 5.5, h: 5.5, fill: { color: DEEPBLUE, transparency: 55 }, line: { type: "none" } });
  s.addShape("oval", { x: -2.0, y: 4.6, w: 4.6, h: 4.6, fill: { color: TEAL, transparency: 60 }, line: { type: "none" } });

  s.addText("卒業論文発表", {
    x: MARGIN, y: 1.5, w: 10.5, h: 0.5, fontFace: "Calibri", fontSize: 15, bold: true,
    color: "8FB7E0", charSpacing: 1.5, isTextBox: true
  });
  s.addText("おにぎり×スムージー 部分的液状化が\nSCI車いす選手の血糖動態・コンディションに与える影響", {
    x: MARGIN, y: 2.0, w: 11.8, h: 1.8, fontFace: "Cambria", fontSize: 32, bold: true,
    color: WHITE, isTextBox: true, lineSpacing: 40
  });
  s.addText("実験1：副食の形態比較（固形 vs スムージー）　／　実験2：部分的液状化と糖質量の最適化", {
    x: MARGIN, y: 3.95, w: 11.5, h: 0.5, fontFace: "Calibri", fontSize: 16,
    color: "CADCFC", isTextBox: true
  });

  s.addShape("line", { x: MARGIN, y: 5.0, w: W - MARGIN * 2, h: 0, line: { color: "3A4A8F", width: 1 } });

  s.addText("○○大学 ○○学部 ○○学科", { x: MARGIN, y: 5.3, w: 8, h: 0.4, fontFace: "Calibri", fontSize: 13, color: "9AA6C4", isTextBox: true });
  s.addText("発表者：○○ ○○　　指導教員：○○ ○○", { x: MARGIN, y: 5.75, w: 8, h: 0.4, fontFace: "Calibri", fontSize: 13, color: "9AA6C4", isTextBox: true });
  s.addText("対象：高位脊髄損傷（SCI）車いす陸上選手 1名を対象とした反復測定研究", {
    x: MARGIN, y: 6.7, w: 10, h: 0.4, fontFace: "Calibri", fontSize: 11, italic: true, color: "9AA6C4", isTextBox: true
  });
}

// ================= 2: 目次 =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "AGENDA", "目次", false);
  const items = [
    "1. 研究の背景と目的",
    "2. 実験デザイン・測定方法",
    "3. 実験1：副食の形態比較（固形 vs スムージー）",
    "4. 実験2：部分的液状化と糖質量の最適化",
    "5. 総合考察",
    "6. 結論・今後の課題",
  ];
  let y = 1.9;
  items.forEach(it => {
    s.addShape("oval", { x: MARGIN, y: y + 0.06, w: 0.1, h: 0.1, fill: { color: TEAL }, line: { type: "none" } });
    s.addText(it, { x: MARGIN + 0.35, y, w: 11, h: 0.5, fontFace: "Calibri", fontSize: 18, color: NAVY, isTextBox: true, margin: 0 });
    y += 0.78;
  });
}

// ================= 3: 背景 =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "BACKGROUND", "研究の背景と目的", false);

  const items = [
    { n: "1", t: "SCI選手の病態生理", d: "高位脊髄損傷者は交感神経の遠心路が遮断され、食後低血圧・血糖値スパイク／反応性低血糖を起こしやすい。" },
    { n: "2", t: "現場での気づき", d: "「おにぎり2個＋バナナ＆ヨーグルト」の副食をスムージー化したところ、練習時の出力が劇的に向上したとの報告。" },
    { n: "3", t: "作業仮説", d: "おにぎりの満足感は残しつつ副食を部分的に液状化し、総固形物量を減らすことで胃排泄を促し、血糖・消化ストレスを回避できるのでは。" },
    { n: "4", t: "研究目的", d: "実験1で副食の形態変化（固形/液状）の単独効果を確認したうえで、実験2で「部分的液状化＋糖質量最適化」の効果を血糖動態・自覚コンディション・トレーニング指標から検証する。" },
  ];
  const colors = [DEEPBLUE, TEAL, C_ONIGISMO, NAVY];
  let y = 1.85;
  items.forEach((it, i) => {
    s.addShape("oval", { x: MARGIN, y: y, w: 0.55, h: 0.55, fill: { color: colors[i] }, line: { type: "none" } });
    s.addText(it.n, { x: MARGIN, y: y, w: 0.55, h: 0.55, align: "center", valign: "middle", fontFace: "Cambria", fontSize: 18, bold: true, color: WHITE, isTextBox: true, margin: 0 });
    s.addText(it.t, { x: MARGIN + 0.8, y: y - 0.03, w: 10.8, h: 0.35, fontFace: "Calibri", fontSize: 15, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    s.addText(it.d, { x: MARGIN + 0.8, y: y + 0.32, w: 10.9, h: 0.6, fontFace: "Calibri", fontSize: 12.5, color: MUTED, isTextBox: true, margin: 0 });
    y += 1.28;
  });
  addFooter(s, "研究の背景と意義（提供資料より要約）", false);
}

// ================= 4: 全体の実験デザイン =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "METHOD", "全体の実験デザイン（4条件・DAY1〜14）", false);

  const rows = [
    [{ text: "条件", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "日程", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "8:00の食事内容", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "おにぎりのタイミング", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "対応する実験", options: { bold: true, color: WHITE, fill: { color: NAVY } } }],
    ["固形摂取", "DAY1〜3", "果物ヨーグルト（固形）のみ", "約2.5〜3時間後", "実験1"],
    ["スムージー摂取", "DAY4〜6", "果物ヨーグルト（スムージー）のみ", "約2.5〜3時間後", "実験1"],
    ["おにぎり＋スムージー", "DAY8〜10", "おにぎり＋スムージー（同時）", "8:00に同時摂取", "実験2"],
    ["おにぎり＋糖質減", "DAY11〜13", "おにぎり＋スムージー糖質減（同時）", "8:00に同時摂取", "実験2"],
  ].map((r, i) => i === 0 ? r : r.map((c, j) => ({
    text: c, options: { color: j === 0 ? NAVY : INK, bold: j === 0 || j === 4, fill: { color: i % 2 === 0 ? CARDBG : WHITE }, fontSize: 12 }
  })));

  s.addTable(rows, {
    x: MARGIN, y: 1.8, w: W - MARGIN * 2, h: 2.2,
    fontFace: "Calibri", fontSize: 12, border: { type: "solid", color: "E3E1DB", pt: 0.75 },
    autoPage: false, valign: "middle", rowH: 0.44,
    colW: [2.2, 1.1, 4.3, 2.43, 2.1]
  });

  s.addShape("roundRect", { x: MARGIN, y: 4.35, w: W - MARGIN * 2, h: 2.15, rectRadius: 0.12, fill: { color: "FDF3E2" }, line: { color: "EDA100", width: 1 } });
  s.addText("⚠ 重要な注意点", { x: MARGIN + 0.3, y: 4.52, w: 6, h: 0.35, fontFace: "Calibri", fontSize: 13, bold: true, color: "6B4B00", isTextBox: true, margin: 0 });
  s.addText(
    "固形・スムージー条件（実験1）は副食のみを先に食べ、おにぎりは約2.5〜3時間後。おにぎり＋スムージー・糖質減条件（実験2）はおにぎりと副食を同時摂取。つまり4条件とも14:00までの総摂取エネルギーはほぼ同じで、違いの本質は「食べる中身」ではなく「摂取タイミング」にある。トレーニングはどの条件も11:00〜14:00の間に実施（1日60〜180分、条件ブロックにより変動）。各条件 n=3日（同一選手の反復測定）。",
    { x: MARGIN + 0.3, y: 4.92, w: W - MARGIN * 2 - 0.6, h: 1.45, fontFace: "Calibri", fontSize: 12, color: "6B4B00", isTextBox: true, margin: 0 }
  );
  addFooter(s, "DAY7=調整日、DAY14=予備日。12:00以降は自由摂取。", false);
}

// ================= 5: 実験デザインのタイムライン =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "METHOD", "1日の測定タイムライン", false);

  const rowDefs = [
    { label: "固形摂取", sub: "実験1 / DAY1〜3", color: C_SOLID, breakfast: "果物ヨーグルト（固形）", onigiriLater: true },
    { label: "スムージー摂取", sub: "実験1 / DAY4〜6", color: C_SMOOTHIE, breakfast: "果物ヨーグルト（スムージー）", onigiriLater: true },
    { label: "おにぎり＋スムージー", sub: "実験2 / DAY8〜10", color: C_ONIGISMO, breakfast: "おにぎり＋スムージー（同時）", onigiriLater: false },
    { label: "おにぎり＋糖質減", sub: "実験2 / DAY11〜13", color: C_LOWSUGAR, breakfast: "おにぎり＋スムージー糖質減（同時）", onigiriLater: false },
  ];

  const TL_X0 = MARGIN + 2.35, TL_X1 = W - MARGIN - 0.1;
  const TL_W = TL_X1 - TL_X0;
  const H0 = 8, H1 = 20;
  const hourToX = h => TL_X0 + ((h - H0) / (H1 - H0)) * TL_W;

  const axisY = 1.72;
  for (let h = H0; h <= H1; h += 2) {
    const tickAlign = h === H0 ? "left" : (h === H1 ? "right" : "center");
    const tickX = h === H0 ? hourToX(h) : (h === H1 ? hourToX(h) - 0.7 : hourToX(h) - 0.35);
    s.addText(`${h}:00`, { x: tickX, y: axisY, w: 0.7, h: 0.22, align: tickAlign, fontFace: "Calibri", fontSize: 9, color: MUTED, isTextBox: true, margin: 0 });
    s.addShape("line", { x: hourToX(h), y: axisY + 0.24, w: 0, h: 4.55, line: { color: "EDEBE4", width: 0.75 } });
  }

  const rowH = 1.02, rowTop0 = 2.05;
  rowDefs.forEach((r, i) => {
    const y = rowTop0 + i * rowH;
    const barY = y + 0.32, barH = 0.34;
    s.addText(r.label, { x: MARGIN, y: y + 0.02, w: 2.05, h: 0.28, fontFace: "Calibri", fontSize: 12, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    s.addText(r.sub, { x: MARGIN, y: y + 0.3, w: 2.05, h: 0.24, fontFace: "Calibri", fontSize: 9, color: MUTED, isTextBox: true, margin: 0 });

    s.addShape("line", { x: TL_X0, y: barY + barH / 2, w: TL_W, h: 0, line: { color: "E3E1DB", width: 1 } });

    const bx = hourToX(8);
    s.addShape("roundRect", { x: bx, y: barY, w: 0.55, h: barH, rectRadius: 0.05, fill: { color: r.color }, line: { type: "none" } });
    s.addText(r.breakfast, { x: bx - 0.1, y: barY - 0.28, w: 3.4, h: 0.26, fontFace: "Calibri", fontSize: 8.5, color: r.color, bold: true, isTextBox: true, margin: 0 });

    if (r.onigiriLater) {
      const ox = hourToX(10.5);
      s.addShape("oval", { x: ox - 0.06, y: barY + barH / 2 - 0.06, w: 0.12, h: 0.12, fill: { color: r.color }, line: { color: WHITE, width: 1 } });
      s.addText("おにぎり摂取", { x: ox - 0.55, y: barY + barH + 0.03, w: 1.3, h: 0.22, align: "center", fontFace: "Calibri", fontSize: 8, color: r.color, isTextBox: true, margin: 0 });
    }

    const tx0 = hourToX(11), tx1 = hourToX(14);
    s.addShape("roundRect", { x: tx0, y: barY, w: tx1 - tx0, h: barH, rectRadius: 0.05, fill: { color: NAVY, transparency: 25 }, line: { type: "none" } });

    const dx = hourToX(20);
    s.addShape("oval", { x: dx - 0.055, y: barY + barH / 2 - 0.055, w: 0.11, h: 0.11, fill: { color: MUTED }, line: { type: "none" } });
  });

  s.addShape("roundRect", { x: MARGIN, y: rowTop0 + rowDefs.length * rowH + 0.15, w: 0.3, h: 0.16, rectRadius: 0.04, fill: { color: NAVY, transparency: 25 }, line: { type: "none" } });
  s.addText("トレーニング（60〜180分、11:00〜14:00の間で実施）", { x: MARGIN + 0.38, y: rowTop0 + rowDefs.length * rowH + 0.06, w: 5.5, h: 0.32, fontFace: "Calibri", fontSize: 10, color: INK, isTextBox: true, margin: 0 });
  s.addShape("oval", { x: MARGIN + 6.3, y: rowTop0 + rowDefs.length * rowH + 0.18, w: 0.11, h: 0.11, fill: { color: MUTED }, line: { type: "none" } });
  s.addText("20:00 夕食＋夜のコンディション記録（毎日共通）", { x: MARGIN + 6.55, y: rowTop0 + rowDefs.length * rowH + 0.06, w: 5.5, h: 0.32, fontFace: "Calibri", fontSize: 10, color: INK, isTextBox: true, margin: 0 });

  addFooter(s, "色付きブロック＝朝の被験食摂取（8:00）。実験1条件はおにぎりを約2.5時間後に別途摂取。灰色帯＝全条件共通のトレーニング時間帯。", false);
}

// ================= 6: 測定方法 =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "METHOD", "測定項目", false);

  const measures = [
    { icon: "①", title: "血糖値", sub: "15分間隔・8:00〜14:00（各条件3日間平均）", color: C_SOLID },
    { icon: "②", title: "自覚コンディション（食後）", sub: "満腹感・頭痛・吐き気・食欲を30分間隔でアンケート", color: C_ONIGISMO },
    { icon: "③", title: "夜間コンディションアプリ", sub: "起床時コンディション・睡眠の質／時間・RPE・爆発力・持久力・運動後疲労を毎晩記録", color: C_LOWSUGAR },
  ];
  let y = 2.0;
  measures.forEach(m => {
    s.addShape("roundRect", { x: MARGIN, y, w: W - MARGIN * 2, h: 1.3, rectRadius: 0.1, fill: { color: CARDBG }, line: { type: "none" } });
    s.addShape("oval", { x: MARGIN + 0.3, y: y + 0.32, w: 0.65, h: 0.65, fill: { color: m.color }, line: { type: "none" } });
    s.addText(m.icon, { x: MARGIN + 0.3, y: y + 0.32, w: 0.65, h: 0.65, align: "center", valign: "middle", fontFace: "Cambria", fontSize: 22, bold: true, color: WHITE, isTextBox: true, margin: 0 });
    s.addText(m.title, { x: MARGIN + 1.2, y: y + 0.28, w: 10.5, h: 0.4, fontFace: "Calibri", fontSize: 16, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    s.addText(m.sub, { x: MARGIN + 1.2, y: y + 0.68, w: 10.5, h: 0.4, fontFace: "Calibri", fontSize: 12.5, color: MUTED, isTextBox: true, margin: 0 });
    y += 1.55;
  });
  addFooter(s, "n = 3日／条件（同一選手の反復測定）。統計的検定ではなく記述的傾向として解釈。", false);
}

// ================= 実験1 Section divider =================
sectionDivider("EXPERIMENT 1", "実験1：副食の形態比較", "固形摂取 vs スムージー摂取（DAY1〜6）― 副食を液状化する単独の効果を検証する", "01");

// ================= 実験1: 目的・条件 =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "EXPERIMENT 1", "目的と条件", false);

  s.addShape("roundRect", { x: MARGIN, y: 1.8, w: W - MARGIN * 2, h: 1.2, rectRadius: 0.1, fill: { color: CARDBG }, line: { type: "none" } });
  s.addText("目的", { x: MARGIN + 0.3, y: 1.95, w: 2, h: 0.3, fontFace: "Calibri", fontSize: 13, bold: true, color: TEAL, isTextBox: true, margin: 0 });
  s.addText("副食（果物ヨーグルト）を固形のまま摂るか、スムージー化して摂るかで、血糖動態・自覚コンディションにどのような違いが生じるかを検証する。おにぎりはどちらの条件でも約2.5〜3時間後に別途摂取するため、副食の「形態」のみを切り出して比較できる。", {
    x: MARGIN + 0.3, y: 2.25, w: W - MARGIN * 2 - 0.6, h: 0.65, fontFace: "Calibri", fontSize: 12.5, color: INK, isTextBox: true, margin: 0
  });

  const colW = (W - MARGIN * 2 - 0.4) / 2;
  function condCard(x, label, sub, color, desc) {
    s.addShape("roundRect", { x, y: 3.3, w: colW, h: 2.6, rectRadius: 0.1, fill: { color: CARDBG }, line: { type: "none" } });
    s.addShape("rect", { x: x + 0.3, y: 3.5, w: 0.16, h: 0.5, fill: { color }, line: { type: "none" } });
    s.addText(label, { x: x + 0.6, y: 3.44, w: colW - 0.9, h: 0.4, fontFace: "Calibri", fontSize: 17, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    s.addText(sub, { x: x + 0.6, y: 3.84, w: colW - 0.9, h: 0.3, fontFace: "Calibri", fontSize: 11.5, color: MUTED, isTextBox: true, margin: 0 });
    s.addText(desc, { x: x + 0.3, y: 4.3, w: colW - 0.6, h: 1.45, fontFace: "Calibri", fontSize: 12.5, color: INK, isTextBox: true, margin: 0 });
  }
  condCard(MARGIN, "固形摂取", "DAY1〜3（n=3日）", C_SOLID, "8:00に果物ヨーグルトを固形のまま摂取。\nおにぎり2個は10:00〜11:00頃に別途摂取。\n11:00〜14:00の間にトレーニング。");
  condCard(MARGIN + colW + 0.4, "スムージー摂取", "DAY4〜6（n=3日）", C_SMOOTHIE, "8:00に果物ヨーグルトをスムージー化して摂取。\nおにぎり2個は10:00〜11:00頃に別途摂取（固形と同一プロトコル）。\n11:00〜14:00の間にトレーニング。");

  addFooter(s, "測定：血糖値（15分間隔）、自覚コンディション（30分間隔アンケート）", false);
}

// ================= 実験1: 結果① 血糖推移 =================
glucoseChartSlide("EXPERIMENT 1 – RESULTS", "血糖値の推移（8:00〜14:00）",
  "固形摂取", "スムージー摂取",
  "15分間隔・条件ごとの平均血糖値（各条件3日間平均）。破線省略。");

// ================= 実験1: 結果② 主要指標 =================
barPanelsSlide("EXPERIMENT 1 – RESULTS", "主要指標の比較",
  ["固形", "スムージー"], [C_SOLID, C_SMOOTHIE],
  [
    { titleMain: "Δピーク血糖値 (mg/dL)", titleSub: "最高値 − 摂取直前", values: [53.7, 85.0], fmt: "0.0" },
    { titleMain: "変動係数 CV (%)", titleSub: "6時間の乱高下の大きさ", values: [11.2, 14.7], fmt: "0.0" },
    { titleMain: "練習中(11-14h)平均血糖", titleSub: "mg/dL（燃料供給の目安）", values: [135.1, 222.1], fmt: "#,##0" },
  ],
  "副食を液状化するだけで、Δピーク・CVともに増大。一方、練習中の血糖水準はスムージーの方が大幅に高い。");

// ================= 実験1: 結果③ 自覚コンディション =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "EXPERIMENT 1 – RESULTS", "自覚コンディション", false);

  const condTimes = ["8:00", "8:30", "9:00", "9:30", "10:00"];
  const fullness = { "固形摂取": [1.67, 4.00, 4.00, 2.00, 2.00], "スムージー摂取": [3.33, 3.67, 5.00, 2.00, 1.33] };
  const appetite = { "固形摂取": [7.67, 8.00, 7.00, 7.67, 7.67], "スムージー摂取": [8.67, 6.33, 5.50, 7.67, 8.67] };

  function miniChart(x, title, dataObj) {
    s.addText(title, { x, y: 1.75, w: 5.7, h: 0.28, fontFace: "Calibri", fontSize: 12.5, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    s.addChart("line", [
      { name: "固形摂取", labels: condTimes, values: dataObj["固形摂取"] },
      { name: "スムージー摂取", labels: condTimes, values: dataObj["スムージー摂取"] },
    ], {
      x, y: 2.05, w: 5.7, h: 2.7,
      chartColors: [C_SOLID, C_SMOOTHIE],
      lineSize: 2.25, lineDataSymbol: "circle", lineDataSymbolSize: 5,
      showTitle: false, showLegend: true, legendPos: "b", legendFontSize: 10.5, legendColor: INK,
      catAxisLabelColor: MUTED, catAxisLabelFontSize: 10,
      valAxisLabelColor: MUTED, valAxisLabelFontSize: 10,
      valAxisMinVal: 0, valAxisMaxVal: 10,
      valGridLine: { color: "E3E1DB", size: 0.75 },
      catGridLine: { style: "none" },
      catAxisLineColor: "E3E1DB", valAxisLineColor: "E3E1DB"
    });
  }
  miniChart(MARGIN, "満腹感の推移 (0=空腹〜10=満腹)", fullness);
  miniChart(MARGIN + 6.1, "食欲(摂食可能感)の推移 (0〜10)", appetite);

  s.addShape("roundRect", { x: MARGIN, y: 5.05, w: W - MARGIN * 2, h: 1.3, rectRadius: 0.1, fill: { color: "EAF7F0" }, line: { type: "none" } });
  s.addText("✓ 頭痛・吐き気はどちらの条件も全時点で最小値（1）＝消化器症状に有意差なし", {
    x: MARGIN + 0.3, y: 5.22, w: W - MARGIN * 2 - 0.6, h: 0.35, fontFace: "Calibri", fontSize: 13, bold: true, color: "0F5C3D", isTextBox: true, margin: 0
  });
  s.addText("満腹感・食欲もほぼ同水準で推移しており、副食のみを液状化しても自覚的な消化器症状・満腹感に目立った違いは生じていない。", {
    x: MARGIN + 0.3, y: 5.58, w: W - MARGIN * 2 - 0.6, h: 0.65, fontFace: "Calibri", fontSize: 12, color: "0F5C3D", isTextBox: true, margin: 0
  });
}

// ================= 実験1: 考察 =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "EXPERIMENT 1 – DISCUSSION", "実験1 考察", false);

  const points = [
    { t: "血糖の乱高下は液状化により増大", d: "Δピークは固形の1.6倍（85.0 vs 53.7 mg/dL）、CVも高い（14.7% vs 11.2%）。液状化は消化の負担感を下げる一方、血糖の安定には寄与しない。" },
    { t: "消化器症状には有意差なし", d: "頭痛・吐き気はどちらも全時点で最小値。満腹感・食欲も同水準。液状化そのものが不調を招いているわけではない。" },
    { t: "練習中の血糖水準はスムージーの方が高い", d: "11:00〜14:00の平均血糖は固形135 mg/dLに対しスムージー222 mg/dL。選手の「出力向上」の体感は、血糖の安定ではなく、消化器系の負担軽減、または燃料供給量の違いによる可能性がある。" },
    { t: "示唆", d: "副食の液状化「単独」では血糖の乱高下を悪化させる副作用があり、実験2で検証する「おにぎりとの同時摂取」が鍵になると考えられる。" },
  ];
  let y = 1.85;
  points.forEach((p, i) => {
    s.addShape("oval", { x: MARGIN, y, w: 0.42, h: 0.42, fill: { color: i === points.length - 1 ? C_ONIGISMO : TEAL }, line: { type: "none" } });
    s.addText(String(i + 1), { x: MARGIN, y, w: 0.42, h: 0.42, align: "center", valign: "middle", fontFace: "Cambria", fontSize: 14, bold: true, color: WHITE, isTextBox: true, margin: 0 });
    s.addText(p.t, { x: MARGIN + 0.65, y: y - 0.03, w: 11.3, h: 0.32, fontFace: "Calibri", fontSize: 14, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    s.addText(p.d, { x: MARGIN + 0.65, y: y + 0.3, w: 11.3, h: 0.65, fontFace: "Calibri", fontSize: 12, color: MUTED, isTextBox: true, margin: 0 });
    y += 1.28;
  });
  addFooter(s, "⚠ 総合考察で後述する血糖ベースラインシフトの影響を受けている可能性があり、①②の数値は参考値として扱う。", false);
}

// ================= 実験2 Section divider =================
sectionDivider("EXPERIMENT 2", "実験2：部分的液状化と糖質量の最適化", "おにぎり＋スムージー vs おにぎり＋糖質減（DAY8〜13）― おにぎりを崩さず同時摂取する方式の効果と、総糖質量最適化の効果を検証する", "02");

// ================= 実験2: 目的・条件 =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "EXPERIMENT 2", "目的と条件", false);

  s.addShape("roundRect", { x: MARGIN, y: 1.8, w: W - MARGIN * 2, h: 1.2, rectRadius: 0.1, fill: { color: CARDBG }, line: { type: "none" } });
  s.addText("目的", { x: MARGIN + 0.3, y: 1.95, w: 2, h: 0.3, fontFace: "Calibri", fontSize: 13, bold: true, color: TEAL, isTextBox: true, margin: 0 });
  s.addText("おにぎりを崩さず副食のみをスムージー化し、8:00に同時摂取する「部分的液状化」プロトコルが血糖動態・コンディションに与える影響を検証する。さらに副食の糖質量を減らすことで、血糖の乱高下をさらに抑制できるかを検証する。", {
    x: MARGIN + 0.3, y: 2.25, w: W - MARGIN * 2 - 0.6, h: 0.65, fontFace: "Calibri", fontSize: 12.5, color: INK, isTextBox: true, margin: 0
  });

  const colW = (W - MARGIN * 2 - 0.4) / 2;
  function condCard(x, label, sub, color, desc) {
    s.addShape("roundRect", { x, y: 3.3, w: colW, h: 2.6, rectRadius: 0.1, fill: { color: CARDBG }, line: { type: "none" } });
    s.addShape("rect", { x: x + 0.3, y: 3.5, w: 0.16, h: 0.5, fill: { color }, line: { type: "none" } });
    s.addText(label, { x: x + 0.6, y: 3.44, w: colW - 0.9, h: 0.4, fontFace: "Calibri", fontSize: 16, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    s.addText(sub, { x: x + 0.6, y: 3.84, w: colW - 0.9, h: 0.3, fontFace: "Calibri", fontSize: 11.5, color: MUTED, isTextBox: true, margin: 0 });
    s.addText(desc, { x: x + 0.3, y: 4.3, w: colW - 0.6, h: 1.45, fontFace: "Calibri", fontSize: 12.5, color: INK, isTextBox: true, margin: 0 });
  }
  condCard(MARGIN, "おにぎり＋スムージー", "DAY8〜10（n=3日）", C_ONIGISMO, "8:00におにぎり2個＋果物ヨーグルト（スムージー）を同時摂取。\n11:00〜14:00の間にトレーニング。");
  condCard(MARGIN + colW + 0.4, "おにぎり＋糖質減", "DAY11〜13（n=3日）", C_LOWSUGAR, "8:00におにぎり2個＋果物ヨーグルト（糖質を減らしたスムージー）を同時摂取。\n11:00〜14:00の間にトレーニング。");

  addFooter(s, "測定：血糖値（15分間隔）、自覚コンディション（30分間隔アンケート）、毎晩のコンディションアプリ記録", false);
}

// ================= 実験2: 結果① 血糖推移 =================
glucoseChartSlide("EXPERIMENT 2 – RESULTS", "血糖値の推移（8:00〜14:00）",
  "おにぎり＋スムージー", "おにぎり＋糖質減",
  "15分間隔・条件ごとの平均血糖値（各条件3日間平均）。");

// ================= 実験2: 結果② 主要指標 =================
barPanelsSlide("EXPERIMENT 2 – RESULTS", "主要指標の比較",
  ["おにぎり+スムージー", "おにぎり+糖質減"], [C_ONIGISMO, C_LOWSUGAR],
  [
    { titleMain: "iAUC 2時間 (mg/dL・分)", titleSub: "ベースライン超過分の面積", values: [5230.0, 3167.5], fmt: "#,##0" },
    { titleMain: "Δピーク血糖値 (mg/dL)", titleSub: "最高値 − 摂取直前", values: [78.0, 84.3], fmt: "0.0" },
    { titleMain: "練習中(11-14h)平均血糖", titleSub: "mg/dL（燃料供給の目安）", values: [220.1, 229.4], fmt: "#,##0" },
  ],
  "糖質減はiAUC 2hを約39%削減。練習中の血糖水準は糖質減の方がむしろ高く、燃料供給は犠牲になっていない。");

// ================= 実験2: 結果③ 自覚コンディション + 夜間指標 =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "EXPERIMENT 2 – RESULTS", "自覚コンディション・夜間コンディション指標", false);

  s.addShape("roundRect", { x: MARGIN, y: 1.75, w: 5.85, h: 2.35, rectRadius: 0.1, fill: { color: CARDBG }, line: { type: "none" } });
  s.addText("食後アンケート（頭痛・吐き気）", { x: MARGIN + 0.25, y: 1.9, w: 5.4, h: 0.3, fontFace: "Calibri", fontSize: 13, bold: true, color: NAVY, isTextBox: true, margin: 0 });
  const giRows = [
    ["", "頭痛", "吐き気"],
    ["おにぎり＋スムージー", "1（変化なし）", "9:30のみ一時的に2"],
    ["おにぎり＋糖質減", "1（変化なし）", "1（変化なし）"],
  ];
  s.addTable(giRows.map((r, i) => i === 0
    ? r.map(c => ({ text: c, options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: 11 } }))
    : r.map((c, j) => ({ text: c, options: { color: INK, bold: j === 0, fontSize: 11.5, fill: { color: WHITE } } }))
  ), { x: MARGIN + 0.25, y: 2.25, w: 5.35, h: 1.1, fontFace: "Calibri", fontSize: 11.5, border: { type: "solid", color: "E3E1DB", pt: 0.75 }, autoPage: false, valign: "middle", rowH: 0.37, colW: [2.35, 1.5, 1.5] });
  s.addText("満腹感は同時摂取・糖質減の方が高くなる傾向（総摂取量の違い）だが、消化器症状は両条件とも軽微。", {
    x: MARGIN + 0.25, y: 3.55, w: 5.35, h: 0.5, fontFace: "Calibri", fontSize: 11, color: MUTED, isTextBox: true, margin: 0
  });

  const panelX = MARGIN + 6.25;
  s.addText("夜間コンディションアプリ記録（3日間平均）", { x: panelX, y: 1.9, w: 6.5, h: 0.3, fontFace: "Calibri", fontSize: 13, bold: true, color: NAVY, isTextBox: true, margin: 0 });
  const nightRows = [
    ["", "おにぎり+スムージー", "おにぎり+糖質減"],
    ["起床時コンディション", "2.33", "2.67"],
    ["睡眠の質", "2.00", "2.67"],
    ["RPE", "5.50", "6.33"],
    ["持久力", "3.83", "2.33"],
    ["爆発力", "3.50", "3.33"],
  ];
  s.addTable(nightRows.map((r, i) => i === 0
    ? r.map(c => ({ text: c, options: { bold: true, color: WHITE, fill: { color: NAVY }, fontSize: 11 } }))
    : r.map((c, j) => ({ text: c, options: { color: INK, bold: j === 0, fontSize: 11.5, fill: { color: i % 2 === 0 ? CARDBG : WHITE } } }))
  ), { x: panelX, y: 2.25, w: 6.5, h: 2.0, fontFace: "Calibri", fontSize: 10.5, border: { type: "solid", color: "E3E1DB", pt: 0.75 }, autoPage: false, valign: "middle", rowH: 0.33, colW: [2.7, 1.9, 1.9] });

  s.addShape("roundRect", { x: MARGIN, y: 4.35, w: W - MARGIN * 2, h: 2.15, rectRadius: 0.1, fill: { color: "FDF3E2" }, line: { color: "EDA100", width: 1 } });
  s.addText("⚠ 要注意の矛盾", { x: MARGIN + 0.3, y: 4.52, w: 6, h: 0.3, fontFace: "Calibri", fontSize: 13, bold: true, color: "6B4B00", isTextBox: true, margin: 0 });
  s.addText(
    "起床時コンディション・睡眠の質は糖質減の方が良いが、持久力・爆発力の自己評価は糖質減の方が低い。血糖の燃料供給（練習中平均血糖）は糖質減の方が高いため、この体感の低下が血糖以外の要因（練習内容そのものの負荷、n=3のばらつき等）による可能性がある。糖質減条件は練習時間も平均100分と、おにぎり＋スムージー条件（平均80分）よりやや長く、交絡の可能性も残る。",
    { x: MARGIN + 0.3, y: 4.88, w: W - MARGIN * 2 - 0.6, h: 1.55, fontFace: "Calibri", fontSize: 12, color: "6B4B00", isTextBox: true, margin: 0 }
  );
}

// ================= 実験2: 考察 =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "EXPERIMENT 2 – DISCUSSION", "実験2 考察", false);

  const points = [
    { t: "部分的液状化（同時摂取）は血糖の乱高下を抑制", d: "おにぎりを崩さず同時に摂取することで、副食単独（実験1・スムージー）よりΔピーク・CVが小さくなり、波形がなだらかになった。作業仮説を支持する結果。" },
    { t: "糖質量の最適化はiAUCを明確に削減", d: "副食の糖質を減らすことで、食後2時間の正味の血糖上昇（iAUC 2h）が約39%減少。ピークの高さは同水準だが、上昇の「持続」が抑えられている。" },
    { t: "燃料供給は犠牲になっていない", d: "練習中（11:00〜14:00）の平均血糖は糖質減の方がむしろ高く、血糖の観点からはパフォーマンスを犠牲にしていない。" },
    { t: "体感との矛盾は要検証", d: "一方で夜間記録では糖質減の日の持久力・爆発力の自己評価が最も低く、血糖データと矛盾する。練習内容・時間の交絡や n=3 のばらつきを含め、追加検証が必要。" },
  ];
  let y = 1.85;
  points.forEach((p, i) => {
    s.addShape("oval", { x: MARGIN, y, w: 0.42, h: 0.42, fill: { color: i === points.length - 1 ? "EDA100" : TEAL }, line: { type: "none" } });
    s.addText(String(i + 1), { x: MARGIN, y, w: 0.42, h: 0.42, align: "center", valign: "middle", fontFace: "Cambria", fontSize: 14, bold: true, color: WHITE, isTextBox: true, margin: 0 });
    s.addText(p.t, { x: MARGIN + 0.65, y: y - 0.03, w: 11.3, h: 0.32, fontFace: "Calibri", fontSize: 14, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    s.addText(p.d, { x: MARGIN + 0.65, y: y + 0.3, w: 11.3, h: 0.65, fontFace: "Calibri", fontSize: 12, color: MUTED, isTextBox: true, margin: 0 });
    y += 1.28;
  });
  addFooter(s, "✓ 実験2は両条件とも血糖ベースラインシフト後で条件が揃っており、この考察（①②③）は信頼できる（総合考察で後述）。", false);
}

// ================= 総合考察 Section divider =================
sectionDivider("GENERAL DISCUSSION", "総合考察", "実験1・実験2を横断し、摂取タイミングの効果と、アスリートにとっての血糖値の意味を考察する", "03");

// ================= 横断①: タイミングの効果 =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "CROSS-EXPERIMENT", "タイミングの効果：同時摂取 vs 分割摂取（同エネルギー条件下）", false);
  s.addText(
    "4条件とも14:00までの総エネルギーはほぼ同じ。「おにぎりを8:00に同時に食べるか、10:00〜11:00に分けて食べるか」の純粋な効果を、自由摂取前（8:00〜11:30）に絞って比較。",
    { x: MARGIN, y: 1.6, w: W - MARGIN * 2, h: 0.5, fontFace: "Calibri", fontSize: 12.5, color: MUTED, isTextBox: true, margin: 0 }
  );

  const rows2 = [
    [{ text: "条件", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "実験", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "平均血糖(8:00-11:30)", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "CV", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "Δピーク", options: { bold: true, color: WHITE, fill: { color: NAVY } } }],
    ["固形（分割）", "実験1", "119.9", "12.0%", "53.7"],
    ["スムージー（分割）", "実験1", "187.0", "16.5%", "80.3"],
    ["おにぎり＋スムージー（同時）", "実験2", "199.8", "10.1%", "70.7"],
    ["おにぎり＋糖質減（同時）", "実験2", "194.9", "8.5%", "52.3"],
  ].map((r, i) => i === 0 ? r : r.map((c, j) => ({
    text: c, options: { color: j === 0 ? NAVY : INK, bold: j === 0, fill: { color: i % 2 === 0 ? CARDBG : WHITE }, fontSize: 12.5 }
  })));
  s.addTable(rows2, {
    x: MARGIN, y: 2.2, w: W - MARGIN * 2, h: 2.0,
    fontFace: "Calibri", fontSize: 12.5, border: { type: "solid", color: "E3E1DB", pt: 0.75 },
    autoPage: false, valign: "middle", rowH: 0.4,
    colW: [3.6, 1.5, 2.8, 2.0, 2.23]
  });

  s.addShape("roundRect", { x: MARGIN, y: 4.5, w: W - MARGIN * 2, h: 2.3, rectRadius: 0.1, fill: { color: "EAF7F0" }, line: { type: "none" } });
  s.addText("✓ 同時摂取にすると平均血糖は少し上がるが、乱高下は明確に小さくなる", { x: MARGIN + 0.3, y: 4.68, w: W - MARGIN * 2 - 0.6, h: 0.35, fontFace: "Calibri", fontSize: 13.5, bold: true, color: "0F5C3D", isTextBox: true, margin: 0 });
  s.addText(
    "副食とおにぎりを2.5〜3時間ずらして食べる（実験1）と、それぞれが独立した急峻な山を作るのに対し、同時に食べる（実験2）とおにぎり（ゆっくり吸収されるデンプン）が副食の急な糖吸収を緩衝し、1つのなだらかな波にまとまると解釈できる。糖質減はこの「なだらかさ」に加えてΔピークも固形並み（52.3 vs 53.7）まで抑えられている。",
    { x: MARGIN + 0.3, y: 5.08, w: W - MARGIN * 2 - 0.6, h: 1.6, fontFace: "Calibri", fontSize: 12, color: "0F5C3D", isTextBox: true, margin: 0 }
  );
}

// ================= 横断②: アスリート視点 =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "CROSS-EXPERIMENT", "アスリート視点：血糖値は「リスク」か「燃料」か", false);
  s.addText(
    "問題は「血糖が高いこと」自体ではなく①食後低血圧②血糖スパイク＋反応性低血糖という急激な変化。乱高下なく高い水準を維持できるなら、それは燃料が豊富な望ましい状態とも言える。",
    { x: MARGIN, y: 1.6, w: W - MARGIN * 2, h: 0.5, fontFace: "Calibri", fontSize: 12, color: MUTED, isTextBox: true, margin: 0 }
  );

  const fuelConds = ["固形", "スムージー", "おにぎり+スムージー", "おにぎり+糖質減"];
  const fuelColors = [C_SOLID, C_SMOOTHIE, C_ONIGISMO, C_LOWSUGAR];
  const fuelPanelW = 5.8;
  function smallBarPanel(x, titleMain, titleSub, values, fmt) {
    s.addText(titleMain, { x, y: 2.15, w: fuelPanelW, h: 0.28, fontFace: "Calibri", fontSize: 12.5, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    s.addText(titleSub, { x, y: 2.43, w: fuelPanelW, h: 0.24, fontFace: "Calibri", fontSize: 10, color: MUTED, isTextBox: true, margin: 0 });
    s.addChart("bar", [{ name: titleMain, labels: fuelConds, values }], {
      x, y: 2.72, w: fuelPanelW, h: 2.15,
      barDir: "col",
      chartColors: fuelColors, chartColorsOpacity: 100,
      showTitle: false, showLegend: false,
      showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 10.5, dataLabelColor: INK,
      dataLabelFormatCode: fmt,
      catAxisLabelColor: MUTED, catAxisLabelFontSize: 9.5, catAxisLabelRotate: 20,
      valAxisHidden: true,
      catGridLine: { style: "none" }, valGridLine: { style: "none" },
      catAxisLineColor: "E3E1DB", valAxisLineColor: "E3E1DB",
      barGapWidthPct: 35
    });
  }
  smallBarPanel(MARGIN, "トレーニング時間帯(11:00-14:00)の平均血糖", "＝燃料供給 (mg/dL)", [135.1, 222.1, 220.1, 229.4], "#,##0");
  smallBarPanel(W - MARGIN - fuelPanelW, "ピーク後の最小値−ベースライン", "クラッシュ（反応性低血糖）の有無 (mg/dL)", [20.0, 47.7, 18.3, 47.7], "#,##0");

  s.addShape("roundRect", { x: MARGIN, y: 5.15, w: W - MARGIN * 2, h: 1.65, rectRadius: 0.1, fill: { color: "EAF7F0" }, line: { type: "none" } });
  const fuelNotes = [
    "クラッシュ（反応性低血糖）は4条件とも起きていない：ピーク後の最小値はベースラインを+18〜48上回る",
    "固形（実験1）は練習中の血糖が他条件の約6割（135 vs 220〜229）＝燃料不足の可能性",
    "糖質減（実験2）は練習中の血糖がむしろ4条件中最高。ただし持久力・爆発力の自己評価は最低という矛盾があり要検証",
  ];
  let fy = 5.32;
  fuelNotes.forEach(n => {
    s.addText("•  " + n, { x: MARGIN + 0.3, y: fy, w: W - MARGIN * 2 - 0.6, h: 0.45, fontFace: "Calibri", fontSize: 12, color: "0F5C3D", isTextBox: true, margin: 0 });
    fy += 0.48;
  });
}

// ================= 横断③: 新知見（血糖ベースラインシフト） =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "NEW FINDING", "新知見：血糖ベースラインの持続的シフト", false);
  s.addText("その後入手した14日間の連続CGMデータ（FreeStyleリブレ実測）により、実験1・実験2全体の解釈に関わる事実が判明した。", {
    x: MARGIN, y: 1.6, w: W - MARGIN * 2, h: 0.4, fontFace: "Calibri", fontSize: 12, color: MUTED, isTextBox: true, margin: 0
  });

  const dayLabels = ["準備", "DAY1", "DAY2", "DAY3", "DAY4", "DAY5", "DAY6", "DAY7", "DAY8", "DAY9", "DAY10", "DAY11", "DAY12", "DAY13", "DAY14"];
  const dayMeanAll = [141.2, 126.7, 117.6, 119.0, 126.0, 160.7, 208.9, 210.8, 196.0, 189.1, 191.0, 204.5, 187.3, 174.2, 184.2];
  s.addChart("line", [{ name: "終日平均血糖", labels: dayLabels, values: dayMeanAll }], {
    x: MARGIN, y: 2.0, w: W - MARGIN * 2, h: 2.35,
    chartColors: [C_SMOOTHIE],
    lineSize: 2.25, lineDataSymbol: "circle", lineDataSymbolSize: 4,
    showTitle: false, showLegend: false,
    catAxisLabelColor: MUTED, catAxisLabelFontSize: 9,
    valAxisLabelColor: MUTED, valAxisLabelFontSize: 9,
    valAxisTitle: "終日平均血糖(mg/dL)", showValAxisTitle: true, valAxisTitleFontSize: 9, valAxisTitleColor: MUTED,
    valGridLine: { color: "E3E1DB", size: 0.75 }, catGridLine: { style: "none" },
    catAxisLineColor: "E3E1DB", valAxisLineColor: "E3E1DB"
  });

  const rows = [
    [{ text: "対応する分析", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "シフトとの関係・信頼度", options: { bold: true, color: WHITE, fill: { color: NAVY } } }],
    ["実験1（固形 vs スムージー）", "⚠ スムージー(DAY4〜6)はDAY4・5がシフト前、DAY6のみシフト後。結論は参考値として扱う"],
    ["実験2（おにぎり+スムージー vs 糖質減）", "✓ 両条件(DAY8〜13)とも完全にシフト後で条件が揃っており、結論を維持できる"],
  ].map((r, i) => i === 0 ? r : r.map((c, j) => ({
    text: c, options: { color: j === 0 ? NAVY : (c.startsWith("✓") ? "0F5C3D" : "6B4B00"), bold: j === 0, fill: { color: i % 2 === 0 ? CARDBG : WHITE }, fontSize: 12 }
  })));
  s.addTable(rows, {
    x: MARGIN, y: 4.55, w: W - MARGIN * 2, h: 1.3,
    fontFace: "Calibri", fontSize: 12, border: { type: "solid", color: "E3E1DB", pt: 0.75 },
    autoPage: false, valign: "middle", rowH: 0.55,
    colW: [4.8, 7.93]
  });

  s.addShape("roundRect", { x: MARGIN, y: 6.05, w: W - MARGIN * 2, h: 1.05, rectRadius: 0.1, fill: { color: "FDF3E2" }, line: { color: "EDA100", width: 1 } });
  s.addText("DAY5(8/29)14:50頃、血糖が150→270台へ急上昇し以後戻らず（夜間平均93〜107→130〜177mg/dL）。原因不明だが低血糖は14日間通じて一度も検出されず。選手・スタッフへの聞き取りが最優先の次の一手。", {
    x: MARGIN + 0.25, y: 6.18, w: W - MARGIN * 2 - 0.5, h: 0.8, fontFace: "Calibri", fontSize: 11, bold: true, color: "6B4B00", isTextBox: true, margin: 0
  });
}

// ================= 総合考察まとめ =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "GENERAL DISCUSSION", "総合考察まとめ", false);

  s.addShape("roundRect", { x: MARGIN, y: 1.75, w: W - MARGIN * 2, h: 1.55, rectRadius: 0.12, fill: { color: "FDF3E2" }, line: { color: "EDA100", width: 1 } });
  s.addText("⚠ 重要な交絡：練習時間が条件ブロックごとに大きく異なる", { x: MARGIN + 0.3, y: 1.9, w: W - MARGIN * 2 - 0.6, h: 0.3, fontFace: "Calibri", fontSize: 13, bold: true, color: "6B4B00", isTextBox: true, margin: 0 });
  s.addText(
    "実験1・固形の3日間は平均140分と突出して長く、実験1・スムージーの3日間は毎日60分で最短。RPE・爆発力・持久力・運動後疲労は運動量そのものにも左右されるため、この差を切り分けられていない点は最大の限界。",
    { x: MARGIN + 0.3, y: 2.24, w: W - MARGIN * 2 - 0.6, h: 1.0, fontFace: "Calibri", fontSize: 11.5, color: "6B4B00", isTextBox: true, margin: 0 }
  );

  const colW = (W - MARGIN * 2 - 0.4) / 2;
  function tradeCard(x, title, color, lines) {
    s.addShape("roundRect", { x, y: 3.5, w: colW, h: 2.0, rectRadius: 0.1, fill: { color: CARDBG }, line: { type: "none" } });
    s.addShape("rect", { x: x + 0.3, y: 3.65, w: 0.16, h: 0.38, fill: { color }, line: { type: "none" } });
    s.addText(title, { x: x + 0.58, y: 3.61, w: colW - 0.9, h: 0.46, fontFace: "Calibri", fontSize: 14, bold: true, color: NAVY, isTextBox: true, margin: 0, valign: "middle" });
    let ly = 4.15;
    lines.forEach(l => {
      s.addText("•  " + l, { x: x + 0.3, y: ly, w: colW - 0.6, h: 0.38, fontFace: "Calibri", fontSize: 11, color: INK, isTextBox: true, margin: 0 });
      ly += 0.42;
    });
  }
  tradeCard(MARGIN, "おにぎり＋スムージー（糖質ノーマル）", C_ONIGISMO, [
    "血糖の乱高下（CV）が4条件中最小、練習中の燃料供給も十分（220）",
    "持久力の自己評価が4条件中最高（3.83）",
    "消化器症状も軽微"
  ]);
  tradeCard(MARGIN + colW + 0.4, "おにぎり＋糖質減", C_LOWSUGAR, [
    "波形が最もなだらか、練習中の燃料供給はむしろ4条件中最高（229）",
    "起床時コンディション・睡眠の質が4条件中最高",
    "一方で持久力・爆発力の自己評価は4条件中最低（要検証の矛盾）"
  ]);

  s.addShape("roundRect", { x: MARGIN, y: 5.7, w: W - MARGIN * 2, h: 1.3, rectRadius: 0.1, fill: { color: "EAF7F0" }, line: { type: "none" } });
  s.addText(
    "✓ 総合評価：現時点のデータでは「おにぎり＋スムージー（糖質ノーマル、同時摂取）」が最もバランスの良い候補。「おにぎり＋糖質減」は血糖面ではむしろ優れており、体感との矛盾を解消できれば第一候補に上がる可能性もある。",
    { x: MARGIN + 0.3, y: 5.9, w: W - MARGIN * 2 - 0.6, h: 0.95, fontFace: "Calibri", fontSize: 12.5, bold: true, color: "0F5C3D", isTextBox: true, margin: 0 }
  );
}

// ================= 結論 =================
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  titleBlock(s, "CONCLUSION", "結論", true);

  const concl = [
    "実験1：副食のみの液状化は血糖の乱高下をむしろ悪化させるが、消化器症状には差がない（⚠血糖ベースラインシフトの影響下にあり参考値）",
    "実験2：おにぎりと副食を同時摂取する「部分的液状化」は血糖の乱高下を抑制し、糖質量の最適化でさらに改善する（✓シフト後で条件が揃い信頼できる）",
    "アスリート視点では、固形は「安定」ではなく「練習中の燃料不足」と解釈すべきで、おにぎり＋スムージー（同時摂取）が乱高下抑制と燃料供給を両立する最もバランスの良い候補",
  ];
  let y = 1.9;
  concl.forEach((c, i) => {
    s.addShape("oval", { x: MARGIN, y, w: 0.42, h: 0.42, fill: { color: "1C7293" }, line: { type: "none" } });
    s.addText(String(i + 1), { x: MARGIN, y, w: 0.42, h: 0.42, align: "center", valign: "middle", fontFace: "Cambria", fontSize: 14, bold: true, color: WHITE, isTextBox: true, margin: 0 });
    s.addText(c, { x: MARGIN + 0.65, y: y - 0.02, w: 11.3, h: 0.85, fontFace: "Calibri", fontSize: 14, color: "E8EDF7", isTextBox: true, margin: 0, valign: "middle" });
    y += 1.15;
  });
  addFooter(s, "データ出典：for_AI_.xlsx／0824スケジュール.xlsx／condition_app_2026-08-25_2026-09-07.xlsx／14日間_for_AI.xlsx", true);
}

// ================= 今後の課題 =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "FUTURE WORK", "今後の課題", false);

  const next = [
    { t: "【最優先】血糖ベースラインシフトの原因究明", d: "14日間CGMで判明したDAY5(8/29)14:50頃からの持続的シフトの原因を、選手・スタッフへの聞き取り（補食・体調・ストレスの有無）で確認する。コスト0で最大の手がかりが得られる。" },
    { t: "練習量の統制", d: "練習時間が条件ブロックごとに大きく異なる（60〜180分）。練習内容・時間を条件間で揃えて再検証すると、食事の純粋な効果を評価しやすくなる。" },
    { t: "糖質減条件の矛盾の解消", d: "血糖の燃料供給は良好なのに持久力・爆発力の体感が低いという矛盾を解消するため、乳酸値やパワーメーターなど血糖以外の直接的なパフォーマンス指標の取得を検討したい。" },
    { t: "サンプルサイズの拡大", d: "各条件n=3日・単一被験者のため、複数選手・複数週にわたる追試により結果の頑健性を高める必要がある。" },
  ];
  let y = 1.85;
  next.forEach((p, i) => {
    s.addShape("oval", { x: MARGIN, y: y, w: 0.5, h: 0.5, fill: { color: DEEPBLUE }, line: { type: "none" } });
    s.addText(String(i + 1), { x: MARGIN, y: y, w: 0.5, h: 0.5, align: "center", valign: "middle", fontFace: "Cambria", fontSize: 16, bold: true, color: WHITE, isTextBox: true, margin: 0 });
    s.addText(p.t, { x: MARGIN + 0.75, y: y - 0.02, w: 10.9, h: 0.35, fontFace: "Calibri", fontSize: 14.5, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    s.addText(p.d, { x: MARGIN + 0.75, y: y + 0.34, w: 10.9, h: 0.6, fontFace: "Calibri", fontSize: 12, color: MUTED, isTextBox: true, margin: 0 });
    y += 1.25;
  });
}

// ================= おわりに =================
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addShape("rect", { x: 0, y: 0, w: W, h: H, fill: { color: NAVY } });
  s.addShape("oval", { x: -2.0, y: 4.6, w: 4.6, h: 4.6, fill: { color: TEAL, transparency: 60 }, line: { type: "none" } });
  s.addText("ご清聴ありがとうございました", {
    x: MARGIN, y: 3.2, w: W - MARGIN * 2, h: 1.0, align: "center", fontFace: "Cambria", fontSize: 34, bold: true, color: WHITE, isTextBox: true
  });
  s.addText("ご質問・ご指摘をお願いいたします", {
    x: MARGIN, y: 4.1, w: W - MARGIN * 2, h: 0.5, align: "center", fontFace: "Calibri", fontSize: 16, color: "CADCFC", isTextBox: true
  });
}

pres.writeFile({ fileName: "output_thesis.pptx" }).then(() => console.log("done"));
