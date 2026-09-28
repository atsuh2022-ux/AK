// 「運動中にエネルギー源となる栄養素」のスライドを元の構成どおりに作る（クリックで順に表示）。
// グラフの値: Romijn JA et al. (1993) の図からの読み取り概算（cal/kg/min）
// 実行: NODE_PATH=<pptxgenjs・react-icons・react・react-dom・sharp を入れた node_modules> node make_energy_nutrient_slide.js
const pptxgen = require("pptxgenjs");
const JSZip = require("jszip");
const fs = require("fs");
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");
const gi = require("react-icons/gi");

const FONT = "Yu Gothic";
const TEXT = "1A1A1A", MUTED = "5A5A5A", GRID = "E4E3DF", DARKRED = "C00000";
const CARB = "1F3F8F", CARB_FILL = "7FA3E0", FAT = "E0661A", FAT_FILL = "F4A582";

async function icon(Comp, color) {
  const svg = renderToStaticMarkup(React.createElement(Comp, { color: `#${color}`, size: 256 }));
  const png = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + png.toString("base64");
}

const LEVELS = ["25", "65", "85"];
// 積み上げ順（下から）
const SOURCES = [
  { name: "Plasma Glucose（血液中のブドウ糖）", color: "1B2F66", values: [9, 17, 38] },
  { name: "Plasma FFA（血液中の脂肪酸）", color: "E8741A", values: [68, 58, 43] },
  { name: "Muscle Triglycerides（筋肉の中の脂肪）", color: "F8C9A0", values: [10, 54, 40] },
  { name: "Muscle Glycogen（筋グリコーゲン）", color: "3A6BC9", values: [0, 80, 175] },
];
const Y_MAX = 400;

// チャート枠とプロット領域（割合）を固定し、矢印を 85% の棒に合わせる
const CHART = { x: 1.55, y: 2.55, w: 5.6, h: 3.3 };
const PLOT = { x: 0.13, y: 0.04, w: 0.84, h: 0.8 };
const GAP = 0.8; // barGapWidthPct / 100

// ステップ（クリック順）ごとにアニメーションさせる図形の名前
const STEPS = [[], [], [], [], []];

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  const slide = pres.addSlide();
  slide.background = { color: "FFFFFF" };
  const named = (step, name) => { STEPS[step].push(name); return name; };

  // タイトル（最初から表示）
  slide.addImage({ data: await icon(gi.GiBowlOfRice, "8A7560"), x: 0.3, y: 0.2, w: 1.15, h: 1.15 });
  slide.addImage({ data: await icon(fa.FaRunning, "D7262E"), x: 1.6, y: 0.5, w: 0.85, h: 0.85 });
  slide.addText("運動中にエネルギー源となる栄養素", {
    x: 2.6, y: 0.5, w: 9.5, h: 0.75, fontFace: FONT, fontSize: 30, bold: true, color: TEXT,
    valign: "middle", margin: 0, isTextBox: true,
  });

  // ① 炭水化物（糖質）と脂質
  const ellipse = (text, x, w, fill, line, step) => slide.addText(text, {
    x, y: 1.35, w, h: 0.8, shape: pres.shapes.OVAL, fill: { color: fill }, line: { color: line, width: 1.5 },
    fontFace: FONT, fontSize: 26, bold: true, color: TEXT, align: "center", valign: "middle",
    margin: 0, objectName: named(step, text),
  });
  ellipse("炭水化物（糖質）", 3.0, 4.2, CARB_FILL, "4A72C4", 0);
  ellipse("脂質", 7.6, 3.8, FAT_FILL, "E0661A", 0);

  // ② グラフと見出し
  const caption = (text, y, name) => slide.addText(text, {
    x: 1.9, y, w: 5.2, h: 0.45, fill: { color: "EDEDED" }, fontFace: FONT, fontSize: 18, bold: true,
    color: DARKRED, align: "center", valign: "middle", margin: 0, objectName: named(1, name),
  });
  caption("使っているエネルギー源", 2.2, "CapTop");
  slide.addChart(pres.charts.BAR, SOURCES.map((s) => ({ name: s.name, labels: LEVELS, values: s.values })), {
    ...CHART, objectName: named(1, "Chart"), layout: PLOT,
    barDir: "col", barGrouping: "stacked", barGapWidthPct: GAP * 100,
    chartColors: SOURCES.map((s) => s.color), dataBorder: { pt: 1, color: "FFFFFF" },
    showLegend: false,
    valAxisMinVal: 0, valAxisMaxVal: Y_MAX, valAxisMajorUnit: 100,
    valAxisTitle: "cal・kg⁻¹・min⁻¹", showValAxisTitle: true,
    valAxisTitleFontSize: 11, valAxisTitleColor: MUTED, valAxisLabelFontSize: 11, valAxisLabelColor: MUTED,
    catAxisTitle: "% of VO₂max（運動の強さ）", showCatAxisTitle: true, catAxisTitleFontFace: FONT,
    catAxisTitleFontSize: 12, catAxisTitleColor: MUTED, catAxisLabelFontSize: 13, catAxisLabelColor: TEXT,
    valGridLine: { color: GRID, size: 0.75 }, catGridLine: { style: "none" },
  });
  caption("（右に行くほど、強度が高い）", 5.95, "CapBottom");

  // 凡例（グラフ左上の空きに、上から Glycogen の順で）
  const lx = CHART.x + CHART.w * PLOT.x + 0.15;
  [...SOURCES].reverse().forEach((s, i) => {
    const y = CHART.y + CHART.h * PLOT.y + 0.05 + i * 0.27;
    slide.addShape(pres.shapes.RECTANGLE, {
      x: lx, y: y + 0.05, w: 0.17, h: 0.17, fill: { color: s.color }, line: { color: "7F7F7F", width: 0.5 },
      objectName: named(1, `LegBox${i}`),
    });
    slide.addText(s.name, {
      x: lx + 0.25, y, w: 3.4, h: 0.27, fontFace: FONT, fontSize: 10.5, color: TEXT, valign: "middle",
      margin: 0, objectName: named(1, `LegText${i}`),
    });
  });

  // ③ 85% の棒の各部分を指す矢印と「糖質／脂質」
  const plotX = CHART.x + CHART.w * PLOT.x, plotW = CHART.w * PLOT.w;
  const catW = plotW / LEVELS.length, barW = catW / (1 + GAP);
  const barRight = plotX + catW * 2.5 + barW / 2;
  const yOf = (v) => CHART.y + CHART.h * (PLOT.y + PLOT.h * (1 - v / Y_MAX));
  const segMid = (k) => {
    const below = SOURCES.slice(0, k).reduce((s, x) => s + x.values[2], 0);
    return yOf(below + SOURCES[k].values[2] / 2);
  };
  const arrowX = barRight + 0.08, labelX = arrowX + 0.75;
  SOURCES.forEach((s, k) => {
    const carb = k === 0 || k === 3;
    slide.addShape(pres.shapes.LINE, {
      x: arrowX, y: segMid(k), w: 0.7, h: 0, flipH: true,
      line: { color: carb ? CARB : FAT, width: 3, endArrowType: "triangle" },
      objectName: named(2, `Arrow${k}`),
    });
  });
  const label = (text, y, color, name) => slide.addText(text, {
    x: labelX, y: y - 0.23, w: 1.0, h: 0.46, fontFace: FONT, fontSize: 24, bold: true, color,
    valign: "middle", margin: 0, objectName: named(2, name),
  });
  label("糖質", segMid(3), CARB, "LabelGlycogen");
  label("脂質", (segMid(1) + segMid(2)) / 2 - 0.1, FAT, "LabelFat");
  label("糖質", segMid(0) + 0.12, CARB, "LabelGlucose");

  // ④ メッセージ
  slide.addText([
    { text: "運動強度が上がるに", options: { breakLine: true } },
    { text: "つれて" }, { text: "糖質", options: { color: CARB } }, { text: "に頼る", options: { breakLine: true } },
    { text: "割合が上がる" },
  ], {
    x: 9.1, y: 2.9, w: 4.0, h: 2.2, fontFace: FONT, fontSize: 30, bold: true, color: TEXT,
    align: "center", valign: "middle", margin: 0, objectName: named(3, "Message"),
  });

  // ⑤ まとめ
  slide.addText([
    { text: "運動時（特に高強度運動時）に糖質の必要量が増えるので、" },
    { text: "主食が超重要！", options: { color: DARKRED } },
  ], {
    x: 0.3, y: 6.55, w: 12.73, h: 0.75, shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.1,
    fill: { color: "FFF59D" }, line: { color: "F0A020", width: 2, dashType: "dash" },
    fontFace: FONT, fontSize: 24, bold: true, color: TEXT, align: "center", valign: "middle",
    margin: 0, objectName: named(4, "Summary"),
  });

  // ---- アニメーション（各ステップ＝クリックでフェードイン）----
  const zip = await JSZip.loadAsync(await pres.write({ outputType: "nodebuffer" }));
  const path = "ppt/slides/slide1.xml";
  let xml = await zip.file(path).async("string");
  const idOf = (name) => {
    const m = xml.match(new RegExp(`<p:cNvPr id="(\\d+)" name="${name}"`));
    if (!m) throw new Error(`shape ${name} not found`);
    return m[1];
  };
  // テキストを持つ図形だけ bldP を付け、グラフは bldGraphic で丸ごと出す
  const hasText = (id) => new RegExp(`<p:cNvPr id="${id}"[^]*?</p:sp>`).exec(xml)?.[0].includes("<p:txBody>");

  let ctn = 3;
  const fade = (id, nodeType) =>
    `<p:par><p:cTn id="${ctn++}" presetID="10" presetClass="entr" presetSubtype="0" fill="hold" grpId="0" nodeType="${nodeType}"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>` +
    `<p:set><p:cBhvr><p:cTn id="${ctn++}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn><p:tgtEl><p:spTgt spid="${id}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>` +
    `<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="${ctn++}" dur="500"/><p:tgtEl><p:spTgt spid="${id}"/></p:tgtEl></p:cBhvr></p:animEffect>` +
    `</p:childTnLst></p:cTn></p:par>`;
  const steps = STEPS.map((names) => {
    const ids = names.map(idOf);
    const outer = ctn++, inner = ctn++;
    const effects = ids.map((id, i) => fade(id, i === 0 ? "clickEffect" : "withEffect")).join("");
    return `<p:par><p:cTn id="${outer}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst><p:childTnLst>` +
      `<p:par><p:cTn id="${inner}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>` +
      effects + `</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>`;
  });
  const chartId = idOf("Chart");
  const bld = STEPS.flat().map(idOf).map((id) => id === chartId
    ? `<p:bldGraphic spid="${id}" grpId="0"><p:bldAsOne/></p:bldGraphic>`
    : hasText(id) ? `<p:bldP spid="${id}" grpId="0" animBg="1"/>` : "").join("");
  const timing = `<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>` +
    `<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>` + steps.join("") +
    `</p:childTnLst></p:cTn><p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>` +
    `<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>` +
    `</p:childTnLst></p:cTn></p:par></p:tnLst><p:bldLst>${bld}</p:bldLst></p:timing>`;
  xml = xml.includes("</p:clrMapOvr>")
    ? xml.replace("</p:clrMapOvr>", "</p:clrMapOvr>" + timing)
    : xml.replace("</p:cSld>", "</p:cSld>" + timing);
  zip.file(path, xml);
  fs.writeFileSync(`${__dirname}/energy_nutrient_slide.pptx`,
    await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
  console.log("wrote energy_nutrient_slide.pptx");
})();
