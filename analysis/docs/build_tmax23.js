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
    margins: { top: 100, bottom: 100, left: 120, right: 120 },
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text, font: FONT, size: 20, bold: !!opts.bold })],
    })],
  });
}

function resultsTable(rows) {
  const colW = [3000, 2600, 2000, 2000];
  const tableWidth = colW.reduce((a, b) => a + b, 0);
  const header = new TableRow({
    tableHeader: true,
    children: ["条件", "Tmax", "ピーク血糖値", "Δピーク"].map((t, i) =>
      cell(t, { width: colW[i], shade: "21295C", bold: true })
    ),
  });
  const body = rows.map((r, idx) => new TableRow({
    children: r.map((t, i) => cell(t, { width: colW[i], shade: idx % 2 === 0 ? "F4F7F9" : undefined })),
  }));
  return new Table({ width: { size: tableWidth, type: WidthType.DXA }, columnWidths: colW, rows: [header, ...body] });
}

function titleParagraph(text) {
  return new Paragraph({
    spacing: { after: 400 },
    children: [new TextRun({ text, font: HFONT, bold: true, size: 32 })],
  });
}

function tableCaption(text) {
  return new Paragraph({
    spacing: { before: 100, after: 100 },
    children: [new TextRun({ text, font: FONT, size: 19, bold: true })],
  });
}

function buildDoc(sections) {
  return new Document({
    styles: { default: { document: { run: { font: FONT, size: 21 } } } },
    sections: [{ properties: { page: { size: { width: 11906, height: 16838 } } }, children: sections }],
  });
}

// ============ ② スムージー vs おにぎり＋スムージー ============
const doc2 = buildDoc([
  titleParagraph("朝食の摂取タイミング（段階摂取 vs 同時摂取）が血糖ピーク到達時間（Tmax）に及ぼす影響"),

  heading("背景", HeadingLevel.HEADING_1),
  p("固形食・スムージーといった朝食の性状の違いに加え、同一の栄養素（おにぎり・スムージー）を摂取する際の「タイミング」の違いが血糖応答に与える影響も重要な検討課題である。具体的には、スムージーのみを8時に摂取し、約2時間半後の10時台に別途おにぎりを追加摂取する「段階摂取」と、おにぎりとスムージーを8時に同時摂取する「同時摂取」とでは、血糖値の立ち上がり方やピークのタイミングが異なる可能性がある。"),
  p("本節では、スムージー摂取条件（段階摂取）とおにぎり＋スムージー摂取条件（同時摂取）を比較し、摂取タイミングの違いが血糖ピーク到達時間（Tmax）に及ぼす影響を検討した。"),

  heading("方法", HeadingLevel.HEADING_1),
  p("対象は高位脊髄損傷を有する車いす陸上競技選手1名である。スムージー摂取条件（DAY4〜DAY6）では8:00にスムージーのみを摂取し、その後10時台におにぎりを追加摂取したのち11:00より練習を開始するプロトコルで実施された。おにぎり＋スムージー摂取条件（DAY8〜DAY10）では、8:00におにぎりとスムージーを同時に摂取するプロトコルで実施された。両条件ともFreeStyleリブレによる持続血糖モニタリングを行い、15分間隔で血糖値を記録した。"),
  p("本比較では、固形摂取とスムージー摂取の比較で用いた「単一栄養素の吸収速度を評価する」目的（8:00〜10:00への区間限定）とは異なり、「同じ2つの食品を同時に摂取するか、時間を分けて摂取するか」という摂取プロトコル全体としての血糖応答を評価することを目的とするため、8:00〜14:00の全記録区間を解析対象とした。各条件につき3日分の血糖値を時刻ごとに平均し、ピーク到達時刻（Tmax）、ピーク血糖値、および摂取前血糖値（ベースライン）からの増加量（Δピーク）を算出した。"),

  heading("結果", HeadingLevel.HEADING_1),
  p("スムージー摂取条件（段階摂取）ではTmaxは摂取後3時間45分（11:45）であり、ピーク血糖値は244.3 mg/dL、Δピークは85.0 mg/dLであった。おにぎり＋スムージー摂取条件（同時摂取）ではTmaxは摂取後4時間45分（12:45）であり、ピーク血糖値は242.3 mg/dL、Δピークは78.0 mg/dLであった（表1）。"),
  p("両条件のピーク血糖値・Δピークはほぼ同等であった一方、Tmaxには1時間の差がみられ、同時摂取条件の方がピーク到達が遅い結果となった。"),
  tableCaption("表1　スムージー摂取（段階摂取）・おにぎり＋スムージー摂取（同時摂取）条件におけるTmax（8:00〜14:00）"),
  resultsTable([
    ["スムージー摂取（段階摂取）", "摂取後3時間45分（11:45）", "244.3 mg/dL", "85.0 mg/dL"],
    ["おにぎり＋スムージー（同時摂取）", "摂取後4時間45分（12:45）", "242.3 mg/dL", "78.0 mg/dL"],
  ]),

  heading("考察", HeadingLevel.HEADING_1),
  p("ピーク血糖値・Δピークがほぼ同等であった一方でTmaxに1時間の差が生じたことは、摂取タイミングの違いが血糖反応の「大きさ」よりも「到達時間」に影響を与えることを示唆する。消化速度の異なる2種類の食品（単純糖質中心のスムージーと複合炭水化物中心のおにぎり）を同時に摂取した場合、胃内容物の複合化や胃排出速度の平均化などにより、吸収のタイミングが後ろ倒しになった可能性が考えられる。"),
  p("本選手の練習開始時刻は11:00であり、段階摂取条件のTmax（11:45）は練習開始から45分後に位置するのに対し、同時摂取条件のTmax（12:45）は練習開始から1時間45分後に位置する。エネルギー供給のタイミングを練習時間帯に近づけたい場合には、段階摂取の方が実践的に有利である可能性を示す結果であり、朝食と補食の摂取タイミング設計における示唆を持つ。"),
  p("なお、本比較には重要な限界がある。⚠ スムージー摂取条件（DAY4〜DAY6）は、後続の14日間連続血糖モニタリングで判明したDAY5（8/29）以降の血糖ベースラインシフトの影響を一部受けている（DAY4・DAY5はシフト前、DAY6のみシフト後）のに対し、おにぎり＋スムージー摂取条件（DAY8〜DAY10）は完全にシフト後に実施されている。両条件のベースライン血糖値自体に差があり（159.3 vs 164.3 mg/dL）、この交絡がTmax・ピーク値の比較結果に影響している可能性があるため、本結果は参考値として解釈する必要がある。また、各条件n=3日であり統計的検定は行っておらず、Tmaxは3日間平均曲線上の値であり個々の試行日のばらつきを反映できていない点も、限界として付記する。"),
]);

// ============ ③ おにぎり＋スムージー vs おにぎり＋糖質減 ============
const doc3 = buildDoc([
  titleParagraph("スムージーの糖質量の違い（通常 vs 糖質減）が血糖ピーク到達時間（Tmax）に及ぼす影響"),

  heading("背景", HeadingLevel.HEADING_1),
  p("朝食の糖質量は、血糖応答の大きさだけでなくピークに至るまでの時間にも影響しうる。一般に、糖質量を減らすことで血糖上昇は緩やかになり、ピーク到達も早まる、あるいはピーク自体が低くなることが期待される。"),
  p("本節では、おにぎり＋スムージー摂取条件（通常のPFCバランス）とおにぎり＋糖質減摂取条件（スムージーの糖質を減らしたPFCバランス）を比較し、糖質量の違いが血糖ピーク到達時間（Tmax）に及ぼす影響を検討した。"),

  heading("方法", HeadingLevel.HEADING_1),
  p("対象は高位脊髄損傷を有する車いす陸上競技選手1名である。おにぎり＋スムージー摂取条件（DAY8〜DAY10、通常）およびおにぎり＋糖質減摂取条件（DAY11〜DAY13、スムージーの糖質量を減らしたPFCバランス）とも、8:00におにぎりとスムージーを同時に摂取するプロトコルは共通であり、スムージーの糖質量（PFCバランス）のみが異なる。両条件ともFreeStyleリブレによる持続血糖モニタリングを行い、15分間隔で血糖値を記録した。"),
  p("両条件は摂取様式が共通しているため、8:00〜14:00の全記録区間を解析対象とし、ピーク到達時刻（Tmax）、ピーク血糖値、およびベースラインからの増加量（Δピーク）を算出した。"),

  heading("結果", HeadingLevel.HEADING_1),
  p("おにぎり＋スムージー摂取条件（通常）ではTmaxは摂取後4時間45分（12:45）であり、ピーク血糖値は242.3 mg/dL、Δピークは78.0 mg/dLであった。おにぎり＋糖質減摂取条件ではTmaxは摂取後5時間30分（13:30）であり、ピーク血糖値は250.3 mg/dL、Δピークは84.3 mg/dLであった（表1）。"),
  p("糖質減条件の方がTmaxは45分遅く、ピーク血糖値・Δピークもやや高い値を示した。"),
  tableCaption("表1　おにぎり＋スムージー（通常）・おにぎり＋糖質減条件におけるTmax（8:00〜14:00）"),
  resultsTable([
    ["おにぎり＋スムージー（通常）", "摂取後4時間45分（12:45）", "242.3 mg/dL", "78.0 mg/dL"],
    ["おにぎり＋糖質減", "摂取後5時間30分（13:30）", "250.3 mg/dL", "84.3 mg/dL"],
  ]),

  heading("考察", HeadingLevel.HEADING_1),
  p("糖質量を減らすことで血糖応答が緩やかになる、またはピークが低くなることが予想されたが、本結果はその予想とは逆の傾向を示した。考えられる要因として、第一に、スムージーの糖質を減らした分、相対的に脂質・たんぱく質の比率が増加し、脂質による胃排出遅延効果により、糖質の吸収自体が後ろ倒しになり、かつ緩徐に持続的な上昇を示した可能性が考えられる。第二に、おにぎり＋糖質減条件（DAY11〜DAY13）は、血糖ベースラインシフト（DAY5以降）の発生からより長い期間が経過した時期に実施されており、シフトの影響がこの時期にさらに蓄積・悪化していた可能性も否定できない。第三に、n=3日という少数の試行における日差（体調・練習強度等）が、たまたま糖質減条件側に偏った可能性も考えられる。"),
  p("✓ 本比較は、おにぎり＋スムージー条件・おにぎり＋糖質減条件のいずれもDAY8〜DAY13、すなわち血糖ベースラインシフト後の期間に実施されており、両条件のベースライン血糖値（164.3 vs 166.0 mg/dL）もほぼ同等であった。そのため、固形vsスムージー・スムージーvsおにぎり＋スムージーの比較と異なり、本比較はシフトによる系統的な交絡を受けにくく、観察された差は条件間の実質的な違い、またはランダムな日差を反映している可能性が高いと考えられる。"),
  p("ただし、本結果はn=3日の記述的傾向にとどまり、統計的に有意な差であるとは言えない点、Tmaxが3日間平均曲線上の値であり個々の試行日のばらつきを反映できていない点は、他の比較と同様の限界として付記する必要がある。"),
]);

Packer.toBuffer(doc2).then((buf) => { require("fs").writeFileSync("output_tmax2.docx", buf); console.log("done2"); });
Packer.toBuffer(doc3).then((buf) => { require("fs").writeFileSync("output_tmax3.docx", buf); console.log("done3"); });
