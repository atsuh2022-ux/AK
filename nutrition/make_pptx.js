// 献立（menu.json）ごとに、栄養素充足率の積み上げグラフの PowerPoint を作る。
// ・<献立>_animation.pptx : クリックで料理ごとに積み上がるアニメーション版
// ・<献立>_steps_<年齢>.pptx : 料理を1品ずつ重ねた静止スライド版
// 実行: NODE_PATH=<pptxgenjs を入れた node_modules> node make_pptx.js
const pptxgen = require("pptxgenjs");
const JSZip = require("jszip");
const fs = require("fs");

const MENU = JSON.parse(fs.readFileSync(__dirname + "/menu.json", "utf8"));
const NUTRIENTS = MENU.nutrients;
const MAX_DISHES = 6;

// 日本人の食事摂取基準（2020年版）男性・身体活動レベルⅡ
// 脂質・炭水化物は目標量（エネルギー比 20〜30%・50〜65%）の中央値をグラム換算
const std = (kcal, p, ca, fe, va, b1, b2, vc, fib) =>
  [kcal, p, kcal * 0.25 / 9, kcal * 0.575 / 4, ca, fe, va, b1, b2, vc, fib];
const AGES = [
  ["12〜14歳", std(2600, 60, 1000, 10.0, 800, 1.4, 1.6, 100, 17)],
  ["15〜17歳", std(2800, 65, 800, 10.0, 900, 1.5, 1.7, 100, 19)],
];

const TEXT = "0B0B0B", MUTED = "52514E", GRID = "E4E3DF", LINE = "E34948";
const FONT = "Yu Gothic";
const Y_MAX = 100;

// チャート枠と、その中のプロット領域（割合）を固定して、33% ラベルの位置を合わせる
const CHART = { x: 0.3, y: 1.05, w: 9.7, h: 5.9 };
const PLOT = { x: 0.1, y: 0.03, w: 0.84, h: 0.78 };

// upto: 表示する料理の数（アニメーション版は全料理を置き、クリックで順に表示する）
// dishes: [[料理名, {color, values}], ...]
function addChartSlide(pres, menu, dishes, ageLabel, s, upto = dishes.length) {
  const slide = pres.addSlide();
  slide.background = { color: "FFFFFF" };
  slide.addText(`献立の栄養素充足率（思春期男性 ${ageLabel}）`, {
    x: 0.5, y: 0.3, w: 12.3, h: 0.7, fontFace: FONT, fontSize: 28, bold: true,
    color: TEXT, margin: 0, isTextBox: true,
  });
  slide.addText(`主菜：${menu.main}`, {
    x: 10.35, y: 0.4, w: 2.9, h: 0.5, fontFace: FONT, fontSize: 16, bold: true,
    color: TEXT, margin: 0, valign: "middle", isTextBox: true,
  });

  // まだ出ていない料理も 0 で系列に残し、料理ごとの色を固定する
  const barData = dishes.map(([name, { values }], d) => ({
    name, labels: NUTRIENTS,
    values: values.map((v, i) => (d < upto ? Math.round(v / s[i] * 1000) / 10 : 0)),
  }));
  slide.addChart([
    {
      type: pres.charts.BAR, data: barData,
      options: {
        barDir: "col", barGrouping: "stacked", barGapWidthPct: 60,
        chartColors: dishes.map(([, d]) => d.color), dataBorder: { pt: 1, color: "FFFFFF" },
      },
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

  // 料理名（アニメーション版はクリックごとに表示）
  slide.addText("料理", {
    x: 10.35, y: 1.25, w: 2.6, h: 0.4, fontFace: FONT, fontSize: 14, color: MUTED,
    margin: 0, isTextBox: true,
  });
  dishes.slice(0, upto).forEach(([name, { color }], i) => {
    slide.addText([
      { text: "■ ", options: { color } },
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

function newPres() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  return pres;
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
  const steps = [step("0", [effect(tgtSeries(chartId, dishIds.length), "fade", "afterEffect", true)])];
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

const ageKey = (label) => label.replace("〜", "-").replace("歳", "");

(async () => {
  for (const [key, menu] of Object.entries(MENU.menus)) {
    const dishes = menu.dishes.map((name) => [name, MENU.dishes[name]]);
    if (dishes.length > MAX_DISHES) throw new Error(`${key}: 料理は${MAX_DISHES}品まで`);

    // アニメーション版：年齢区分ごとに1枚
    const animPres = newPres();
    for (const [ageLabel, s] of AGES) addChartSlide(animPres, menu, dishes, ageLabel, s);
    const zip = await JSZip.loadAsync(await animPres.write({ outputType: "nodebuffer" }));
    for (let n = 1; n <= AGES.length; n++) {
      const path = `ppt/slides/slide${n}.xml`;
      let xml = await zip.file(path).async("string");
      const chartId = idOf(xml, "Chart");
      const dishIds = dishes.map((_, i) => idOf(xml, `Dish${i}`));
      const timing = timingXml(chartId, dishIds);
      xml = xml.includes("</p:clrMapOvr>")
        ? xml.replace("</p:clrMapOvr>", "</p:clrMapOvr>" + timing)
        : xml.replace("</p:cSld>", "</p:cSld>" + timing);
      zip.file(path, xml);
    }
    const animFile = `${key}_animation.pptx`;
    fs.writeFileSync(`${__dirname}/${animFile}`,
      await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
    console.log(`wrote ${animFile}`);

    // 静止版：年齢区分ごとに1ファイル、料理を1品ずつ重ねたスライド
    for (const [ageLabel, s] of AGES) {
      const pres = newPres();
      for (let k = 1; k <= dishes.length; k++) addChartSlide(pres, menu, dishes, ageLabel, s, k);
      const file = `${key}_steps_${ageKey(ageLabel)}.pptx`;
      await pres.writeFile({ fileName: `${__dirname}/${file}` });
      console.log(`wrote ${file}`);
    }
  }
})();
