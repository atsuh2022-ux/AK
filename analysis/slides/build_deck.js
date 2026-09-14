const pptxgen = require("pptxgenjs");

// ---- palette ----
const NAVY = "21295C";
const DEEPBLUE = "065A82";
const TEAL = "1C7293";
const WHITE = "FFFFFF";
const INK = "1A1A1A";
const MUTED = "5C6570";
const CARDBG = "F4F7F9";

// condition colors (kept consistent with the glucose chart shown earlier)
const C_SOLID = "2A78D6";      // 固形
const C_SMOOTHIE = "EB6834";   // スムージー
const C_ONIGISMO = "1BAF7A";   // おにぎり+スムージー
const C_LOWSUGAR = "EDA100";   // 糖質減

const times = ["08:00","08:15","08:30","08:45","09:00","09:15","09:30","09:45","10:00","10:15","10:30","10:45","11:00","11:15","11:30","11:45","12:00","12:15","12:30","12:45","13:00","13:15","13:30","13:45","14:00"];
const hourlyLabels = times.map(t => (t.endsWith(":00") ? t : ""));

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
    fontFace: "Cambria", fontSize: 28, bold: true, color: dark ? WHITE : NAVY,
    isTextBox: true
  });
}

// ================= Slide 1: Title =================
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addShape("rect", { x: 0, y: 0, w: W, h: H, fill: { color: NAVY } });
  s.addShape("oval", { x: 10.6, y: -1.6, w: 5.5, h: 5.5, fill: { color: DEEPBLUE, transparency: 55 }, line: { type: "none" } });
  s.addShape("oval", { x: -2.0, y: 4.6, w: 4.6, h: 4.6, fill: { color: TEAL, transparency: 60 }, line: { type: "none" } });

  s.addText("SCI車いす選手 食事介入研究", {
    x: MARGIN, y: 2.05, w: 10.5, h: 0.5, fontFace: "Calibri", fontSize: 15, bold: true,
    color: "8FB7E0", charSpacing: 1.5, isTextBox: true
  });
  s.addText("おにぎり × スムージー 部分的液状化研究", {
    x: MARGIN, y: 2.55, w: 11.5, h: 1.3, fontFace: "Cambria", fontSize: 40, bold: true,
    color: WHITE, isTextBox: true
  });
  s.addText("血糖値・コンディション比較分析", {
    x: MARGIN, y: 3.55, w: 11.5, h: 0.6, fontFace: "Calibri", fontSize: 20,
    color: "CADCFC", isTextBox: true
  });

  s.addShape("line", { x: MARGIN, y: 4.5, w: 0, h: 0, line: { type: "none" } }); // noop spacer (avoid accent-line pattern elsewhere)

  const stats = [
    ["4", "比較条件"],
    ["14", "測定日数(DAY)"],
    ["25", "血糖測定点/日"],
  ];
  let sx = MARGIN;
  stats.forEach(([n, l]) => {
    s.addText(n, { x: sx, y: 5.35, w: 1.6, h: 0.7, fontFace: "Cambria", fontSize: 34, bold: true, color: WHITE, isTextBox: true, margin: 0 });
    s.addText(l, { x: sx, y: 6.05, w: 2.6, h: 0.4, fontFace: "Calibri", fontSize: 12, color: "9AA6C4", isTextBox: true, margin: 0 });
    sx += 2.0;
  });

  s.addText("高位脊髄損傷（SCI）車いす陸上選手 1名を対象とした反復測定", {
    x: MARGIN, y: 6.75, w: 9, h: 0.4, fontFace: "Calibri", fontSize: 11, italic: true, color: "9AA6C4", isTextBox: true
  });
}

// ================= Slide 2: Background =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "BACKGROUND", "研究の背景と目的", false);

  const items = [
    { n: "1", t: "SCI選手の病態生理", d: "高位脊髄損傷者は交感神経の遠心路が遮断され、食後低血圧・血糖値スパイク／反応性低血糖を起こしやすい。" },
    { n: "2", t: "現場での気づき", d: "「おにぎり2個＋バナナ＆ヨーグルト」の副食をスムージー化したところ、練習時の出力が劇的に向上したとの報告。" },
    { n: "3", t: "作業仮説", d: "おにぎりの満足感は残しつつ副食を部分的に液状化し、総固形物量を減らすことで胃排泄を促し、血糖・消化ストレスを回避できるのでは。" },
    { n: "4", t: "本分析の目的", d: "4条件（固形／スムージー／おにぎり＋スムージー／糖質減食）で血糖動態と自覚コンディションへの影響を比較検証する。" },
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

// ================= Slide 3: Method / schedule =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "METHOD", "4条件の摂取スケジュール", false);

  const rows = [
    [{ text: "条件", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "日程", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "8:00の食事内容", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "おにぎりのタイミング", options: { bold: true, color: WHITE, fill: { color: NAVY } } }],
    ["固形摂取", "DAY1〜3", "果物ヨーグルト（固形）のみ", "約2.5〜3時間後"],
    ["スムージー摂取", "DAY4〜6", "果物ヨーグルト（スムージー）のみ", "約2.5〜3時間後"],
    ["おにぎり＋スムージー", "DAY8〜10", "おにぎり＋スムージー（同時）", "8:00に同時摂取"],
    ["おにぎり＋糖質減", "DAY11〜13", "おにぎり＋スムージー糖質減（同時）", "8:00に同時摂取"],
  ].map((r, i) => i === 0 ? r : r.map((c, j) => ({
    text: c, options: { color: j === 0 ? NAVY : INK, bold: j === 0, fill: { color: i % 2 === 0 ? CARDBG : WHITE }, fontSize: 12.5 }
  })));

  s.addTable(rows, {
    x: MARGIN, y: 1.85, w: W - MARGIN * 2, h: 2.5,
    fontFace: "Calibri", fontSize: 12.5, border: { type: "solid", color: "E3E1DB", pt: 0.75 },
    autoPage: false, valign: "middle", rowH: 0.5,
    colW: [2.6, 1.25, 5.2, 3.08]
  });

  s.addShape("roundRect", { x: MARGIN, y: 4.75, w: W - MARGIN * 2, h: 1.85, rectRadius: 0.12, fill: { color: "FDF3E2" }, line: { color: "EDA100", width: 1 } });
  s.addText("⚠ 重要な注意点", { x: MARGIN + 0.3, y: 4.92, w: 6, h: 0.35, fontFace: "Calibri", fontSize: 13, bold: true, color: "6B4B00", isTextBox: true, margin: 0 });
  s.addText(
    "固形・スムージー条件は「副食のみを先に食べ、おにぎりは約2.5〜3時間後」、おにぎり＋スムージー・糖質減条件は「おにぎりと副食を同時摂取」という異なるプロトコル。4条件は形態とタイミングが同時に変わるため、純粋な形態比較ができるのは「固形 vs スムージー（副食のみ）」に限られる。トレーニングはどの条件も11:00〜14:00の間に実施（1日60〜180分、条件ブロックにより変動）。",
    { x: MARGIN + 0.3, y: 5.32, w: W - MARGIN * 2 - 0.6, h: 1.2, fontFace: "Calibri", fontSize: 12, color: "6B4B00", isTextBox: true, margin: 0 }
  );
  addFooter(s, "n = 3日／条件（同一選手の反復測定）。12:00以降は自由摂取。", false);
}

// ================= Slide 3.5: Experimental design timeline =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "METHOD", "実験デザイン（1日のタイムライン）", false);

  const rowDefs = [
    { label: "固形摂取", sub: "DAY1〜3", color: C_SOLID,
      breakfast: "果物ヨーグルト（固形）", onigiriLater: true },
    { label: "スムージー摂取", sub: "DAY4〜6", color: C_SMOOTHIE,
      breakfast: "果物ヨーグルト（スムージー）", onigiriLater: true },
    { label: "おにぎり＋スムージー", sub: "DAY8〜10", color: C_ONIGISMO,
      breakfast: "おにぎり＋スムージー（同時）", onigiriLater: false },
    { label: "おにぎり＋糖質減", sub: "DAY11〜13", color: C_LOWSUGAR,
      breakfast: "おにぎり＋スムージー糖質減（同時）", onigiriLater: false },
  ];

  const TL_X0 = MARGIN + 2.35, TL_X1 = W - MARGIN - 0.1;
  const TL_W = TL_X1 - TL_X0;
  const H0 = 8, H1 = 20; // 8:00 - 20:00
  const hourToX = h => TL_X0 + ((h - H0) / (H1 - H0)) * TL_W;

  // hour axis ticks (top)
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

    s.addText(r.label, { x: MARGIN, y: y + 0.06, w: 2.05, h: 0.32, fontFace: "Calibri", fontSize: 12, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    s.addText(r.sub, { x: MARGIN, y: y + 0.36, w: 2.05, h: 0.26, fontFace: "Calibri", fontSize: 9.5, color: MUTED, isTextBox: true, margin: 0 });

    // baseline
    s.addShape("line", { x: TL_X0, y: barY + barH / 2, w: TL_W, h: 0, line: { color: "E3E1DB", width: 1 } });

    // 8:00 breakfast marker
    const bx = hourToX(8);
    s.addShape("roundRect", { x: bx, y: barY, w: 0.55, h: barH, rectRadius: 0.05, fill: { color: r.color }, line: { type: "none" } });
    s.addText(r.breakfast, { x: bx - 0.1, y: barY - 0.28, w: 3.4, h: 0.26, fontFace: "Calibri", fontSize: 8.5, color: r.color, bold: true, isTextBox: true, margin: 0 });

    // onigiri-later marker for 固形/スムージー
    if (r.onigiriLater) {
      const ox = hourToX(10.5);
      s.addShape("oval", { x: ox - 0.06, y: barY + barH / 2 - 0.06, w: 0.12, h: 0.12, fill: { color: r.color }, line: { color: WHITE, width: 1 } });
      s.addText("おにぎり摂取", { x: ox - 0.55, y: barY + barH + 0.03, w: 1.3, h: 0.22, align: "center", fontFace: "Calibri", fontSize: 8, color: r.color, isTextBox: true, margin: 0 });
    }

    // shared training window 11:00-14:00
    const tx0 = hourToX(11), tx1 = hourToX(14);
    s.addShape("roundRect", { x: tx0, y: barY, w: tx1 - tx0, h: barH, rectRadius: 0.05, fill: { color: NAVY, transparency: 25 }, line: { type: "none" } });

    // 20:00 dinner marker
    const dx = hourToX(20);
    s.addShape("oval", { x: dx - 0.055, y: barY + barH / 2 - 0.055, w: 0.11, h: 0.11, fill: { color: MUTED }, line: { type: "none" } });
  });

  // legend / annotation for training block + dinner marker
  s.addShape("roundRect", { x: MARGIN, y: rowTop0 + rowDefs.length * rowH + 0.15, w: 0.3, h: 0.16, rectRadius: 0.04, fill: { color: NAVY, transparency: 25 }, line: { type: "none" } });
  s.addText("トレーニング（60〜180分、11:00〜14:00の間で実施）", { x: MARGIN + 0.38, y: rowTop0 + rowDefs.length * rowH + 0.06, w: 5.5, h: 0.32, fontFace: "Calibri", fontSize: 10, color: INK, isTextBox: true, margin: 0 });
  s.addShape("oval", { x: MARGIN + 6.3, y: rowTop0 + rowDefs.length * rowH + 0.18, w: 0.11, h: 0.11, fill: { color: MUTED }, line: { type: "none" } });
  s.addText("20:00 夕食＋夜のコンディション記録（毎日共通）", { x: MARGIN + 6.55, y: rowTop0 + rowDefs.length * rowH + 0.06, w: 5.5, h: 0.32, fontFace: "Calibri", fontSize: 10, color: INK, isTextBox: true, margin: 0 });

  addFooter(s, "色付きブロック＝朝の被験食摂取（8:00）。固形・スムージー条件はおにぎりを約2.5時間後に別途摂取。灰色帯＝全条件共通のトレーニング時間帯。", false);
}

// ================= Slide 4: Glucose curve =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "RESULTS", "血糖値の推移（8:00〜14:00）", false);

  const chartData = Object.keys(glucose).map((k, i) => ({
    name: k,
    labels: times,
    values: glucose[k]
  }));
  const chartColors = [C_SOLID, C_SMOOTHIE, C_ONIGISMO, C_LOWSUGAR];

  s.addChart("line", chartData, {
    x: MARGIN, y: 1.75, w: W - MARGIN * 2, h: 4.55,
    chartColors: chartColors,
    lineSize: 2.5, lineDataSymbol: "none",
    showTitle: false,
    showLegend: true, legendPos: "b", legendFontSize: 12, legendColor: INK,
    catAxisLabelColor: MUTED, catAxisLabelFontSize: 10,
    valAxisLabelColor: MUTED, valAxisLabelFontSize: 10,
    valAxisTitle: "血糖値 (mg/dL)", showValAxisTitle: true, valAxisTitleFontSize: 11, valAxisTitleColor: MUTED,
    valGridLine: { color: "E3E1DB", size: 0.75 },
    catGridLine: { style: "none" },
    catAxisLineColor: "E3E1DB", valAxisLineColor: "E3E1DB",
    catAxisLabelRotate: 0,
    // thin out category labels to hour marks only
    catAxisLabelFrequency: 4,
    dataLabelColor: INK
  });
  addFooter(s, "15分間隔・条件ごとの平均血糖値（各条件3日間平均）。", false);
}

// ================= Slide 5: Key metrics bar charts =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "RESULTS", "主要指標の比較", false);

  const conds = ["固形", "スムージー", "おにぎり+スムージー", "おにぎり+糖質減"];
  const chartColors = [C_SOLID, C_SMOOTHIE, C_ONIGISMO, C_LOWSUGAR];

  const deltaPeak = [53.7, 85.0, 78.0, 84.3];
  const iauc2h = [1807.5, 1625.0, 5230.0, 3167.5];
  const cv = [11.2, 14.7, 10.1, 11.8];

  function barPanel(x, titleMain, titleSub, values, unit) {
    s.addText(titleMain, { x, y: 1.72, w: 3.75, h: 0.3, fontFace: "Calibri", fontSize: 13, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    s.addText(titleSub, { x, y: 2.0, w: 3.75, h: 0.28, fontFace: "Calibri", fontSize: 10.5, color: MUTED, isTextBox: true, margin: 0 });
    s.addChart("bar", [{ name: titleMain, labels: conds, values }], {
      x, y: 2.35, w: 3.75, h: 3.65,
      barDir: "col",
      chartColors: chartColors,
      chartColorsOpacity: 100,
      showTitle: false,
      showLegend: false,
      showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 10.5, dataLabelColor: INK,
      dataLabelFormatCode: unit === "%" ? "0.0" : "#,##0",
      catAxisLabelColor: MUTED, catAxisLabelFontSize: 9.5, catAxisLabelRotate: 20,
      valAxisHidden: true,
      catGridLine: { style: "none" }, valGridLine: { style: "none" },
      catAxisLineColor: "E3E1DB", valAxisLineColor: "E3E1DB",
      barGapWidthPct: 40
    });
  }

  barPanel(MARGIN, "Δピーク血糖値 (mg/dL)", "最高値 − 摂取直前", deltaPeak, "");
  barPanel(MARGIN + 4.15, "iAUC 2時間 (mg/dL・分)", "ベースライン超過分の面積", iauc2h, "");
  barPanel(MARGIN + 8.3, "変動係数 CV (%)", "6時間の値の乱高下", cv, "%");

  addFooter(s, "iAUC = incremental AUC（ベースライン超過分のみを積算した正味の食後上昇量）。", false);
}

// ================= Slide 6: Comparison 1 =================
function comparisonSlide(kicker, title, leftLabel, leftColor, leftStats, rightLabel, rightColor, rightStats, insight) {
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, kicker, title, false);

  const colW = (W - MARGIN * 2 - 0.4) / 2;
  function card(x, label, color, stats) {
    s.addShape("roundRect", { x, y: 1.85, w: colW, h: 2.9, rectRadius: 0.1, fill: { color: CARDBG }, line: { type: "none" } });
    s.addShape("rect", { x: x + 0.35, y: 2.1, w: 0.16, h: 0.5, fill: { color }, line: { type: "none" } });
    s.addText(label, { x: x + 0.65, y: 2.05, w: colW - 1.0, h: 0.55, fontFace: "Calibri", fontSize: 16, bold: true, color: NAVY, isTextBox: true, margin: 0, valign: "middle" });
    let sy = 2.8;
    stats.forEach(([v, l]) => {
      s.addText(v, { x: x + 0.35, y: sy, w: colW - 0.7, h: 0.55, fontFace: "Cambria", fontSize: 26, bold: true, color, isTextBox: true, margin: 0 });
      s.addText(l, { x: x + 0.35, y: sy + 0.5, w: colW - 0.7, h: 0.35, fontFace: "Calibri", fontSize: 11, color: MUTED, isTextBox: true, margin: 0 });
      sy += 0.87;
    });
  }
  card(MARGIN, leftLabel, leftColor, leftStats);
  card(MARGIN + colW + 0.4, rightLabel, rightColor, rightStats);

  s.addShape("roundRect", { x: MARGIN, y: 5.0, w: W - MARGIN * 2, h: 1.65, rectRadius: 0.1, fill: { color: "EAF7F0" }, line: { type: "none" } });
  s.addText("考察", { x: MARGIN + 0.3, y: 5.15, w: 3, h: 0.3, fontFace: "Calibri", fontSize: 12, bold: true, color: "0F5C3D", isTextBox: true, margin: 0 });
  s.addText(insight, { x: MARGIN + 0.3, y: 5.48, w: W - MARGIN * 2 - 0.6, h: 1.05, fontFace: "Calibri", fontSize: 12.5, color: INK, isTextBox: true, margin: 0 });

  return s;
}

comparisonSlide(
  "COMPARISON 1", "スムージー vs 固形（副食のみ・純粋比較）",
  "固形摂取", C_SOLID, [["53.7 mg/dL", "Δピーク血糖値"], ["11.2%", "変動係数 CV"]],
  "スムージー摂取", C_SMOOTHIE, [["85.0 mg/dL", "Δピーク血糖値（1.6倍）"], ["14.7%", "変動係数 CV"]],
  "副食を液状化するだけで血糖の上昇幅・乱高下は明確に増大。液状化は消化の負担感を下げる一方、血糖の安定には必ずしも寄与しない可能性がある。選手の「出力向上」の体感は、血糖の安定ではなく消化器系の負担軽減（内臓への血流集中の緩和）による可能性が高い。"
);

comparisonSlide(
  "COMPARISON 2", "スムージー vs おにぎり＋スムージー",
  "スムージー摂取", C_SMOOTHIE, [["85.0 mg/dL", "Δピーク血糖値"], ["14.7%", "変動係数 CV"]],
  "おにぎり＋スムージー", C_ONIGISMO, [["78.0 mg/dL", "Δピーク血糖値"], ["10.1%", "変動係数 CV（最小）"]],
  "おにぎりを同時摂取した方がΔピーク・CVともに小さい。おにぎり（固形デンプン）が副食の急激な糖吸収を緩衝し、波形がなだらかになっている可能性がある。総摂取糖質量は増えるが（iAUC絶対値は上昇）、研究背景の「総固形物量の調整による血糖・消化ストレス緩和」仮説を支持する結果。"
);

comparisonSlide(
  "COMPARISON 3", "おにぎり＋スムージー vs おにぎり＋糖質減",
  "おにぎり＋スムージー", C_ONIGISMO, [["5,230", "iAUC 2h (mg/dL・分)"], ["242.3 mg/dL", "ピーク血糖値"]],
  "おにぎり＋糖質減", C_LOWSUGAR, [["3,168 (▼39%)", "iAUC 2h (mg/dL・分)"], ["250.3 mg/dL", "ピーク血糖値（同水準）"]],
  "研究目的に最も近い比較。糖質を減らすことで食後2時間の正味の血糖上昇（iAUC）が約39%減少。ピーク自体の高さはほぼ同水準だが、上昇の「持続・面積」＝体への負荷は明確に小さい。おにぎりの満足感を保ちながら総糖質量を最適化する方針はデータ上も支持される。"
);

// ================= Slide: Timing effect (same-energy comparison) =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "COMPARISON 5", "タイミングの効果：同時摂取 vs 分割摂取（同エネルギー条件下）", false);
  s.addText(
    "4条件とも14:00までの総エネルギーはほぼ同じ。「おにぎりを8:00に同時に食べるか、10:00〜11:00に分けて食べるか」の純粋な効果を、自由摂取前（8:00〜11:30）に絞って比較。",
    { x: MARGIN, y: 1.6, w: W - MARGIN * 2, h: 0.5, fontFace: "Calibri", fontSize: 12.5, color: MUTED, isTextBox: true, margin: 0 }
  );

  const rows2 = [
    [{ text: "条件", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "平均血糖(8:00-11:30)", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "CV", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "Δピーク", options: { bold: true, color: WHITE, fill: { color: NAVY } } }],
    ["固形（分割・全て固形）", "119.9", "12.0%", "53.7"],
    ["スムージー（分割）", "187.0", "16.5%", "80.3"],
    ["おにぎり＋スムージー（同時）", "199.8", "10.1%", "70.7"],
    ["おにぎり＋糖質減（同時）", "194.9", "8.5%", "52.3"],
  ].map((r, i) => i === 0 ? r : r.map((c, j) => ({
    text: c, options: { color: j === 0 ? NAVY : INK, bold: j === 0, fill: { color: i % 2 === 0 ? CARDBG : WHITE }, fontSize: 13 }
  })));
  s.addTable(rows2, {
    x: MARGIN, y: 2.2, w: W - MARGIN * 2, h: 2.0,
    fontFace: "Calibri", fontSize: 13, border: { type: "solid", color: "E3E1DB", pt: 0.75 },
    autoPage: false, valign: "middle", rowH: 0.4,
    colW: [4.4, 3.0, 2.4, 2.33]
  });

  s.addShape("roundRect", { x: MARGIN, y: 4.5, w: W - MARGIN * 2, h: 2.3, rectRadius: 0.1, fill: { color: "EAF7F0" }, line: { type: "none" } });
  s.addText("✓ 同時摂取にすると平均血糖は少し上がるが、乱高下は明確に小さくなる", { x: MARGIN + 0.3, y: 4.68, w: W - MARGIN * 2 - 0.6, h: 0.35, fontFace: "Calibri", fontSize: 13.5, bold: true, color: "0F5C3D", isTextBox: true, margin: 0 });
  s.addText(
    "副食とおにぎりを2.5〜3時間ずらして食べると、それぞれが独立した急峻な山を作るのに対し、同時に食べるとおにぎり（ゆっくり吸収されるデンプン）が副食の急な糖吸収を緩衝し、1つのなだらかな波にまとまると解釈できる。糖質減はこの「なだらかさ」に加えてΔピークも固形並み（52.3 vs 53.7）まで抑えられている。絶対値が最も低いのは固形で、これは「同時摂取か否か」ではなく「副食が固形かスムージーか」という形態の効果。",
    { x: MARGIN + 0.3, y: 5.08, w: W - MARGIN * 2 - 0.6, h: 1.6, fontFace: "Calibri", fontSize: 12, color: "0F5C3D", isTextBox: true, margin: 0 }
  );
}

// ================= Slide: Athlete fuel perspective =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "PERSPECTIVE", "アスリート視点：血糖値は「リスク」か「燃料」か", false);
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
      chartColors: fuelColors,
      chartColorsOpacity: 100,
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
    "固形は候補から外れる：練習中の血糖が他条件の約6割（135 vs 220〜229）＝燃料不足の可能性",
    "糖質減は練習中の血糖がむしろ4条件中最高。ただし持久力・爆発力の自己評価は最低という矛盾があり要検証",
  ];
  let fy = 5.32;
  fuelNotes.forEach(n => {
    s.addText("•  " + n, { x: MARGIN + 0.3, y: fy, w: W - MARGIN * 2 - 0.6, h: 0.45, fontFace: "Calibri", fontSize: 12, color: "0F5C3D", isTextBox: true, margin: 0 });
    fy += 0.48;
  });
}

// ================= Slide 9: Condition survey =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "CONDITION", "自覚コンディション（4条件比較）", false);

  const condTimes = ["8:00", "8:30", "9:00", "9:30", "10:00"];
  const condConds = ["固形", "スムージー", "おにぎり+スムージー", "おにぎり+糖質減"];
  const condColors = [C_SOLID, C_SMOOTHIE, C_ONIGISMO, C_LOWSUGAR];

  const fullness = [
    [1.67, 4.00, 4.00, 2.00, 2.00],
    [3.33, 3.67, 5.00, 2.00, 1.33],
    [2.33, 7.67, 5.33, 5.50, 3.33],
    [1.67, 9.00, 8.00, 5.50, 4.67],
  ];
  const appetite = [
    [7.67, 8.00, 7.00, 7.67, 7.67],
    [8.67, 6.33, 5.50, 7.67, 8.67],
    [7.00, 3.67, 5.33, 5.50, 5.67],
    [9.00, 3.33, 3.00, 4.50, 5.33],
  ];

  function condChart(y, title, values) {
    s.addText(title, { x: MARGIN, y, w: 6.9, h: 0.28, fontFace: "Calibri", fontSize: 12.5, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    s.addChart("line", condConds.map((c, i) => ({ name: c, labels: condTimes, values: values[i] })), {
      x: MARGIN, y: y + 0.3, w: 6.9, h: 1.85,
      chartColors: condColors,
      lineSize: 2, lineDataSymbol: "circle", lineDataSymbolSize: 5,
      showTitle: false, showLegend: false,
      catAxisLabelColor: MUTED, catAxisLabelFontSize: 9.5,
      valAxisLabelColor: MUTED, valAxisLabelFontSize: 9.5,
      valAxisMinVal: 0, valAxisMaxVal: 10,
      valGridLine: { color: "E3E1DB", size: 0.75 },
      catGridLine: { style: "none" },
      catAxisLineColor: "E3E1DB", valAxisLineColor: "E3E1DB"
    });
  }
  condChart(1.75, "満腹感の推移 (0=空腹〜10=満腹)", fullness);
  condChart(4.05, "食欲(摂食可能感)の推移 (0=食べられない〜10=まだ食べられる)", appetite);

  // shared legend
  let lx = MARGIN;
  condConds.forEach((c, i) => {
    s.addShape("rect", { x: lx, y: 6.42, w: 0.16, h: 0.13, fill: { color: condColors[i] }, line: { type: "none" } });
    s.addText(c, { x: lx + 0.22, y: 6.30, w: 1.7, h: 0.3, fontFace: "Calibri", fontSize: 9.5, color: MUTED, isTextBox: true, margin: 0 });
    lx += 1.78;
  });

  s.addShape("roundRect", { x: 8.35, y: 1.75, w: 4.38, h: 4.85, rectRadius: 0.1, fill: { color: "EAF7F0" }, line: { type: "none" } });
  s.addText("✓ 消化器症状は4条件とも良好", { x: 8.65, y: 2.0, w: 3.9, h: 0.4, fontFace: "Calibri", fontSize: 13.5, bold: true, color: "0F5C3D", isTextBox: true, margin: 0 });
  const notes = [
    "頭痛：4条件すべて全測定点で最小値(1)、変化なし",
    "吐き気：4条件すべてほぼ1（おにぎり+スムージーのDAY10 9:30のみ一時的に2）",
    "血糖値が高めに推移するおにぎり同時摂取条件でも、消化器症状は悪化していない",
    "満腹感・食欲の差は「おにぎりを同時に食べたか」による食事量の違いを反映しており、副食の形態（固形/液状）そのものの効果ではない",
  ];
  let ny = 2.55;
  notes.forEach(n => {
    s.addText("•  " + n, { x: 8.65, y: ny, w: 3.85, h: 0.95, fontFace: "Calibri", fontSize: 11, color: INK, isTextBox: true, margin: 0 });
    ny += 1.02;
  });
}

// ================= Slide: Nightly performance metrics =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "PERFORMANCE", "毎晩のコンディション・トレーニング指標（4条件比較）", false);

  const perfConds = ["固形", "スムージー", "おにぎり+スムージー", "おにぎり+糖質減"];
  const perfColors = [C_SOLID, C_SMOOTHIE, C_ONIGISMO, C_LOWSUGAR];

  const metrics = [
    { title: "起床時コンディション", sub: "高いほど良好", values: [2.00, 2.33, 2.33, 2.67] },
    { title: "睡眠の質", sub: "高いほど良好", values: [2.00, 2.00, 2.00, 2.67] },
    { title: "持久力（自己評価）", sub: "高いほど良好", values: [3.00, 3.67, 3.83, 2.33] },
    { title: "爆発力（自己評価）", sub: "高いほど良好", values: [4.00, 3.67, 3.50, 3.33] },
    { title: "RPE（主観的運動強度）", sub: "高いほどきつい", values: [6.67, 5.67, 5.50, 6.33] },
    { title: "練習時間 (分/日)", sub: "条件ブロックにより変動", values: [140, 60, 80, 100], intFmt: true },
  ];

  const panelW = 3.75, gapX = 0.4;
  const cols = 3;
  metrics.forEach((m, idx) => {
    const col = idx % cols, row = Math.floor(idx / cols);
    const x = MARGIN + col * (panelW + gapX);
    const y = 1.72 + row * 2.55;
    s.addText(m.title, { x, y, w: panelW, h: 0.28, fontFace: "Calibri", fontSize: 12, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    s.addText(m.sub, { x, y: y + 0.27, w: panelW, h: 0.24, fontFace: "Calibri", fontSize: 9.5, color: MUTED, isTextBox: true, margin: 0 });
    s.addChart("bar", [{ name: m.title, labels: perfConds, values: m.values }], {
      x, y: y + 0.58, w: panelW, h: 1.85,
      barDir: "col",
      chartColors: perfColors,
      chartColorsOpacity: 100,
      showTitle: false, showLegend: false,
      showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 9.5, dataLabelColor: INK,
      dataLabelFormatCode: m.intFmt ? "#,##0" : "0.0",
      catAxisLabelColor: MUTED, catAxisLabelFontSize: 8.5, catAxisLabelRotate: 20,
      valAxisHidden: true,
      catGridLine: { style: "none" }, valGridLine: { style: "none" },
      catAxisLineColor: "E3E1DB", valAxisLineColor: "E3E1DB",
      barGapWidthPct: 35
    });
  });

  addFooter(s, "各条件3日間平均。起床時コンディション・睡眠の質・持久力・爆発力は高いほど良好、運動後疲労・RPEは高いほど負荷が大きいと仮定（原データに尺度定義なし）。", false);
}

// ================= Slide: Synthesis / trade-off =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "SYNTHESIS", "総合考察：食事 × トレーニング × 血糖", false);

  s.addShape("roundRect", { x: MARGIN, y: 1.75, w: W - MARGIN * 2, h: 1.55, rectRadius: 0.12, fill: { color: "FDF3E2" }, line: { color: "EDA100", width: 1 } });
  s.addText("⚠ 重要な交絡：練習時間が条件ブロックごとに大きく異なる", { x: MARGIN + 0.3, y: 1.9, w: W - MARGIN * 2 - 0.6, h: 0.3, fontFace: "Calibri", fontSize: 13, bold: true, color: "6B4B00", isTextBox: true, margin: 0 });
  s.addText(
    "固形の3日間は平均140分（180/120/120分）と突出して長く、スムージーの3日間は毎日60分で最短。RPE・爆発力・持久力・運動後疲労は運動量そのものにも左右されるため、固形のRPE・爆発力の高さは「食事」よりも「練習量が多かったこと」を反映している可能性がある。トレーニングはどの条件も11:00〜14:00の間に実施。",
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
    "✓ 総合評価：現時点のデータでは「おにぎり＋スムージー（糖質ノーマル、同時摂取）」が最もバランスの良い候補。「おにぎり＋糖質減」は血糖面（なだらかさ・燃料供給とも）ではむしろ優れており、体感（持久力低下）との矛盾を解消できれば第一候補に上がる可能性もある。",
    { x: MARGIN + 0.3, y: 5.9, w: W - MARGIN * 2 - 0.6, h: 0.95, fontFace: "Calibri", fontSize: 12.5, bold: true, color: "0F5C3D", isTextBox: true, margin: 0 }
  );
}

// ================= Slide 10: Conclusion =================
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  titleBlock(s, "CONCLUSION", "結論と次のステップ", true);

  const concl = [
    "おにぎりを崩さず副食と同時に食べる方針は血糖の観点から一貫して支持される：乱高下を抑えつつ、練習中の燃料供給も確保できる",
    "固形は「血糖が安定」ではなく「練習中の燃料不足」（練習中平均135、他条件の約6割）と解釈すべき",
    "総合評価：現時点では「おにぎり＋スムージー（糖質ノーマル、同時摂取）」が最もバランスの良い候補",
  ];
  let y = 1.9;
  concl.forEach((c, i) => {
    s.addShape("oval", { x: MARGIN, y, w: 0.42, h: 0.42, fill: { color: "1C7293" }, line: { type: "none" } });
    s.addText(String(i + 1), { x: MARGIN, y, w: 0.42, h: 0.42, align: "center", valign: "middle", fontFace: "Cambria", fontSize: 14, bold: true, color: WHITE, isTextBox: true, margin: 0 });
    s.addText(c, { x: MARGIN + 0.65, y: y - 0.02, w: 11.3, h: 0.6, fontFace: "Calibri", fontSize: 14, color: "E8EDF7", isTextBox: true, margin: 0, valign: "middle" });
    y += 0.85;
  });

  s.addShape("roundRect", { x: MARGIN, y: 4.55, w: W - MARGIN * 2, h: 2.2, rectRadius: 0.1, fill: { color: "1A2350" }, line: { type: "none" } });
  s.addText("次のステップ", { x: MARGIN + 0.35, y: 4.75, w: 6, h: 0.35, fontFace: "Calibri", fontSize: 14, bold: true, color: "8FB7E0", isTextBox: true, margin: 0 });
  const next = [
    "8:00ベースライン血糖の条件間差（60〜70 mg/dL）の要因確認（前日運動量・睡眠・センサー校正）",
    "練習時間が条件ブロックごとに大きく異なる（60〜180分）ため、今後は練習内容・時間を揃えて再検証すると食事の純粋な効果を評価しやすくなる",
    "満腹感・食欲の条件差は「おにぎり同時摂取による食事量の違い」であり、形態そのものの効果ではない点に留意",
  ];
  let ny = 5.2;
  next.forEach(n => {
    s.addText("•  " + n, { x: MARGIN + 0.35, y: ny, w: W - MARGIN * 2 - 0.7, h: 0.5, fontFace: "Calibri", fontSize: 12.5, color: "CADCFC", isTextBox: true, margin: 0 });
    ny += 0.48;
  });

  addFooter(s, "データ出典：for_AI_.xlsx／0824スケジュール.xlsx／condition_app_2026-08-25_2026-09-07.xlsx", true);
}

pres.writeFile({ fileName: "output.pptx" }).then(() => console.log("done"));
