// 「運動強度とエネルギー源」のスライドを高校生向けに作る。
// 元の図: Romijn JA et al. (1993) の運動強度別エネルギー源（値は図からの読み取り概算、cal/kg/min）
// 実行: NODE_PATH=<pptxgenjs を入れた node_modules> node make_energy_source_slide.js
const pptxgen = require("pptxgenjs");

const FONT = "Yu Gothic";
const TEXT = "1A1A1A", MUTED = "5A5A5A", GRID = "E4E3DF";
const CARB = "1F4FA8", CARB_LIGHT = "8FB3EA", FAT = "E8741A", FAT_LIGHT = "F7C08A";

const LEVELS = ["ゆっくり\n（ウォーキング程度）", "ややきつい\n（ジョギング程度）", "きつい\n（速いランニング）"];
// 積み上げ順（下から）
const SOURCES = [
  { name: "糖質：血液中のブドウ糖", color: CARB_LIGHT, values: [9, 17, 38] },
  { name: "脂質：血液中の脂肪", color: FAT_LIGHT, values: [68, 58, 43] },
  { name: "脂質：筋肉の中の脂肪", color: FAT, values: [10, 54, 40] },
  { name: "糖質：筋肉のグリコーゲン", color: CARB, values: [0, 80, 175] },
];

const totals = LEVELS.map((_, i) => SOURCES.reduce((s, src) => s + src.values[i], 0));
const carbShare = LEVELS.map((_, i) =>
  (SOURCES[0].values[i] + SOURCES[3].values[i]) / totals[i]);

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
const slide = pres.addSlide();
slide.background = { color: "FFFFFF" };

slide.addText([
  { text: "運動がきつくなるほど、", options: { color: TEXT } },
  { text: "糖質", options: { color: CARB } },
  { text: "をたくさん使う", options: { color: TEXT } },
], {
  x: 0.5, y: 0.3, w: 12.3, h: 0.75, fontFace: FONT, fontSize: 32, bold: true,
  margin: 0, isTextBox: true,
});
slide.addText("運動の強さ別に「体がエネルギーを何から作っているか」を比べたグラフ", {
  x: 0.5, y: 1.05, w: 12.3, h: 0.4, fontFace: FONT, fontSize: 16, color: MUTED,
  margin: 0, isTextBox: true,
});

// 左：積み上げ棒グラフ
slide.addChart(pres.charts.BAR, SOURCES.map((s) => ({ name: s.name, labels: LEVELS, values: s.values })), {
  x: 0.4, y: 1.55, w: 7.7, h: 5.4,
  barDir: "col", barGrouping: "stacked", barGapWidthPct: 55,
  chartColors: SOURCES.map((s) => s.color), dataBorder: { pt: 1, color: "FFFFFF" },
  showLegend: true, legendPos: "b", catAxisLabelRotate: 0, legendFontFace: FONT, legendFontSize: 12, legendColor: TEXT,
  valAxisMinVal: 0, valAxisMaxVal: 300, valAxisMajorUnit: 100,
  valAxisTitle: "使うエネルギーの量（多い↑）", showValAxisTitle: true,
  valAxisTitleFontFace: FONT, valAxisTitleFontSize: 12, valAxisTitleColor: MUTED,
  valAxisLabelFontSize: 11, valAxisLabelColor: MUTED,
  catAxisLabelFontFace: FONT, catAxisLabelFontSize: 12, catAxisLabelColor: TEXT,
  catAxisTitle: "運動の強さ →", showCatAxisTitle: true,
  catAxisTitleFontFace: FONT, catAxisTitleFontSize: 12, catAxisTitleColor: MUTED,
  valGridLine: { color: GRID, size: 0.75 }, catGridLine: { style: "none" },
});

// 右：糖質の割合を大きな数字で
const px = 8.45, pw = 4.45;
slide.addText("エネルギーのうち「糖質」の割合", {
  x: px, y: 1.65, w: pw, h: 0.45, fontFace: FONT, fontSize: 17, bold: true, color: TEXT,
  margin: 0, isTextBox: true,
});
const SHORT = ["ゆっくり", "ややきつい", "きつい"];
carbShare.forEach((share, i) => {
  const y = 2.2 + i * 1.02;
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: px, y, w: pw, h: 0.88, rectRadius: 0.1, fill: { color: "EEF3FC" }, line: { color: "EEF3FC" },
  });
  slide.addText(SHORT[i], {
    x: px + 0.25, y, w: 1.9, h: 0.88, fontFace: FONT, fontSize: 18, bold: true, color: TEXT,
    valign: "middle", margin: 0, isTextBox: true,
  });
  slide.addText([
    { text: "約", options: { fontSize: 18, color: TEXT } },
    { text: `${Math.round(share * 10)}割`, options: { fontSize: 34, bold: true, color: CARB } },
  ], {
    x: px + 2.1, y, w: 2.1, h: 0.88, fontFace: FONT, align: "right", valign: "middle",
    margin: 0, isTextBox: true,
  });
});

// まとめ
slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
  x: px, y: 5.35, w: pw, h: 1.6, rectRadius: 0.12, fill: { color: CARB }, line: { color: CARB },
});
slide.addText([
  { text: "練習や試合がハードな日ほど", options: { breakLine: true } },
  { text: "ごはん・パン・めん類など" , options: { breakLine: true } },
  { text: "糖質をしっかりとろう！", options: { fontSize: 20 } },
], {
  x: px + 0.25, y: 5.4, w: pw - 0.5, h: 1.5, fontFace: FONT, fontSize: 16, bold: true,
  color: "FFFFFF", valign: "middle", margin: 0, isTextBox: true,
});

slide.addText("Romijn JA ほか（1993）の図をもとに作成（値は図から読み取った概算）。運動の強さは最大酸素摂取量の25%・65%・85%。", {
  x: 0.5, y: 7.05, w: 12.3, h: 0.3, fontFace: FONT, fontSize: 10, color: MUTED, margin: 0, isTextBox: true,
});

pres.writeFile({ fileName: `${__dirname}/energy_source_slide.pptx` }).then(() => console.log("wrote energy_source_slide.pptx"));
