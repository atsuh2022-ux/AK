// 「炭水化物源と摂取量」「たんぱく質必要量」の2枚を PowerPoint で作る。
// 実行: NODE_PATH=<pptxgenjs を入れた node_modules> node make_intake_slides.js
const pptxgen = require("pptxgenjs");

const FONT = "Yu Gothic";
const TEXT = "1A1A1A", MUTED = "5A5A5A", NAVY = "1F3A8A", HEAD = "FCEFB4",
  ZEBRA = "EDEDED", RULE = "BFBFBF", ACCENT = "C0392B";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in

function title(slide, text) {
  slide.background = { color: "FFFFFF" };
  slide.addText(text, {
    x: 0.6, y: 0.35, w: 12.1, h: 0.8, fontFace: FONT, fontSize: 32, bold: true,
    color: NAVY, margin: 0, isTextBox: true,
  });
}

// ---- 1枚目：エネルギー摂取量の調整 炭水化物源と摂取量 ----
{
  const slide = pres.addSlide();
  title(slide, "エネルギー摂取量の調整　炭水化物源と摂取量");

  const head = (t) => ({
    text: t, options: { bold: true, fill: { color: HEAD }, color: TEXT, fontSize: 18 },
  });
  const rows = [[
    head("体重\n（kg）"), head("炭水化物摂取量\n（g/kg体重）"), head("1日摂取量\n（g/日）"),
    head("1食あたりの白飯\n（g）"), head("1食あたりの食パン\n（6枚切り・枚）"),
  ]];
  const data = [
    [80, 480, 345, 4.6], [75, 450, 320, 4.3], [70, 420, 300, 4.0], [65, 390, 280, 3.7],
    [60, 360, 260, 3.4], [55, 330, 240, 3.1], [50, 300, 220, 2.9], [45, 270, 200, 2.6],
  ];
  data.forEach(([kg, day, rice, bread], i) => {
    const fill = { color: i % 2 ? ZEBRA : "FFFFFF" };
    const cell = (t, color = TEXT, bold = false) => ({ text: String(t), options: { fill, color, bold } });
    rows.push([
      cell(kg, NAVY, true), cell(6), cell(day),
      cell(rice, NAVY, true), cell(bread.toFixed(1), NAVY, true),
    ]);
  });
  slide.addTable(rows, {
    x: 0.9, y: 1.45, w: 11.5, colW: [1.7, 2.6, 2.1, 2.55, 2.55],
    rowH: [0.95, ...Array(8).fill(0.52)],
    fontFace: FONT, fontSize: 20, align: "center", valign: "middle", margin: 0.04,
    border: { type: "solid", pt: 0.75, color: RULE },
  });

  slide.addText([
    { text: "主な炭水化物源：", options: { bold: true, color: TEXT } },
    { text: "ごはん・パックごはん・おにぎり・食パン", options: { color: TEXT } },
  ], {
    x: 0.9, y: 6.7, w: 11.5, h: 0.45, fontFace: FONT, fontSize: 16, margin: 0, isTextBox: true,
  });
}

// ---- 2枚目：一般的な健康人のたんぱく質必要量 ----
{
  const slide = pres.addSlide();
  title(slide, "一般的な健康人のたんぱく質必要量");

  slide.addText("1日あたり総量", {
    x: 0.9, y: 1.3, w: 5, h: 0.45, fontFace: FONT, fontSize: 18, bold: true,
    color: TEXT, margin: 0, isTextBox: true,
  });

  const h = (text, opts = {}) => ({ text, options: { bold: true, fill: { color: HEAD }, ...opts } });
  const rows = [
    [h("年齢（歳）", { rowspan: 2 }), h("推奨量（g/日）", { colspan: 2 })],
    [h("男子"), h("女子")],
  ];
  const data = [
    ["1〜2", 20, 20], ["3〜5", 25, 25], ["6〜7", 30, 30], ["8〜9", 40, 40],
    ["10〜11", 45, 50], ["12〜14", 60, 55], ["15〜17", 65, 55], ["18〜29", 65, 50],
    ["30〜49", 65, 50], ["50〜64", 65, 50], ["65〜74", 60, 50], ["75以上", 60, 50],
  ];
  data.forEach(([age, m, f], i) => {
    // 思春期（12〜17歳）を強調
    const teen = age === "12〜14" || age === "15〜17";
    const fill = { color: teen ? "E3EAFB" : "FFFFFF" };
    rows.push([age, m, f].map((t) => ({
      text: String(t), options: { fill, bold: teen, color: teen ? NAVY : TEXT },
    })));
  });
  slide.addTable(rows, {
    x: 0.9, y: 1.8, w: 5.4, colW: [2.0, 1.7, 1.7], rowH: 0.34,
    fontFace: FONT, fontSize: 15, align: "center", valign: "middle", margin: 0.03,
    border: { type: "solid", pt: 0.75, color: RULE }, color: TEXT,
  });
  slide.addText("（「日本人の食事摂取基準 2020年版」をもとに作成）", {
    x: 0.9, y: 6.7, w: 5.4, h: 0.3, fontFace: FONT, fontSize: 11, color: MUTED,
    margin: 0, align: "center", isTextBox: true,
  });

  // 右側：体重1kgあたりの量（イメージ）… 一般の人とアスリートの比較
  const px = 7.1, pw = 5.6;
  slide.addText("体重1kgあたりの量（イメージ）", {
    x: px, y: 1.3, w: pw, h: 0.45, fontFace: FONT, fontSize: 18, bold: true,
    color: TEXT, margin: 0, isTextBox: true,
  });
  const baseY = 5.3, unit = 1.3; // 1 g/kg あたりの高さ（インチ）
  const bars = [
    { label: "一般の人", val: 1, text: "約1g", color: "9DB4E8" },
    { label: "アスリート", val: 2, text: "約2g", color: NAVY },
  ];
  bars.forEach((b, i) => {
    const bx = px + 0.7 + i * 2.5, bw = 1.6, bh = b.val * unit;
    slide.addShape(pres.shapes.RECTANGLE, {
      x: bx, y: baseY - bh, w: bw, h: bh, fill: { color: b.color }, line: { color: b.color },
    });
    slide.addText(b.text, {
      x: bx - 0.3, y: baseY - bh - 0.6, w: bw + 0.6, h: 0.5, fontFace: FONT, fontSize: 22,
      bold: true, color: TEXT, align: "center", margin: 0, isTextBox: true,
    });
    slide.addText(b.label, {
      x: bx - 0.3, y: baseY + 0.1, w: bw + 0.6, h: 0.4, fontFace: FONT, fontSize: 16,
      color: TEXT, align: "center", margin: 0, isTextBox: true,
    });
  });
  slide.addShape(pres.shapes.LINE, {
    x: px + 0.3, y: baseY, w: pw - 0.9, h: 0, line: { color: MUTED, width: 1 },
  });

  // 下：アスリートの目安
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: px, y: 6.0, w: pw, h: 1.0, rectRadius: 0.12, fill: { color: "E3EAFB" }, line: { color: "E3EAFB" },
  });
  slide.addText([
    { text: "アスリートのたんぱく質摂取目安", options: { fontSize: 16, bold: true, color: NAVY, breakLine: true } },
    { text: "体重1kgあたり ", options: { fontSize: 20, color: TEXT } },
    { text: "2g/日", options: { fontSize: 26, bold: true, color: ACCENT } },
    { text: " 程度", options: { fontSize: 20, color: TEXT } },
  ], {
    x: px + 0.25, y: 6.05, w: pw - 0.5, h: 0.9, fontFace: FONT, valign: "middle", margin: 0,
    isTextBox: true,
  });
}

pres.writeFile({ fileName: `${__dirname}/intake_slides.pptx` }).then(() => console.log("wrote intake_slides.pptx"));
