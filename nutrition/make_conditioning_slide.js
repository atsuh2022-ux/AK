// 「トータルコンディショニング」の概念図を PowerPoint の図形で作る。
// 実行: NODE_PATH=<pptxgenjs・react-icons・react・react-dom・sharp を入れた node_modules> node make_conditioning_slide.js
const pptxgen = require("pptxgenjs");
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");
const gi = require("react-icons/gi");

const FONT = "Yu Gothic";
const RED = "D7262E", GRAY = "8A8A8A", TEXT = "1A1A1A";

async function icon(Comp, color) {
  const svg = renderToStaticMarkup(React.createElement(Comp, { color: `#${color}`, size: 256 }));
  const png = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + png.toString("base64");
}

// 中心と各要素の配置（インチ、角度は右=0°・反時計回り）
const C = { x: 6.67, y: 4.1 };
const RING_R = 3.0, BOX_R = 2.05, BOX = 0.95, HUB_R = 0.8;
const ITEMS = [
  { label: "フィジカル", deg: 90, icon: gi.GiMuscleUp },
  { label: "メンタル", deg: 42, icon: fa.FaBrain },
  { label: "栄養", deg: 0, icon: fa.FaAppleAlt },
  { label: "その他", deg: -42, icon: fa.FaEllipsisH },
  { label: "睡眠", deg: -138, icon: fa.FaBed },
  { label: "トレーニング", deg: 180, icon: fa.FaDumbbell },
  { label: "メディカル", deg: 138, icon: fa.FaPlus },
];
// リングの上に並べる「支える人たち」（下のラベル付近は空ける）
const SUPPORTERS = [30, 70, 110, 150, 200, 230, 310, 340];

const pt = (deg, r) => {
  const a = (deg * Math.PI) / 180;
  return { x: C.x + r * Math.cos(a), y: C.y - r * Math.sin(a) };
};

// 始点 p1 から終点 p2 への矢印（pptxgenjs の線は左上基準＋反転で向きを表す）
function arrow(slide, pres, p1, p2, color) {
  slide.addShape(pres.shapes.LINE, {
    x: Math.min(p1.x, p2.x), y: Math.min(p1.y, p2.y),
    w: Math.max(Math.abs(p2.x - p1.x), 0.001), h: Math.max(Math.abs(p2.y - p1.y), 0.001),
    flipH: p2.x < p1.x, flipV: p2.y < p1.y,
    line: { color, width: 3, endArrowType: "triangle" },
  });
}

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  const slide = pres.addSlide();
  slide.background = { color: "FFFFFF" };

  slide.addText("アスリートを支えるトータルコンディショニング", {
    x: 0.6, y: 0.3, w: 12.1, h: 0.6, fontFace: FONT, fontSize: 28, bold: true,
    color: TEXT, margin: 0, isTextBox: true,
  });

  // 外側のリング
  slide.addShape(pres.shapes.OVAL, {
    x: C.x - RING_R, y: C.y - RING_R, w: RING_R * 2, h: RING_R * 2,
    fill: { type: "none" }, line: { color: RED, width: 10 },
  });

  // 支える人たち（白い円の上にアイコン）
  const person = await icon(fa.FaUser, RED);
  for (const deg of SUPPORTERS) {
    const p = pt(deg, RING_R);
    slide.addShape(pres.shapes.OVAL, {
      x: p.x - 0.28, y: p.y - 0.28, w: 0.56, h: 0.56,
      fill: { color: "FFFFFF" }, line: { color: RED, width: 1.5 },
    });
    slide.addImage({ data: person, x: p.x - 0.16, y: p.y - 0.18, w: 0.32, h: 0.32 });
  }

  // 下から中心へ向かう大きな矢印と「トータルコンディショニング」
  slide.addShape(pres.shapes.UP_ARROW, {
    x: C.x - 0.75, y: C.y + HUB_R + 0.12, w: 1.5, h: RING_R - HUB_R - 0.45,
    fill: { color: RED }, line: { color: RED },
  });
  slide.addText("トータルコンディショニング", {
    x: C.x - 1.9, y: C.y + RING_R - 0.33, w: 3.8, h: 0.62, fontFace: FONT, fontSize: 18,
    bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0,
    shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.31, fill: { color: RED },
    line: { color: "FFFFFF", width: 2 },
  });

  // 要素ボックスと双方向の矢印（赤：要素→アスリート、灰：アスリート→要素）
  for (const it of ITEMS) {
    const b = pt(it.deg, BOX_R);
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: b.x - BOX / 2, y: b.y - BOX / 2, w: BOX, h: BOX, rectRadius: 0.14,
      fill: { color: "FFFFFF" }, line: { color: RED, width: 2.5 },
    });
    slide.addImage({ data: await icon(it.icon, RED), x: b.x - 0.3, y: b.y - 0.3, w: 0.6, h: 0.6 });
    slide.addText(it.label, {
      x: b.x - 1.0, y: b.y - BOX / 2 - 0.42, w: 2.0, h: 0.38, fontFace: FONT, fontSize: 15,
      bold: true, color: TEXT, align: "center", valign: "bottom", margin: 0, isTextBox: true,
    });

    const a = (it.deg * Math.PI) / 180, off = 0.09;
    const n = { x: -Math.sin(a) * off, y: -Math.cos(a) * off }; // 矢印を左右にずらす量
    const r1 = HUB_R + 0.12, r2 = BOX_R - BOX / 2 - 0.12;
    const shift = (p, s) => ({ x: p.x + n.x * s, y: p.y + n.y * s });
    arrow(slide, pres, shift(pt(it.deg, r2), 1), shift(pt(it.deg, r1), 1), RED);
    arrow(slide, pres, shift(pt(it.deg, r1), -1), shift(pt(it.deg, r2), -1), GRAY);
  }

  // 中心：アスリート
  slide.addShape(pres.shapes.OVAL, {
    x: C.x - HUB_R, y: C.y - HUB_R, w: HUB_R * 2, h: HUB_R * 2,
    fill: { color: "FFFFFF" }, line: { color: GRAY, width: 4 },
  });
  slide.addImage({ data: await icon(fa.FaRunning, TEXT), x: C.x - 0.38, y: C.y - 0.55, w: 0.76, h: 0.76 });
  slide.addText("アスリート", {
    x: C.x - 0.8, y: C.y + 0.25, w: 1.6, h: 0.35, fontFace: FONT, fontSize: 14, bold: true,
    color: TEXT, align: "center", margin: 0, isTextBox: true,
  });

  await pres.writeFile({ fileName: `${__dirname}/conditioning_slide.pptx` });
  console.log("wrote conditioning_slide.pptx");
})();
