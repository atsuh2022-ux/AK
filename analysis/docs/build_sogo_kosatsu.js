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
    children: [new TextRun({ text, font: HFONT, bold: true, size: level === HeadingLevel.HEADING_1 ? 26 : 23 })],
  });
}

function cell(text, opts = {}) {
  return new TableCell({
    width: { size: opts.width, type: WidthType.DXA },
    shading: opts.shade ? { type: ShadingType.CLEAR, color: "auto", fill: opts.shade } : undefined,
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 100, bottom: 100, left: 120, right: 120 },
    children: [new Paragraph({
      alignment: opts.center ? AlignmentType.CENTER : AlignmentType.LEFT,
      children: [new TextRun({ text, font: FONT, size: 19, bold: !!opts.bold })],
    })],
  });
}

const colW = [2700, 2700, 3400];
const tableWidth = colW.reduce((a, b) => a + b, 0);

const header = new TableRow({
  tableHeader: true,
  children: ["想定していた主張", "データによる支持", "推奨される表現"].map((t, i) =>
    cell(t, { width: colW[i], shade: "21295C", bold: true, center: true })
  ),
});
const rowsData = [
  ["スムージーは固形食より消化・吸収が速い", "✗ 支持されない\nTmax：固形30分（8:30）vs スムージー45分（8:45）。むしろ固形の方がやや早い", "「吸収の速さ」ではなく「血糖上昇の大きさ（Δピーク）」の違いとして記述する"],
  ["胃の貯留時間が短く、身体的負担が少ない", "△ 部分的にのみ支持\n10:00時点の残存満腹感はスムージーが低い(1.33 vs 2.00)が、ピーク時点(9:00)の満腹感はスムージーの方が高い(5.0 vs 4.0)", "「負担軽減」と断定せず、「終盤の残存感は低い可能性がある」等、限定的な表現にとどめる"],
  ["エネルギーが速く使えるようになった", "△ 「速く」ではなく「多く」\nΔピークはスムージー85.0 vs 固形53.7 mg/dLで、スムージーの方が明確に大きい", "「より多くの糖質が短時間で血中に供給された」という量的な表現に修正する"],
];
const body = rowsData.map((r, idx) => new TableRow({
  children: r.map((t, i) => cell(t, { width: colW[i], shade: idx % 2 === 0 ? "F4F7F9" : undefined })),
}));
const claimTable = new Table({ width: { size: tableWidth, type: WidthType.DXA }, columnWidths: colW, rows: [header, ...body] });

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 21 } } } },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 } } },
    children: [
      new Paragraph({
        spacing: { after: 400 },
        children: [new TextRun({ text: "総合考察：実験1（コンディション変化）と実験2（血糖値比較）の関連について", font: HFONT, bold: true, size: 32 })],
      }),

      heading("実験1と実験2をつなぐ仮説", HeadingLevel.HEADING_1),
      p("実験1では、朝食をスムージー中心に変更した前後で、瞬発力・敏速性、持久力の実感向上および疲労感の軽減という、複数の項目にわたる好ましい変化が観察された。この観察は、朝食の形態が運動パフォーマンスに関連する主観的コンディションに何らかの影響を及ぼしている可能性を示唆するものであり、その背景にある生理学的機序を明らかにすることを目的として実験2（固形食・スムージー等4条件による血糖値比較）を実施した。"),
      p("実験2に着手した時点での作業仮説は、「スムージーは固形食に比べて消化・吸収が速く、胃内での滞留時間が短いために身体的負担が少なく、かつエネルギーとして迅速に利用可能になることで、瞬発力・持久力の向上や疲労感の軽減につながったのではないか」というものであった。"),

      heading("実験2の結果が実際に示していること", HeadingLevel.HEADING_1),
      p("しかし、実験2で得られた血糖値データは、この作業仮説を単純な形では支持しなかった。固形摂取条件とスムージー摂取条件について、後続のおにぎり摂取（2品目）が行われる前の8:00〜10:00の区間でピーク到達時間（Tmax）を比較したところ、固形摂取では摂取後30分（8:30）、スムージー摂取では摂取後45分（8:45）であり、Tmaxの差はわずか15分にとどまった。すなわち、血糖値が最高値に達するまでの「速さ」という観点では、両条件に明確な差は認められなかった。"),
      p("一方で、ピーク血糖値およびベースラインからの増加量（Δピーク）は、スムージー摂取条件の方が固形摂取条件よりも明確に大きかった（Δピーク：スムージー85.0 mg/dL、固形53.7 mg/dL）。また、満腹感に関する主観評価（0〜10点）をみると、スムージー摂取条件はピーク時点（9:00）の満腹感がむしろ固形摂取条件よりも高く（5.0 vs 4.0）、そのピークのタイミングも遅かった（9:00 vs 8:30）。一方で、10:00時点の残存満腹感はスムージー摂取条件の方が低かった（1.33 vs 2.00）。"),

      heading("想定していた説明と、データが支持する範囲の違い", HeadingLevel.HEADING_1),
      p("以上を踏まえ、実験2着手時の作業仮説と、実際に得られたデータが支持する範囲との対応を表1に整理する。"),
      new Paragraph({
        spacing: { before: 100, after: 100 },
        children: [new TextRun({ text: "表1　作業仮説とデータによる支持の対応", font: FONT, size: 19, bold: true })],
      }),
      claimTable,
      p("表1が示す通り、「消化・吸収が速い」という当初の説明は、Tmaxのデータとは整合しない。むしろ固形摂取の方がわずかに早くピークに到達しており、この点に関しては当初の仮説を修正する必要がある。「胃の負担が少ない」という説明についても、満腹感のピーク値自体はスムージーの方が高かったことから、単純な「負担軽減」として記述することは適切ではなく、「消化管内からの排出自体は、終盤では早い可能性がある」という限定的な表現にとどめるべきである。"),

      heading("統合的な解釈（データが支持する範囲での考察）", HeadingLevel.HEADING_1),
      p("実験2のデータから妥当に主張できるのは、「スムージーは固形食に比べて、同じ時間内でより多くの糖質が血中に供給された（＝血糖上昇の勢い・大きさが異なる）」という量的な違いである。この量的な違いが、運動前・運動中に利用可能なエネルギー量の違いとして、瞬発力・持久力の実感向上や疲労感の軽減に部分的に寄与した可能性は否定できない。"),
      p("すなわち、実験1で観察されたコンディションの変化は、朝食からの「吸収の速さ」ではなく、「供給される糖質の量・血糖上昇の大きさ」という側面から説明する方が、実験2で得られたデータとの整合性が高いと考えられる。"),

      heading("本研究全体の限界", HeadingLevel.HEADING_1),
      p("ただし、実験1と実験2を統合して解釈するにあたっては、以下の点に留意する必要がある。"),
      p("第一に、実験1（12月16日前後の観察）と実験2（8月下旬〜9月の統制されたプロトコル）は実施時期が大きく異なり、両者の間には練習フェーズやシーズンの違いなど、朝食形態以外の要因が介在していた可能性がある。したがって、実験1で観察された変化の生理学的機序を実験2が直接的に証明したとは言えず、本研究で示せるのはあくまで示唆的な関連にとどまる。"),
      p("第二に、実験2における固形摂取条件とスムージー摂取条件の比較は、後続の14日間連続血糖モニタリングで判明したDAY5（8/29）以降の血糖ベースラインシフトの影響を一部受けている可能性があり、この点でも結果の解釈には慎重を要する。"),
      p("第三に、各条件n=3日という少数の試行に基づく記述的な傾向であり、統計的検定は行っていない。"),

      heading("今後の検証", HeadingLevel.HEADING_1),
      p("実験1と実験2の関連をより強固に示すためには、同一期間内で朝食条件を統制しつつ、血糖値と主観的コンディション（瞬発力・持久力・疲労感）を同時に測定し、両者の関連を直接的に検討する追試が必要である。また、消化管の負担や胃内滞留時間を評価する指標（満腹感アンケートに加え、可能であれば胃排出に関する客観的指標等）を充実させることで、「負担軽減」という当初の仮説についてもより精緻に検証できると考えられる。"),
    ],
  }],
});

Packer.toBuffer(doc).then((buf) => { require("fs").writeFileSync("output_sogo_kosatsu.docx", buf); console.log("done"); });
