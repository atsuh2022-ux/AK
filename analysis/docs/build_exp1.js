const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, AlignmentType, VerticalAlign
} = require("docx");

const FONT = "游明朝";
const HFONT = "游ゴシック";

function p(text) {
  return new Paragraph({
    spacing: { after: 200, line: 360 },
    children: [new TextRun({ text, font: FONT, size: 21 })],
  });
}

function heading(text, level) {
  return new Paragraph({
    heading: level,
    spacing: { before: 320, after: 160 },
    children: [new TextRun({ text, font: HFONT, bold: true, size: level === HeadingLevel.HEADING_1 ? 28 : 24 })],
  });
}

function cell(text, opts = {}) {
  return new TableCell({
    width: { size: opts.width, type: WidthType.DXA },
    shading: opts.shade ? { type: ShadingType.CLEAR, color: "auto", fill: opts.shade } : undefined,
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 80, bottom: 80, left: 100, right: 100 },
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text, font: FONT, size: 18, bold: !!opts.bold })],
    })],
  });
}

const colW = [2000, 2400, 1500, 1500, 1200];
const tableWidth = colW.reduce((a, b) => a + b, 0);

const rows = [
  ["瞬発力・敏速性", "全くない/少ない", "44%", "32%", "-12pt"],
  ["瞬発力・敏速性", "普通", "12%", "16%", "+4pt"],
  ["瞬発力・敏速性", "少しある/かなりある", "44%", "51%", "+7pt"],
  ["持久力", "全くない/少ない", "24%", "32%", "+8pt"],
  ["持久力", "普通", "44%", "22%", "-22pt"],
  ["持久力", "少しある/かなりある", "32%", "46%", "+14pt"],
  ["疲労感（練習中）", "全くない/少ない", "4%", "19%", "+15pt"],
  ["疲労感（練習中）", "普通", "44%", "41%", "-3pt"],
  ["疲労感（練習中）", "少しある/かなりある", "52%", "41%", "-11pt"],
  ["疲労感（練習後）", "全くない/少ない", "8%", "38%", "+30pt"],
  ["疲労感（練習後）", "普通", "36%", "43%", "+7pt"],
  ["疲労感（練習後）", "少しある/かなりある", "56%", "19%", "-37pt"],
];
// rows where |diff| >= 10pt AND the direction is favorable (less fatigue / more power-endurance felt)
const favorable = new Set([0, 5, 6, 8, 9, 11]);

const header = new TableRow({
  tableHeader: true,
  children: ["項目", "回答区分", "変更前\n(n=25)", "変更後\n(n=37)", "差"].map((t, i) =>
    cell(t, { width: colW[i], shade: "21295C", bold: true })
  ),
});
const body = rows.map((r, idx) => new TableRow({
  children: r.map((t, i) => cell(t, {
    width: colW[i],
    shade: favorable.has(idx) ? "EAF7F0" : (idx % 2 === 0 ? "F4F7F9" : undefined),
  })),
}));
const condTable = new Table({ width: { size: tableWidth, type: WidthType.DXA }, columnWidths: colW, rows: [header, ...body] });

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 21 } } } },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 } } },
    children: [
      new Paragraph({
        spacing: { after: 400 },
        children: [new TextRun({ text: "朝食形態の変更（12/16）前後における実践練習時コンディションの変化", font: HFONT, bold: true, size: 32 })],
      }),

      heading("背景", HeadingLevel.HEADING_1),
      p("本研究はもともと、日々のコンディション記録アプリを用いた定常的なモニタリングの中で得られた観察から着想を得ている。対象選手は朝食の形態を12月16日を境にスムージー中心へと変更しており、その前後で実践練習時の主観的コンディション（瞬発力・敏速性、持久力、疲労感）に変化がみられるかを比較したところ、複数の項目で望ましい方向への変化が確認された。"),
      p("この予備的な観察が、朝食の形態・組成が血糖動態やコンディションに及ぼす影響を統制された条件下で検証する、固形食・スムージー等4条件の血糖値比較研究（実験2）に着手する直接の動機となった。本節ではこの予備的な観察（実験1）について整理する。"),

      heading("方法", HeadingLevel.HEADING_1),
      p("対象は実験2と同一の、高位脊髄損傷を有する車いす陸上競技選手1名である。対象選手は日々のコンディション記録アプリを用いて、実践練習後に「瞬発力・敏速性」「持久力」「疲労感（練習中）」「疲労感（練習後）」の4項目について、3段階（全くない/少ない・普通・少しある/かなりある）で自己評価を行っていた。"),
      p("朝食をスムージー中心に変更した12月16日を境に、変更前（n=25回答）・変更後（n=37回答）の回答割合を項目ごとに集計し、比較した。本検討は特定の条件を実験的に割り付けて実施した介入研究ではなく、日常的に蓄積されたコンディション記録データを後方視的に比較した観察研究である点に留意されたい。"),

      heading("結果", HeadingLevel.HEADING_1),
      p("12月16日を境とした前後比較の結果を表1に示す。回答割合の差が10ポイント以上であり、かつ好ましい方向への変化（疲労感の減少、持久力・瞬発力の実感の増加）を示した項目は、網掛けで示した6区分であった。"),
      new Paragraph({
        spacing: { before: 100, after: 100 },
        children: [new TextRun({ text: "表1　朝食変更（12/16）前後における実践練習時コンディションの回答割合", font: FONT, size: 19, bold: true })],
      }),
      condTable,
      p("瞬発力・敏速性では「全くない/少ない」の回答割合が44%から32%へ12ポイント減少した（力を感じないとする回答が減少）。持久力では「少しある/かなりある」の回答割合が32%から46%へ14ポイント増加した。疲労感（練習中）では「全くない/少ない」が4%から19%へ15ポイント増加し、「少しある/かなりある」は52%から41%へ11ポイント減少した。疲労感（練習後）では「全くない/少ない」が8%から38%へ30ポイント増加し、「少しある/かなりある」は56%から19%へ37ポイント減少し、4項目の中で最も大きな変化を示した。"),

      heading("考察", HeadingLevel.HEADING_1),
      p("朝食をスムージー中心に変更して以降、瞬発力・敏速性、持久力の実感が高まり、特に練習後の疲労感が大きく軽減する傾向が観察された。これは、朝食形態の違いが血糖動態を介してエネルギー供給パターンを変化させ、練習中・練習後の主観的コンディションに影響を及ぼしている可能性を示唆する観察であり、固形食・スムージー等の違いが血糖応答にどう反映されるかを厳密に検証する必要性（実験2の着想）につながるものである。"),
      p("一方で、本観察には研究デザイン上の重要な限界がある。本比較は12月16日というカレンダー日付を境にした前後比較であり、この期間に朝食形態以外の要因（練習フェーズや試合期・オフ期の違い、季節・気温の変化、疲労の蓄積度、睡眠環境の変化等）が同時に変化していた可能性を排除できない。この構造は、後続の実験2・14日間連続血糖モニタリングにおいて確認された「DAY5（8/29）以降の血糖ベースラインシフト」が引き起こす前後比較の交絡と本質的に同型の問題であり、本観察のみから朝食形態の変更を直接の原因として特定することはできない。"),
      p("また、本検討は朝食形態の変更という単一の生活イベントを境にした観察研究であり、ランダム化や統制群を伴う実験的デザインではない。得られた割合の差についても統計的検定は行っておらず、記述的な傾向として位置づけるべきである。これらの限界を踏まえ、本観察（実験1）はあくまで研究の着想・動機づけとなった予備的知見として扱い、朝食形態と血糖動態・コンディションの関係を因果的に検証する役割は、統制されたプロトコルのもとで実施した実験2が担うものと位置づける。"),
    ],
  }],
});

Packer.toBuffer(doc).then((buf) => { require("fs").writeFileSync("output_exp1.docx", buf); console.log("done"); });
