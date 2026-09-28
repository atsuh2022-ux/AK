// 献立の栄養素充足率を、料理ごとにクリックで積み上げるアニメーション付き PowerPoint を作る。
// 実行: NODE_PATH=<pptxgenjs を入れた node_modules> node make_pptx.js
const pptxgen = require("pptxgenjs");
const JSZip = require("jszip");
const fs = require("fs");

const NUTRIENTS = ["エネルギー", "たんぱく質", "脂質", "炭水化物", "カルシウム", "鉄",
  "ビタミンA", "ビタミンB1", "ビタミンB2", "ビタミンC", "食物繊維"];

// 料理ごとの栄養量（日本食品標準成分表 八訂より算出）
const DISHES = [
  ["ご飯", [234, 3.8, 0.5, 55.7, 5, 0.2, 0, 0.03, 0.02, 0, 2.3]],
  ["豚の生姜焼き", [274, 16.8, 19.5, 7.5, 26, 0.6, 23, 0.58, 0.16, 23, 1.1]],
  ["ほうれん草の胡麻和え", [54, 2.8, 3.0, 5.5, 102, 1.1, 270, 0.05, 0.09, 11, 2.8]],
  ["豆腐の味噌汁", [46, 3.9, 1.8, 4.5, 51, 1.0, 0, 0.03, 0.04, 1, 1.4]],
  ["オレンジ", [42, 1.0, 0.1, 9.8, 21, 0.3, 10, 0.10, 0.03, 40, 0.8]],
  ["牛乳", [122, 6.6, 7.6, 9.6, 220, 0.0, 76, 0.08, 0.30, 2, 0]],
];

// 日本人の食事摂取基準（2020年版）男性・身体活動レベルⅡ
// 脂質・炭水化物は目標量（エネルギー比 20〜30%・50〜65%）の中央値をグラム換算
const std = (kcal, p, ca, fe, va, b1, b2, vc, fib) =>
  [kcal, p, kcal * 0.25 / 9, kcal * 0.575 / 4, ca, fe, va, b1, b2, vc, fib];
const AGES = [
  ["12〜14歳", std(2600, 60, 1000, 10.0, 800, 1.4, 1.6, 100, 17)],
  ["15〜17歳", std(2800, 65, 800, 10.0, 900, 1.5, 1.7, 100, 19)],
];

const COLORS = ["2A78D6", "EB6834", "1BAF7A", "EDA100", "E87BA4", "008300"];
const TEXT = "0B0B0B", MUTED = "52514E", GRID = "E4E3DF", LINE = "E34948";
const FONT = "Yu Gothic";
const Y_MAX = 90;

// チャート枠と、その中のプロット領域（割合）を固定して、33% ラベルの位置を合わせる
const CHART = { x: 0.3, y: 1.05, w: 9.7, h: 5.9 };
const PLOT = { x: 0.1, y: 0.03, w: 0.84, h: 0.78 };

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";

for (const [ageLabel, s] of AGES) {
  const slide = pres.addSlide();
  slide.background = { color: "FFFFFF" };
  slide.addText(`献立の栄養素充足率（思春期男性 ${ageLabel}）`, {
    x: 0.5, y: 0.3, w: 12.3, h: 0.7, fontFace: FONT, fontSize: 28, bold: true,
    color: TEXT, margin: 0, isTextBox: true,
  });

  const barData = DISHES.map(([name, vals]) => ({
    name, labels: NUTRIENTS,
    values: vals.map((v, i) => Math.round(v / s[i] * 1000) / 10),
  }));
  slide.addChart([
    {
      type: pres.charts.BAR, data: barData,
      options: { barDir: "col", barGrouping: "stacked", chartColors: COLORS, barGapWidthPct: 60 },
    },
    {
      type: pres.charts.LINE,
      data: [{ name: "1食分に必要な量", labels: NUTRIENTS, values: NUTRIENTS.map(() => 33.3) }],
      options: { chartColors: [LINE], lineDataSymbol: "none", lineSize: 2, lineDash: "dash" },
    },
  ], {
    ...CHART, objectName: "Chart",
    layout: PLOT, showLegend: false,
    valAxisMinVal: 0, valAxisMaxVal: Y_MAX, valAxisMajorUnit: 10,
    valAxisTitle: "1日に必要な量に対する割合（%）", showValAxisTitle: true,
    valAxisTitleFontSize: 12, valAxisTitleColor: MUTED, valAxisTitleFontFace: FONT,
    valAxisLabelColor: MUTED, valAxisLabelFontSize: 12, valAxisLabelFontFace: FONT,
    catAxisLabelColor: TEXT, catAxisLabelFontSize: 13, catAxisLabelFontFace: FONT,
    catAxisLabelRotate: -40,
    valGridLine: { color: GRID, size: 0.75 }, catGridLine: { style: "none" },
  });

  // 33% ラベル（プロット領域の右外）
  const y33 = CHART.y + CHART.h * (PLOT.y + PLOT.h * (1 - 33.3 / Y_MAX));
  slide.addText("1食分に\n必要な量", {
    x: CHART.x + CHART.w * (PLOT.x + PLOT.w) + 0.02, y: y33 - 0.3, w: 0.8, h: 0.6,
    fontFace: FONT, fontSize: 12, bold: true, color: LINE, margin: 0, valign: "middle",
    isTextBox: true,
  });

  // 料理名（クリックごとに表示）
  slide.addText("料理", {
    x: 10.35, y: 1.25, w: 2.6, h: 0.4, fontFace: FONT, fontSize: 14, color: MUTED,
    margin: 0, isTextBox: true,
  });
  DISHES.forEach(([name], i) => {
    slide.addText([
      { text: "■ ", options: { color: COLORS[i] } },
      { text: name, options: { color: TEXT } },
    ], {
      x: 10.35, y: 1.8 + i * 0.7, w: 2.9, h: 0.55, fontFace: FONT, fontSize: 16, bold: true,
      margin: 0, valign: "middle", objectName: `Dish${i}`, isTextBox: true,
    });
  });

  slide.addText(
    "基準値：日本人の食事摂取基準（2020年版）男性・身体活動レベルⅡ。脂質・炭水化物は目標量（エネルギー比20〜30%・50〜65%）の中央値、食物繊維は目標量。",
    { x: 0.5, y: 7.0, w: 12.3, h: 0.3, fontFace: FONT, fontSize: 10, color: MUTED, margin: 0, isTextBox: true },
  );
}

// ---- アニメーション（クリックごとに「料理名フェードイン＋系列ワイプ（下から）」）----
let ctnId;
const tgtShape = (spid) => `<p:spTgt spid="${spid}"/>`;
const tgtSeries = (spid, idx) =>
  `<p:spTgt spid="${spid}"><p:graphicEl><a:chart seriesIdx="${idx}" categoryIdx="-4" bldStep="series"/></p:graphicEl></p:spTgt>`;

function effect(tgt, kind, nodeType, withGrp) {
  const [presetID, subtype, filter] = kind === "wipe" ? [22, 4, "wipe(up)"] : [10, 0, "fade"];
  return `<p:par><p:cTn id="${ctnId++}" presetID="${presetID}" presetClass="entr" presetSubtype="${subtype}" fill="hold"${withGrp ? ' grpId="0"' : ""} nodeType="${nodeType}"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>` +
    `<p:set><p:cBhvr><p:cTn id="${ctnId++}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn><p:tgtEl>${tgt}</p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>` +
    `<p:animEffect transition="in" filter="${filter}"><p:cBhvr><p:cTn id="${ctnId++}" dur="600"/><p:tgtEl>${tgt}</p:tgtEl></p:cBhvr></p:animEffect>` +
    `</p:childTnLst></p:cTn></p:par>`;
}

// 1ステップ = 外側 par（トリガー）> 内側 par > 効果群
function step(trigger, effects) {
  return `<p:par><p:cTn id="${ctnId++}" fill="hold"><p:stCondLst><p:cond delay="${trigger}"/></p:stCondLst><p:childTnLst>` +
    `<p:par><p:cTn id="${ctnId++}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>` +
    effects.join("") + `</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>`;
}

function timingXml(chartId, dishIds) {
  ctnId = 3;
  // 目安線（最後の系列）はスライド表示と同時に出す
  const steps = [step("0", [effect(tgtSeries(chartId, DISHES.length), "fade", "afterEffect", true)])];
  dishIds.forEach((id, i) => {
    steps.push(step("indefinite", [
      effect(tgtShape(id), "fade", "clickEffect", true),
      effect(tgtSeries(chartId, i), "wipe", "withEffect", true),
    ]));
  });
  return `<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>` +
    `<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>` +
    steps.join("") +
    `</p:childTnLst></p:cTn><p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>` +
    `<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>` +
    `</p:childTnLst></p:cTn></p:par></p:tnLst><p:bldLst>` +
    `<p:bldGraphic spid="${chartId}" grpId="0"><p:bldSub><a:bldChart bld="series" animBg="0"/></p:bldSub></p:bldGraphic>` +
    dishIds.map((id) => `<p:bldP spid="${id}" grpId="0"/>`).join("") +
    `</p:bldLst></p:timing>`;
}

const idOf = (xml, name) => {
  const m = xml.match(new RegExp(`<p:cNvPr id="(\\d+)" name="${name}"`));
  if (!m) throw new Error(`shape ${name} not found`);
  return m[1];
};

(async () => {
  const buf = await pres.write({ outputType: "nodebuffer" });
  const zip = await JSZip.loadAsync(buf);
  for (let n = 1; n <= AGES.length; n++) {
    const path = `ppt/slides/slide${n}.xml`;
    let xml = await zip.file(path).async("string");
    const chartId = idOf(xml, "Chart");
    const dishIds = DISHES.map((_, i) => idOf(xml, `Dish${i}`));
    const timing = timingXml(chartId, dishIds);
    xml = xml.includes("</p:clrMapOvr>")
      ? xml.replace("</p:clrMapOvr>", "</p:clrMapOvr>" + timing)
      : xml.replace("</p:cSld>", "</p:cSld>" + timing);
    zip.file(path, xml);
  }
  const out = await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" });
  fs.writeFileSync(__dirname + "/nutrient_animation.pptx", out);
  console.log("wrote nutrient_animation.pptx");
})();
