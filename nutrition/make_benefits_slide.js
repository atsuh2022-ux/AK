// 「アスリートが食事を工夫すると、どんな良いことがあるのか？」のスライドを、各要素にアイコンを付けて作る。
// 実行: NODE_PATH=<pptxgenjs・react-icons・react・react-dom・sharp を入れた node_modules> node make_benefits_slide.js
const pptxgen = require("pptxgenjs");
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");
const fa6 = require("react-icons/fa6");
const gi = require("react-icons/gi");
const md = require("react-icons/md");

const FONT = "Yu Gothic";
const TEXT = "1A1A1A", CREAM = "FFF0C8", ICON = "C9731A", THINK = "D1557A";

async function icon(Comp, color) {
  const svg = renderToStaticMarkup(React.createElement(Comp, { color: `#${color}`, size: 256 }));
  const png = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + png.toString("base64");
}

// 円の中心（インチ）は元のスライドの配置に合わせる
const ITEMS = [
  { text: "コンディション\nを整える", x: 3.0, y: 3.05, icon: fa.FaHeartbeat },
  { text: "身体を大きくする", x: 10.05, y: 2.75, icon: gi.GiMuscleUp },
  { text: "減量する", x: 6.85, y: 4.2, icon: fa6.FaWeightScale },
  { text: "素早く回復する", x: 3.75, y: 5.8, icon: md.MdBatteryChargingFull },
  { text: "トレーニング効果\nを高める", x: 10.75, y: 5.55, icon: gi.GiWeightLiftingUp },
];
const EW = 3.5, EH = 2.55;

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  const slide = pres.addSlide();
  slide.background = { color: "FFFFFF" };

  // 左上：考えている人
  slide.addImage({ data: await icon(gi.GiThink, THINK), x: 0.45, y: 0.3, w: 1.2, h: 1.2 });
  slide.addText("アスリートが食事を工夫すると、\nどんな良いことがあるのか？", {
    x: 2.2, y: 0.3, w: 10.5, h: 1.3, fontFace: FONT, fontSize: 32, bold: true,
    color: TEXT, margin: 0, valign: "middle", isTextBox: true,
  });

  for (const it of ITEMS) {
    slide.addShape(pres.shapes.OVAL, {
      x: it.x - EW / 2, y: it.y - EH / 2, w: EW, h: EH,
      fill: { color: CREAM }, line: { color: CREAM },
    });
    slide.addImage({ data: await icon(it.icon, ICON), x: it.x - 0.45, y: it.y - 1.0, w: 0.9, h: 0.9 });
    slide.addText(it.text, {
      x: it.x - 1.5, y: it.y, w: 3.0, h: 0.9, fontFace: FONT, fontSize: 20, bold: true,
      color: TEXT, align: "center", valign: "middle", margin: 0, isTextBox: true,
    });
  }

  await pres.writeFile({ fileName: `${__dirname}/benefits_slide.pptx` });
  console.log("wrote benefits_slide.pptx");
})();
