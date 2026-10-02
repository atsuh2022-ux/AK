const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, AlignmentType, BorderStyle, VerticalAlign
} = require("docx");

const FONT = "游明朝";
const HFONT = "游ゴシック";

function p(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 200, line: 360 },
    alignment: opts.align || AlignmentType.LEFT,
    children: [new TextRun({ text, font: FONT, size: 21, bold: !!opts.bold })],
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
    margins: { top: 100, bottom: 100, left: 150, right: 150 },
    children: [new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text, font: FONT, size: 21, bold: !!opts.bold })],
    })],
  });
}

const colW = [3200, 3200, 3200];
const tableWidth = colW.reduce((a, b) => a + b, 0);

const resultsTable = new Table({
  width: { size: tableWidth, type: WidthType.DXA },
  columnWidths: colW,
  rows: [
    new TableRow({
      tableHeader: true,
      children: [
        cell("条件", { width: colW[0], shade: "21295C", bold: true }),
        cell("Tmax", { width: colW[1], shade: "21295C", bold: true }),
        cell("ピーク血糖値", { width: colW[2], shade: "21295C", bold: true }),
      ],
    }),
    new TableRow({
      children: [
        cell("固形摂取", { width: colW[0], shade: "F4F7F9" }),
        cell("摂取後30分（8:30）", { width: colW[1], shade: "F4F7F9" }),
        cell("133.3 mg/dL", { width: colW[2], shade: "F4F7F9" }),
      ],
    }),
    new TableRow({
      children: [
        cell("スムージー摂取", { width: colW[0] }),
        cell("摂取後45分（8:45）", { width: colW[1] }),
        cell("202.7 mg/dL", { width: colW[2] }),
      ],
    }),
  ],
});

const doc = new Document({
  styles: {
    default: {
      document: { run: { font: FONT, size: 21 } },
    },
  },
  sections: [
    {
      properties: {
        page: { size: { width: 11906, height: 16838 } }, // A4
      },
      children: [
        new Paragraph({
          spacing: { after: 400 },
          children: [new TextRun({ text: "朝食形態（固形食・スムージー）が血糖ピーク到達時間（Tmax）に及ぼす影響", font: HFONT, bold: true, size: 32 })],
        }),

        heading("背景", HeadingLevel.HEADING_1),
        p("脊髄損傷（SCI）、とりわけ高位胸髄損傷を有する車いすアスリートにおいては、受傷の高位によって消化管運動を調節する自律神経系（迷走神経・交感神経）に機能変化が生じうることが知られている。このため、健常者を対象とした一般的な栄養学的知見（固形食と液体食で胃排出速度・消化吸収速度が異なり、血糖応答の立ち上がり方が異なる、など）が、SCIアスリートにそのまま当てはまるとは限らない。"),
        p("本研究の対象選手においては、朝食の形態（固形食／スムージー）によって血糖値の立ち上がり方や到達するピーク値に違いが生じるかを明らかにすることを目的のひとつとした。特に、血糖値が最高値に達するまでの時間（Time to peak glucose; Tmax）は、摂取した栄養素の消化吸収速度を反映する代表的な指標であり、固形食とスムージーという物理的性状の異なる栄養摂取が、同一選手内でどの程度血糖応答速度に影響するかを定量的に検討した。"),

        heading("方法", HeadingLevel.HEADING_1),
        p("対象は高位脊髄損傷を有する車いす陸上競技選手1名である。固形摂取条件（DAY1〜DAY3）およびスムージー摂取条件（DAY4〜DAY6）の各3日間において、FreeStyleリブレによる持続血糖モニタリング（CGM）を実施した。各試行日とも8:00を栄養摂取直前の基準時刻とし、15分間隔で血糖値を記録した。"),
        p("本解析では、後続のおにぎり摂取（2品目の栄養摂取）が行われる10:00までの区間（8:00〜10:00）を解析対象とした。この区間に限定することで、2品目の摂取による血糖応答への影響を排除し、固形食またはスムージー単独の摂取に対する血糖応答を純粋に評価できるようにした。各条件につき3日分の血糖値を時刻ごとに平均し、得られた平均曲線上でのピーク血糖値とその到達時刻（Tmax）を算出した。"),

        heading("結果", HeadingLevel.HEADING_1),
        p("8:00〜10:00の区間における解析の結果、固形摂取条件ではTmaxは摂取後30分（8:30）であり、この時点でのピーク血糖値は133.3 mg/dLであった。一方、スムージー摂取条件ではTmaxは摂取後45分（8:45）であり、ピーク血糖値は202.7 mg/dLであった（表1）。"),
        p("両条件間のTmaxの差は15分にとどまり、血糖値が最高値に達するまでの時間には大きな差はみられなかった。一方で、ピーク血糖値には約70 mg/dLの差が認められ、スムージー摂取条件の方が固形摂取条件よりも高い血糖上昇を示した。"),
        new Paragraph({
          spacing: { before: 100, after: 100 },
          children: [new TextRun({ text: "表1　固形摂取・スムージー摂取条件におけるTmaxとピーク血糖値（8:00〜10:00）", font: FONT, size: 19, bold: true })],
        }),
        resultsTable,
        p("なお、8:00〜14:00の全区間でみると、両条件とも11時台から12時台にかけてより高い二次的なピーク（固形：11:30に152.7 mg/dL、スムージー：11:45に244.3 mg/dL）が観察されており、血糖応答が単峰性ではなく二峰性を呈する傾向が確認された。"),

        heading("考察", HeadingLevel.HEADING_1),
        p("本結果から、固形摂取とスムージー摂取との間でTmaxに大きな差が認められなかったことは、両条件における胃内滞留時間および消化吸収の立ち上がり速度に顕著な差がなかった可能性を示唆する。一般に液体栄養は固形栄養に比べて胃排出が速く、血糖上昇も早期に生じやすいとされるが、本選手ではそのような差は限定的であった。これは、高位脊髄損傷に伴う自律神経系の機能変化が消化管運動の調節に影響し、液体・固形間の消化速度差を縮小させた可能性、あるいは今回用いた固形食自体の組成（消化の良い食材選定等）が影響した可能性が考えられ、今後の検討課題である。"),
        p("一方で、ピーク血糖値には明確な差が認められた。これはTmax（速度）の差ではなく、血糖上昇の「量・勢い」の差として解釈すべきであり、スムージーに含まれる糖質がより急峻に血中へ取り込まれたこと、あるいは液体形態であることにより糖の溶解・拡散が容易であったことなどが要因として考えられる。この結果は、血糖応答を評価する際にTmaxとピーク値（あるいはΔピーク、AUC等）を区別して検討することの重要性を示している。"),
        p("また、両条件で共通してみられた11時台以降の二次ピークについては、本データのみからその要因を特定することはできない。この時間帯は練習や追加の補食が想定される時間帯と重なっており、運動に伴う血糖動員（カウンターレギュレーションホルモンの分泌）や、記録されていない追加摂取などが関与した可能性がある。"),
        p("最後に、本研究にはいくつかの限界がある。第一に、各条件n=3日と試行数が少なく、統計的検定を行うに足るサンプルサイズではないため、本結果は記述的・探索的な傾向として扱う必要がある。第二に、算出したTmaxは3日間の血糖値を時刻ごとに平均した曲線上のピークであり、個々の試行日におけるピーク到達時刻のばらつきを反映できていない可能性がある。第三に、後続して実施した14日間の連続血糖モニタリングにより、DAY5（8/29）以降に血糖のベースラインが持続的に上昇する現象が確認されており、スムージー条件（DAY4〜DAY6）はこのシフトの前後が混在する期間に実施されているため、結果が部分的に交絡している可能性を否定できない。これに対し固形条件（DAY1〜DAY3）はシフト以前に完全に含まれるため、この限りでは両条件の比較可能性は一定程度保たれていると考えられるが、解釈には留保が必要である。"),
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buf) => {
  require("fs").writeFileSync("output_tmax.docx", buf);
  console.log("done");
});
