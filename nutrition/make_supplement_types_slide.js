// 「スポーツフード・サプリメントの種類」をベン図とアイコンで作る。
// 実行: NODE_PATH=<pptxgenjs・react-icons・react・react-dom・sharp を入れた node_modules> node make_supplement_types_slide.js
const pptxgen = require("pptxgenjs");
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const sharp = require("sharp");
const fa6 = require("react-icons/fa6");
const gi = require("react-icons/gi");

const FONT = "Yu Gothic";
const TEXT = "1A1A1A", MUTED = "5A5A5A";
const DIET = "C0561A", DIET_BG = "F6C9AE", PERF = "2F639E", PERF_BG = "B9D1EE", FOOD = "6B3FA0";

async function icon(Comp, color) {
  if (!Comp) throw new Error("icon not found");
  const svg = renderToStaticMarkup(React.createElement(Comp, { color: `#${color}`, size: 256 }));
  const png = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + png.toString("base64");
}

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  const slide = pres.addSlide();
  slide.background = { color: "FFFFFF" };

  slide.addText("スポーツフード・サプリメントの種類", {
    x: 0.6, y: 0.35, w: 12.1, h: 0.8, fontFace: FONT, fontSize: 32, bold: true, color: TEXT,
    margin: 0, isTextBox: true,
  });

  // ---- 左：ベン図 ----
  const cy = 1.45, cw = 4.6, ch = 5.3, lx = 0.5, rx = 3.3;
  const circle = (x, fill, line) => slide.addShape(pres.shapes.OVAL, {
    x, y: cy, w: cw, h: ch, fill: { color: fill, transparency: 45 }, line: { color: line, width: 3 },
  });
  circle(lx, DIET_BG, DIET);
  circle(rx, PERF_BG, PERF);

  const img = async (Comp, color, x, y, s = 0.75) =>
    slide.addImage({ data: await icon(Comp, color), x: x - s / 2, y, w: s, h: s });
  const label = (text, x, y, w, color, size = 20) => slide.addText(text, {
    x: x - w / 2, y, w, h: 1.0, fontFace: FONT, fontSize: size, bold: true, color,
    align: "center", valign: "middle", margin: 0, isTextBox: true,
  });

  // ダイエタリーサプリメント（左だけの部分）
  const dX = 1.9;
  await img(fa6.FaPrescriptionBottle, DIET, dX, 2.15);
  label("ダイエタリー\nサプリメント", dX, 3.6, 2.5, DIET);
  await img(fa6.FaTablets, DIET, dX, 5.05);

  // スポーツフード（重なった部分）
  const fX = 4.2;
  await img(fa6.FaBottleWater, FOOD, fX, 2.35, 0.65);
  label("スポーツ\nフード", fX, 3.6, 1.6, FOOD, 19);
  await img(gi.GiPowderBag, FOOD, fX - 0.38, 4.85, 0.62);
  await img(gi.GiJelly, FOOD, fX + 0.38, 4.85, 0.62);

  // パフォーマンスサプリメント（右だけの部分）
  const pX = 6.5;
  await img(gi.GiPowder, PERF, pX, 2.15);
  label("パフォーマンス\nサプリメント", pX, 3.6, 2.6, PERF);
  await img(fa6.FaMugHot, PERF, pX, 5.05);

  // ---- 右：3つの種類の説明 ----
  const kinds = [
    {
      name: "スポーツフード", color: FOOD, bg: "EFE8F7",
      body: "運動に必要なエネルギーや栄養素を手軽にとるための食品",
      ex: "スポーツドリンク、ゼリー飲料、プロテイン",
    },
    {
      name: "ダイエタリーサプリメント", color: DIET, bg: "FCEDE3",
      body: "不足しがちなビタミン・ミネラルを補うもの",
      ex: "ビタミン剤、カルシウム",
    },
    {
      name: "パフォーマンスサプリメント", color: PERF, bg: "E6EFF9",
      body: "競技力（パフォーマンス）の向上をねらうもの",
      ex: "クレアチン、カフェイン",
    },
  ];
  const kx = 8.35, kw = 4.55;
  kinds.forEach((k, i) => {
    const y = 1.45 + i * 1.78;
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: kx, y, w: kw, h: 1.62, rectRadius: 0.12, fill: { color: k.bg }, line: { color: k.bg },
    });
    slide.addText(String(i + 1), {
      x: kx + 0.2, y: y + 0.18, w: 0.46, h: 0.46, shape: pres.shapes.OVAL, fill: { color: k.color },
      fontFace: FONT, fontSize: 16, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0,
    });
    slide.addText(k.name, {
      x: kx + 0.8, y: y + 0.13, w: kw - 0.95, h: 0.55, fontFace: FONT, fontSize: 18, bold: true,
      color: k.color, valign: "middle", margin: 0, isTextBox: true,
    });
    slide.addText([
      { text: k.body, options: { color: TEXT, breakLine: true } },
      { text: `例：${k.ex}`, options: { color: MUTED } },
    ], {
      x: kx + 0.25, y: y + 0.72, w: kw - 0.45, h: 0.82, fontFace: FONT, fontSize: 13,
      valign: "top", margin: 0, paraSpaceAfter: 3, isTextBox: true,
    });
  });

  slide.addText("ジュニア期は、まず毎日の食事から！", {
    x: kx, y: 6.85, w: kw, h: 0.4, fontFace: FONT, fontSize: 15, bold: true, color: TEXT,
    align: "right", margin: 0, isTextBox: true,
  });

  await pres.writeFile({ fileName: `${__dirname}/supplement_types_slide.pptx` });
  console.log("wrote supplement_types_slide.pptx");
})();
