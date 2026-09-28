// 「ジュニアアスリートにおけるサプリメントの考え方」を高校生向けに2枚のスライドにする。
// 実行: NODE_PATH=<pptxgenjs・react-icons・react・react-dom・sharp を入れた node_modules> node make_supplement_slides.js
const pptxgen = require("pptxgenjs");
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa");
const gi = require("react-icons/gi");

const FONT = "Yu Gothic";
const TEXT = "1A1A1A", MUTED = "5A5A5A";
const GREEN = "2C7A4B", GREEN_LIGHT = "E6F2EA", ORANGE = "E8741A", RED = "C0392B", RED_LIGHT = "FBEAEA";

async function icon(Comp, color) {
  const el = React.createElement(Comp, { color: `#${color}`, size: 256 });
  if (!Comp) throw new Error("icon not found");
  const png = await sharp(Buffer.from(renderToStaticMarkup(el))).png().toBuffer();
  return "image/png;base64," + png.toString("base64");
}

// 白い円の上にアイコン
async function iconCircle(slide, pres, Comp, color, bg, x, y, d) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: bg }, line: { color: bg } });
  const s = d * 0.58;
  slide.addImage({ data: await icon(Comp, color), x: x + (d - s) / 2, y: y + (d - s) / 2, w: s, h: s });
}

function title(slide, text) {
  slide.background = { color: "FFFFFF" };
  slide.addText(text, {
    x: 0.6, y: 0.35, w: 12.1, h: 0.8, fontFace: FONT, fontSize: 32, bold: true, color: GREEN,
    margin: 0, isTextBox: true,
  });
}

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";

  // ---- 1枚目：サプリメントについての考え方 ----
  {
    const slide = pres.addSlide();
    title(slide, "ジュニアアスリートとサプリメント");

    // 左：サプリに「×」
    slide.addShape(pres.shapes.OVAL, {
      x: 0.9, y: 1.6, w: 3.2, h: 3.2, fill: { color: RED_LIGHT }, line: { color: RED_LIGHT },
    });
    slide.addImage({ data: await icon(fa.FaPills, "8A8A8A"), x: 1.6, y: 2.3, w: 1.8, h: 1.8 });
    slide.addImage({ data: await icon(fa.FaBan, RED), x: 1.2, y: 1.9, w: 2.6, h: 2.6 });
    slide.addText("むやみに\nとらない", {
      x: 0.9, y: 4.9, w: 3.2, h: 0.9, fontFace: FONT, fontSize: 22, bold: true, color: RED,
      align: "center", valign: "middle", margin: 0, isTextBox: true,
    });

    // 右：ポイント2つ
    const points = [
      {
        icon: fa.FaExclamationTriangle, color: RED, bg: RED_LIGHT,
        head: "サプリメントは、むやみにすすめられていません",
        body: "ジュニア期にサプリを使っていた人は、その後の問題行動につながるリスクが高いことが報告されています。",
      },
      {
        icon: fa.FaRunning, color: GREEN, bg: GREEN_LIGHT,
        head: "いちばん大切なのは「体づくり」と「食習慣」",
        body: "競技に合わせた、健康な体づくりと食習慣を身につけることが最も大切です。",
      },
    ];
    for (const [i, p] of points.entries()) {
      const y = 1.6 + i * 1.95;
      slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x: 4.7, y, w: 8.0, h: 1.75, rectRadius: 0.12, fill: { color: p.bg }, line: { color: p.bg },
      });
      await iconCircle(slide, pres, p.icon, p.color, "FFFFFF", 4.95, y + 0.4, 0.95);
      slide.addText([
        { text: p.head, options: { fontSize: 20, bold: true, color: p.color, breakLine: true } },
        { text: p.body, options: { fontSize: 16, color: TEXT } },
      ], {
        x: 6.15, y: y + 0.15, w: 6.35, h: 1.45, fontFace: FONT, valign: "middle", margin: 0,
        paraSpaceAfter: 4, isTextBox: true,
      });
    }

    // 下：まとめ
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.6, y: 5.95, w: 12.1, h: 1.15, rectRadius: 0.14, fill: { color: GREEN }, line: { color: GREEN },
    });
    slide.addImage({ data: await icon(fa.FaCheckCircle, "FFFFFF"), x: 0.95, y: 6.2, w: 0.65, h: 0.65 });
    slide.addText([
      { text: "必要なエネルギーを", options: {} },
      { text: "いろいろな食品", options: { color: "FFE08A" } },
      { text: "からとれば、必要な栄養素は十分にとれる！", options: {} },
    ], {
      x: 1.85, y: 5.95, w: 10.7, h: 1.15, fontFace: FONT, fontSize: 20, bold: true, color: "FFFFFF",
      valign: "middle", margin: 0, isTextBox: true,
    });
  }

  // ---- 2枚目：サプリより大切な3つの食習慣 ----
  {
    const slide = pres.addSlide();
    title(slide, "サプリより大切な、3つの食習慣");

    const cards = [
      {
        icon: gi.GiMeal, head: "いろいろな\n食べものにふれる",
        body: "いろいろな食品や料理、食文化を経験しよう。",
      },
      {
        icon: fa.FaClock, head: "練習に合わせて\n食べる",
        body: "練習やトレーニングの内容・タイミングに合わせて食べる習慣をつけよう。",
      },
      {
        icon: gi.GiCookingPot, head: "自分で食事を\n管理できる力をつける",
        body: "家族や指導者といっしょに料理して、料理や食品の特徴を知ろう。",
        badge: "最優先！",
      },
    ];
    const cw = 3.8, gap = 0.35, x0 = (13.333 - (cw * 3 + gap * 2)) / 2;
    for (const [i, c] of cards.entries()) {
      const x = x0 + i * (cw + gap), y = 1.5;
      slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
        x, y, w: cw, h: 4.3, rectRadius: 0.15, fill: { color: GREEN_LIGHT }, line: { color: GREEN_LIGHT },
      });
      slide.addText(String(i + 1), {
        x: x + 0.25, y: y + 0.25, w: 0.55, h: 0.55, shape: pres.shapes.OVAL, fill: { color: GREEN },
        fontFace: FONT, fontSize: 20, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0,
      });
      if (c.badge) {
        slide.addText(c.badge, {
          x: x + cw - 1.55, y: y + 0.28, w: 1.3, h: 0.45, shape: pres.shapes.ROUNDED_RECTANGLE,
          rectRadius: 0.2, fill: { color: ORANGE }, fontFace: FONT, fontSize: 15, bold: true,
          color: "FFFFFF", align: "center", valign: "middle", margin: 0,
        });
      }
      await iconCircle(slide, pres, c.icon, GREEN, "FFFFFF", x + (cw - 1.4) / 2, y + 0.8, 1.4);
      slide.addText(c.head, {
        x: x + 0.2, y: y + 2.3, w: cw - 0.4, h: 0.95, fontFace: FONT, fontSize: 21, bold: true,
        color: GREEN, align: "center", valign: "middle", margin: 0, isTextBox: true,
      });
      slide.addText(c.body, {
        x: x + 0.3, y: y + 3.3, w: cw - 0.6, h: 0.9, fontFace: FONT, fontSize: 16, color: TEXT,
        align: "left", valign: "top", margin: 0, isTextBox: true,
      });
    }

    // 下：なぜ3が大切か
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.6, y: 6.05, w: 12.1, h: 1.05, rectRadius: 0.14, fill: { color: "FFF4E8" }, line: { color: ORANGE, width: 1.5 },
    });
    slide.addImage({ data: await icon(fa.FaPlane, ORANGE), x: 0.9, y: 6.28, w: 0.6, h: 0.6 });
    slide.addText([
      { text: "海外遠征や寮生活など、", options: {} },
      { text: "親元を離れたとき", options: { bold: true, color: ORANGE } },
      { text: "でも、自分で食事を選べるようにしておこう！", options: {} },
    ], {
      x: 1.75, y: 6.05, w: 10.8, h: 1.05, fontFace: FONT, fontSize: 19, bold: true, color: TEXT,
      valign: "middle", margin: 0, isTextBox: true,
    });
  }

  await pres.writeFile({ fileName: `${__dirname}/supplement_slides.pptx` });
  console.log("wrote supplement_slides.pptx");
})();
