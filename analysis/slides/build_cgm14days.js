const pptxgen = require("pptxgenjs");

const NAVY = "21295C";
const DEEPBLUE = "065A82";
const TEAL = "1C7293";
const WHITE = "FFFFFF";
const INK = "1A1A1A";
const MUTED = "5C6570";
const CARDBG = "F4F7F9";

const C_SOLID = "2A78D6";
const C_SMOOTHIE = "EB6834";
const C_ONIGISMO = "1BAF7A";
const C_LOWSUGAR = "EDA100";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: "Cambria", bodyFontFace: "Calibri" };
const W = 13.33, H = 7.5, MARGIN = 0.6;

function addFooter(slide, note, dark) {
  slide.addText(note, { x: MARGIN, y: H - 0.4, w: W - MARGIN * 2, h: 0.28, fontFace: "Calibri", fontSize: 9.5, color: dark ? "9AA6C4" : MUTED, align: "left" });
}
function titleBlock(slide, kicker, title, dark) {
  slide.addText(kicker, { x: MARGIN, y: 0.42, w: W - MARGIN * 2, h: 0.34, fontFace: "Calibri", fontSize: 12.5, bold: true, color: dark ? "8FB7E0" : TEAL, charSpacing: 1, isTextBox: true });
  slide.addText(title, { x: MARGIN, y: 0.74, w: W - MARGIN * 2, h: 0.65, fontFace: "Cambria", fontSize: 26, bold: true, color: dark ? WHITE : NAVY, isTextBox: true });
}

// ================= 1: Title =================
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  s.addShape("rect", { x: 0, y: 0, w: W, h: H, fill: { color: NAVY } });
  s.addShape("oval", { x: 10.6, y: -1.6, w: 5.5, h: 5.5, fill: { color: DEEPBLUE, transparency: 55 }, line: { type: "none" } });
  s.addShape("oval", { x: -2.0, y: 4.6, w: 4.6, h: 4.6, fill: { color: TEAL, transparency: 60 }, line: { type: "none" } });

  s.addText("FreeStyleリブレ 24時間連続測定", { x: MARGIN, y: 2.1, w: 11, h: 0.4, fontFace: "Calibri", fontSize: 15, bold: true, color: "8FB7E0", charSpacing: 1, isTextBox: true });
  s.addText("14日間連続CGMデータ分析", { x: MARGIN, y: 2.55, w: 11.5, h: 1.0, fontFace: "Cambria", fontSize: 38, bold: true, color: WHITE, isTextBox: true });
  s.addText("DAY準備〜DAY14（8/24〜9/7）の24時間血糖データから分かったこと", { x: MARGIN, y: 3.55, w: 11, h: 0.5, fontFace: "Calibri", fontSize: 16, color: "CADCFC", isTextBox: true });

  const stats = [["1,432", "血糖測定点"], ["15", "測定日数(日)"], ["0", "低血糖(70未満)件数"]];
  let sx = MARGIN;
  stats.forEach(([n, l]) => {
    s.addText(n, { x: sx, y: 4.8, w: 2.6, h: 0.7, fontFace: "Cambria", fontSize: 34, bold: true, color: WHITE, isTextBox: true, margin: 0 });
    s.addText(l, { x: sx, y: 5.5, w: 3.0, h: 0.4, fontFace: "Calibri", fontSize: 12, color: "9AA6C4", isTextBox: true, margin: 0 });
    sx += 3.4;
  });
  s.addText("対象：高位脊髄損傷（SCI）車いす陸上選手 1名", {
    x: MARGIN, y: 6.85, w: 10, h: 0.35, fontFace: "Calibri", fontSize: 10.5, italic: true, color: "9AA6C4", isTextBox: true
  });
}

// ================= 2: データについて =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "METHOD", "今回のデータについて", false);

  const items = [
    { t: "測定機器・期間", d: "FreeStyleリブレLink（間欠スキャン式CGM）。2026/8/24 20:21〜9/7 20:22の連続記録。センサーは1本のみ使用（途中交換なし）。" },
    { t: "これまでの分析との違い", d: "従来は各条件の8:00〜14:00のみを比較していたが、今回は24時間×14日間の全データを分析。夜間・自由摂取後・練習後を含む生活全体の血糖動態が見える。" },
    { t: "測定間隔", d: "自動記録（過去のグルコース値）は約15分間隔。手動スキャンも含め、期間全体で1,432点の血糖データを取得。" },
  ];
  let y = 2.0;
  items.forEach(it => {
    s.addShape("roundRect", { x: MARGIN, y, w: W - MARGIN * 2, h: 1.3, rectRadius: 0.1, fill: { color: CARDBG }, line: { type: "none" } });
    s.addText(it.t, { x: MARGIN + 0.3, y: y + 0.18, w: W - MARGIN * 2 - 0.6, h: 0.35, fontFace: "Calibri", fontSize: 15, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    s.addText(it.d, { x: MARGIN + 0.3, y: y + 0.58, w: W - MARGIN * 2 - 0.6, h: 0.65, fontFace: "Calibri", fontSize: 12.5, color: MUTED, isTextBox: true, margin: 0 });
    y += 1.55;
  });
}

// ================= 3: 14日間の血糖トレンド =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "RESULTS", "14日間の血糖トレンド", false);

  const dayLabels = ["準備", "DAY1", "DAY2", "DAY3", "DAY4", "DAY5", "DAY6", "DAY7", "DAY8", "DAY9", "DAY10", "DAY11", "DAY12", "DAY13", "DAY14"];
  const dayMeanAll = [141.2, 126.7, 117.6, 119.0, 126.0, 160.7, 208.9, 210.8, 196.0, 189.1, 191.0, 204.5, 187.3, 174.2, 184.2];
  const dayMeanNight = [null, 106.6, 93.4, 93.9, 96.5, 104.2, 176.7, 176.8, 160.5, 152.7, 152.2, 165.8, 161.8, 129.8, 152.0];

  s.addChart("line", [
    { name: "終日平均血糖", labels: dayLabels, values: dayMeanAll },
    { name: "夜間(0-6時)平均血糖", labels: dayLabels, values: dayMeanNight },
  ], {
    x: MARGIN, y: 1.7, w: W - MARGIN * 2, h: 4.55,
    chartColors: [C_SMOOTHIE, C_SOLID],
    lineSize: 2.5, lineDataSymbol: "circle", lineDataSymbolSize: 5,
    showTitle: false, showLegend: true, legendPos: "b", legendFontSize: 12, legendColor: INK,
    catAxisLabelColor: MUTED, catAxisLabelFontSize: 10,
    valAxisLabelColor: MUTED, valAxisLabelFontSize: 10,
    valAxisTitle: "血糖値 (mg/dL)", showValAxisTitle: true, valAxisTitleFontSize: 11, valAxisTitleColor: MUTED,
    valGridLine: { color: "E3E1DB", size: 0.75 }, catGridLine: { style: "none" },
    catAxisLineColor: "E3E1DB", valAxisLineColor: "E3E1DB"
  });
  addFooter(s, "DAY5(8/29)を境に、終日平均・夜間平均とも明確な段差が生じ、以後高い水準で推移している。", false);
}

// ================= 4: 良い知らせ =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "RESULTS", "良い知らせ：低血糖は一度も検出されず", false);

  s.addShape("roundRect", { x: MARGIN, y: 1.9, w: W - MARGIN * 2, h: 1.7, rectRadius: 0.12, fill: { color: "EAF7F0" }, line: { color: C_ONIGISMO, width: 1.25 } });
  s.addText("✓", { x: MARGIN + 0.35, y: 2.15, w: 1.0, h: 1.1, fontFace: "Cambria", fontSize: 50, bold: true, color: "0F5C3D", isTextBox: true, margin: 0 });
  s.addText("14日間・1,432測定点を通じ、低血糖（70 mg/dL未満）は日中・夜間問わず一度も検出されませんでした。", {
    x: MARGIN + 1.5, y: 2.15, w: W - MARGIN * 2 - 1.8, h: 1.35, valign: "middle", fontFace: "Calibri", fontSize: 16, bold: true, color: "0F5C3D", isTextBox: true, margin: 0
  });

  s.addText("これまで断片的な時間帯（8:00〜14:00）だけで判断していた「反応性低血糖のリスクなし」を、24時間データで裏付けられました。研究背景にある「血糖スパイク＋反応性低血糖」のうち、少なくとも低血糖側のリスクは実測ベースで否定されます。", {
    x: MARGIN, y: 3.9, w: W - MARGIN * 2, h: 0.8, fontFace: "Calibri", fontSize: 13, color: INK, isTextBox: true, margin: 0
  });

  const panelW = (W - MARGIN * 2 - 0.4) / 2;
  s.addShape("roundRect", { x: MARGIN, y: 4.9, w: panelW, h: 1.75, rectRadius: 0.1, fill: { color: CARDBG }, line: { type: "none" } });
  s.addText("低血糖(70未満)", { x: MARGIN + 0.25, y: 5.05, w: panelW - 0.5, h: 0.3, fontFace: "Calibri", fontSize: 12.5, bold: true, color: NAVY, isTextBox: true, margin: 0 });
  s.addText("0件", { x: MARGIN + 0.25, y: 5.35, w: panelW - 0.5, h: 0.7, fontFace: "Cambria", fontSize: 36, bold: true, color: C_ONIGISMO, isTextBox: true, margin: 0 });
  s.addText("/ 1,432測定点中", { x: MARGIN + 0.25, y: 6.05, w: panelW - 0.5, h: 0.3, fontFace: "Calibri", fontSize: 10.5, color: MUTED, isTextBox: true, margin: 0 });

  s.addShape("roundRect", { x: MARGIN + panelW + 0.4, y: 4.9, w: panelW, h: 1.75, rectRadius: 0.1, fill: { color: CARDBG }, line: { type: "none" } });
  s.addText("高血糖(250超)", { x: MARGIN + panelW + 0.65, y: 5.05, w: panelW - 0.5, h: 0.3, fontFace: "Calibri", fontSize: 12.5, bold: true, color: NAVY, isTextBox: true, margin: 0 });
  s.addText("81件", { x: MARGIN + panelW + 0.65, y: 5.35, w: panelW - 0.5, h: 0.7, fontFace: "Cambria", fontSize: 36, bold: true, color: C_LOWSUGAR, isTextBox: true, margin: 0 });
  s.addText("大半がDAY5・6・7・11に集中", { x: MARGIN + panelW + 0.65, y: 6.05, w: panelW - 0.5, h: 0.3, fontFace: "Calibri", fontSize: 10.5, color: MUTED, isTextBox: true, margin: 0 });
}

// ================= 5: DAY5に何が起きたか =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "KEY FINDING", "DAY5(8/29)午後に何が起きたか", false);
  s.addText("14:50頃を境に血糖が急上昇し、翌朝になっても下がりきりませんでした（30分間隔、8/29 12:00〜8/30 8:00）。", {
    x: MARGIN, y: 1.6, w: W - MARGIN * 2, h: 0.4, fontFace: "Calibri", fontSize: 12, color: MUTED, isTextBox: true, margin: 0
  });

  const times30 = ["12:00","12:30","13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00","19:30","20:00","20:30","21:00","21:30","22:00","22:30","23:00","23:30","0:00","0:30","1:00","1:30","2:00","2:30","3:00","3:30","4:00","4:30","5:00","5:30","6:00","6:30","7:00","7:30","8:00"];
  const vals30 = [152,146,156,149,154,150,225,253,216,239,264,222,192,201,181,178,285,256,260,238,216,212,225,200,193,212,184,204,188,176,179,172,163,154,153,164,164,165,203,184,191];

  s.addChart("line", [{ name: "血糖値", labels: times30, values: vals30 }], {
    x: MARGIN, y: 2.05, w: W - MARGIN * 2, h: 3.4,
    chartColors: [C_LOWSUGAR],
    lineSize: 2, lineDataSymbol: "none",
    showTitle: false, showLegend: false,
    catAxisLabelColor: MUTED, catAxisLabelFontSize: 8, catAxisLabelFrequency: 4, catAxisLabelRotate: 45,
    valAxisLabelColor: MUTED, valAxisLabelFontSize: 9,
    valAxisTitle: "血糖値(mg/dL)", showValAxisTitle: true, valAxisTitleFontSize: 9, valAxisTitleColor: MUTED,
    valGridLine: { color: "E3E1DB", size: 0.75 }, catGridLine: { style: "none" },
    catAxisLineColor: "E3E1DB", valAxisLineColor: "E3E1DB"
  });

  s.addShape("roundRect", { x: MARGIN, y: 5.65, w: W - MARGIN * 2, h: 1.2, rectRadius: 0.1, fill: { color: "FDF3E2" }, line: { color: "EDA100", width: 1 } });
  s.addText("14:50に175→15:20には270まで急上昇。そのまま夜通し200前後を推移し、翌朝8時になっても191と下がりきらない。通常の食事1回分の反応では説明できない持続性。", {
    x: MARGIN + 0.25, y: 5.8, w: W - MARGIN * 2 - 0.5, h: 0.9, fontFace: "Calibri", fontSize: 12, bold: true, color: "6B4B00", isTextBox: true, margin: 0
  });
  addFooter(s, "この日は自由摂取の午後で、被験食プロトコルの対象外の時間帯。", false);
}

// ================= 6: 原因の候補 =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "DISCUSSION", "原因の候補（データからは特定できず）", false);

  const causes = [
    { t: "記録されていない間食・夕食", d: "CGMアプリの食事ログ機能はほとんど使われておらず（食事メモの記載は14日間で数件のみ）、この時間帯に何を食べたか確認できない。", c: C_SOLID },
    { t: "体調不良・感染症の初期症状", d: "ストレスホルモン（コルチゾール等）による持続的な高血糖は、体調不良の初期に典型的に見られるパターン。", c: C_SMOOTHIE },
    { t: "蓄積した練習・精神的ストレス", d: "翌朝（DAY6 9:17）のメモに「7時にドーピング検査があった」との記載あり。前夜からの緊張状態が影響した可能性。", c: C_ONIGISMO },
    { t: "その他の生活要因", d: "記録に残っていない睡眠の乱れ、水分摂取量の変化等、CGMデータだけでは把握できない要因。", c: MUTED },
  ];
  let y = 1.9;
  causes.forEach((c, i) => {
    s.addShape("oval", { x: MARGIN, y, w: 0.42, h: 0.42, fill: { color: c.c }, line: { type: "none" } });
    s.addText(String(i + 1), { x: MARGIN, y, w: 0.42, h: 0.42, align: "center", valign: "middle", fontFace: "Cambria", fontSize: 14, bold: true, color: WHITE, isTextBox: true, margin: 0 });
    s.addText(c.t, { x: MARGIN + 0.65, y: y - 0.02, w: 11.3, h: 0.32, fontFace: "Calibri", fontSize: 14, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    s.addText(c.d, { x: MARGIN + 0.65, y: y + 0.3, w: 11.3, h: 0.6, fontFace: "Calibri", fontSize: 12, color: MUTED, isTextBox: true, margin: 0 });
    y += 1.2;
  });
  addFooter(s, "選手・スタッフへの聞き取りが、原因特定に向けた最も費用対効果の高い次の一手。", false);
}

// ================= 7: 4条件比較への影響 =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "IMPACT", "これまでの4条件比較への影響", false);
  s.addText("固形／スムージー／おにぎり＋スムージー／おにぎり＋糖質減の比較は、DAY1〜13にまたがって実施されていたため、比較によって信頼度が異なる。", {
    x: MARGIN, y: 1.6, w: W - MARGIN * 2, h: 0.5, fontFace: "Calibri", fontSize: 12.5, color: MUTED, isTextBox: true, margin: 0
  });

  const rows = [
    [{ text: "比較", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "シフトとの関係", options: { bold: true, color: WHITE, fill: { color: NAVY } } },
     { text: "信頼度", options: { bold: true, color: WHITE, fill: { color: NAVY } } }],
    ["① 固形 vs スムージー", "固形(DAY1〜3)は完全にシフト前。スムージー(DAY4〜6)はDAY4・5がシフト前、DAY6のみシフト後で3日平均が引っ張られている可能性", "⚠ 要注意"],
    ["② スムージー vs おにぎり＋スムージー", "スムージー側はシフト前後が混在。おにぎり＋スムージー(DAY8〜10)は完全にシフト後", "⚠ 要注意"],
    ["③ おにぎり＋スムージー vs 糖質減", "両条件(DAY8〜13)とも完全にシフト後で条件が揃っている", "✓ 信頼できる"],
  ].map((r, i) => i === 0 ? r : r.map((c, j) => ({
    text: c, options: { color: j === 0 ? NAVY : (j === 2 ? (c.startsWith("✓") ? "0F5C3D" : "6B4B00") : INK), bold: j === 0 || j === 2, fill: { color: i % 2 === 0 ? CARDBG : WHITE }, fontSize: 12 }
  })));
  s.addTable(rows, {
    x: MARGIN, y: 2.2, w: W - MARGIN * 2, h: 2.4,
    fontFace: "Calibri", fontSize: 12, border: { type: "solid", color: "E3E1DB", pt: 0.75 },
    autoPage: false, valign: "middle", rowH: 0.6,
    colW: [3.3, 6.53, 2.3]
  });

  s.addShape("roundRect", { x: MARGIN, y: 4.9, w: W - MARGIN * 2, h: 1.9, rectRadius: 0.1, fill: { color: "EAF7F0" }, line: { type: "none" } });
  s.addText(
    "✓ 最も重要な結果（③糖質量の比較、iAUC 39%減）はシフトの影響を受けず維持できる。①・②で見られた「固形の方が安定」「スムージー単独は乱高下が大きい」という結果は、一部がタイミング（シフト前後の混在）による見かけ上のものである可能性があり、割り引いて解釈する必要がある。",
    { x: MARGIN + 0.3, y: 5.1, w: W - MARGIN * 2 - 0.6, h: 1.6, fontFace: "Calibri", fontSize: 12.5, bold: true, color: "0F5C3D", isTextBox: true, margin: 0 }
  );
}

// ================= 8: その他の観察 =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "OBSERVATIONS", "その他に観察された傾向（参考値, n=14）", false);

  const items = [
    { t: "体重は安定", d: "62.1〜63.4kgの範囲で14日間を通じ大きな変動なし。", c: C_SOLID, sign: "◯" },
    { t: "血糖の変動が小さい日ほど、翌朝の起床時コンディションが良い傾向", d: "CV（変動係数）と起床時コンディションの相関 r=-0.41。血糖の乱高下は主観的な体調にも表れている可能性。", c: C_ONIGISMO, sign: "◯" },
    { t: "血糖の絶対的なばらつきが小さい日ほど、爆発力の自己評価が高い傾向", d: "SD（標準偏差）と爆発力の相関 r=-0.48。「なだらかな血糖の方が良い」というこれまでの考察と整合。", c: C_ONIGISMO, sign: "◯" },
    { t: "夜間血糖と起床時コンディションの正の相関は要注意", d: "相関 r=0.71と高いが、両者とも同じ14日間トレンド（DAY5以降の上昇）に乗っているだけの見かけ上の相関の可能性が高い。因果関係とは解釈しない。", c: C_LOWSUGAR, sign: "△" },
  ];
  let y = 1.85;
  items.forEach(it => {
    s.addShape("oval", { x: MARGIN, y: y + 0.02, w: 0.4, h: 0.4, fill: { color: it.c }, line: { type: "none" } });
    s.addText(it.sign, { x: MARGIN, y: y + 0.02, w: 0.4, h: 0.4, align: "center", valign: "middle", fontFace: "Cambria", fontSize: 16, bold: true, color: WHITE, isTextBox: true, margin: 0 });
    s.addText(it.t, { x: MARGIN + 0.6, y, w: 11.3, h: 0.34, fontFace: "Calibri", fontSize: 13.5, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    s.addText(it.d, { x: MARGIN + 0.6, y: y + 0.33, w: 11.3, h: 0.55, fontFace: "Calibri", fontSize: 11.5, color: MUTED, isTextBox: true, margin: 0 });
    y += 1.25;
  });
  addFooter(s, "n=14の記述的傾向。統計的検定ではなく参考情報として解釈。", false);
}

// ================= 8.5: なぜこの相関が起きたのか =================
{
  const s = pres.addSlide();
  s.background = { color: WHITE };
  titleBlock(s, "DISCUSSION", "なぜこの相関が起きたのか：仮説とエビデンス", false);

  s.addShape("roundRect", { x: MARGIN, y: 1.55, w: W - MARGIN * 2, h: 1.2, rectRadius: 0.1, fill: { color: "FDF3E2" }, line: { color: "EDA100", width: 1 } });
  s.addText("⚠ 最優先で疑うべき解釈：交絡（見せかけの相関）", {
    x: MARGIN + 0.3, y: 1.68, w: W - MARGIN * 2 - 0.6, h: 0.3, fontFace: "Calibri", fontSize: 13, bold: true, color: "6B4B00", isTextBox: true, margin: 0
  });
  s.addText("DAY5以降、血糖変動の拡大とコンディション低下が同時進行。体調不良・疲労など共通の要因が両方を引き起こしているだけの可能性が高く、r=-0.41・-0.48程度の相関はこれだけで説明できる。", {
    x: MARGIN + 0.3, y: 2.0, w: W - MARGIN * 2 - 0.6, h: 0.65, fontFace: "Calibri", fontSize: 11, color: "6B4B00", isTextBox: true, margin: 0
  });

  const cards = [
    { n: "①", t: "睡眠の質への影響", d: "夜間の急な血糖変動が中途覚醒を誘発し、翌朝のコンディションを下げる可能性（CGM併用の睡眠研究で報告あり）", c: C_SOLID },
    { n: "②", t: "自律神経系への負荷", d: "血糖を戻すためのホルモン動員（グルカゴン等）が交感神経を優位にし、夜間の回復を妨げる可能性。SCIでは自律神経調節自体も脆弱", c: C_SMOOTHIE },
    { n: "③", t: "酸化ストレス", d: "平均血糖が同じでも変動幅が大きいほど酸化ストレスが増えることが糖尿病領域で報告されている（Monnierら）。慢性的な疲労感につながりうる経路", c: C_ONIGISMO },
    { n: "④", t: "「爆発力」評価は間接指標の可能性", d: "瞬発力はATP-PCr系が主体で血糖に直接依存しにくい。血糖の安定＝生活リズムが整っている日、という間接的な心理指標である可能性が高い", c: C_LOWSUGAR },
  ];
  const cardW = (W - MARGIN * 2 - 0.3) / 2;
  const cardH = 1.55;
  cards.forEach((c, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = MARGIN + col * (cardW + 0.3);
    const y = 2.95 + row * (cardH + 0.25);
    s.addShape("roundRect", { x, y, w: cardW, h: cardH, rectRadius: 0.08, fill: { color: CARDBG }, line: { type: "none" } });
    s.addShape("oval", { x: x + 0.22, y: y + 0.2, w: 0.36, h: 0.36, fill: { color: c.c }, line: { type: "none" } });
    s.addText(c.n, { x: x + 0.22, y: y + 0.2, w: 0.36, h: 0.36, align: "center", valign: "middle", fontFace: "Cambria", fontSize: 12, bold: true, color: WHITE, isTextBox: true, margin: 0 });
    s.addText(c.t, { x: x + 0.72, y: y + 0.18, w: cardW - 0.95, h: 0.34, fontFace: "Calibri", fontSize: 12.5, bold: true, color: NAVY, isTextBox: true, margin: 0 });
    s.addText(c.d, { x: x + 0.22, y: y + 0.62, w: cardW - 0.45, h: 0.88, fontFace: "Calibri", fontSize: 10.5, color: MUTED, isTextBox: true, margin: 0 });
  });

  s.addShape("roundRect", { x: MARGIN, y: 6.5, w: W - MARGIN * 2, h: 0.8, rectRadius: 0.1, fill: { color: CARDBG }, line: { color: TEAL, width: 1 } });
  s.addText("結論：本データはあくまで相関（n=14）であり、因果関係を示すエビデンスではない。検証にはDAY5要因の特定後、条件を統制した再検証が必要。", {
    x: MARGIN + 0.3, y: 6.62, w: W - MARGIN * 2 - 0.6, h: 0.56, valign: "middle", fontFace: "Calibri", fontSize: 12, bold: true, color: NAVY, isTextBox: true, margin: 0
  });
}

// ================= 9: まとめ・推奨アクション =================
{
  const s = pres.addSlide();
  s.background = { color: NAVY };
  titleBlock(s, "CONCLUSION", "まとめと推奨アクション", true);

  const concl = [
    "14日間・1,432測定点を通じ、低血糖（70mg/dL未満）は一度も検出されなかった（安全面の朗報）",
    "DAY5(8/29)14:50頃から血糖ベースラインが持続的に上昇し、以後DAY14まで元の水準に戻らなかった（原因不明）",
    "この結果、①固形vsスムージー・②タイミングの比較結論は参考値、③糖質量の比較（最重要結果）は結論を維持できる",
  ];
  let y = 1.9;
  concl.forEach((c, i) => {
    s.addShape("oval", { x: MARGIN, y, w: 0.42, h: 0.42, fill: { color: "1C7293" }, line: { type: "none" } });
    s.addText(String(i + 1), { x: MARGIN, y, w: 0.42, h: 0.42, align: "center", valign: "middle", fontFace: "Cambria", fontSize: 14, bold: true, color: WHITE, isTextBox: true, margin: 0 });
    s.addText(c, { x: MARGIN + 0.65, y: y - 0.02, w: 11.3, h: 0.85, fontFace: "Calibri", fontSize: 14, color: "E8EDF7", isTextBox: true, margin: 0, valign: "middle" });
    y += 1.15;
  });

  s.addShape("roundRect", { x: MARGIN, y: 5.55, w: W - MARGIN * 2, h: 1.3, rectRadius: 0.1, fill: { color: "1A2350" }, line: { type: "none" } });
  s.addText("推奨アクション：選手・スタッフに「8/29 14:30〜15:30頃、普段と違うこと（補食・体調の変化・ストレスの多い出来事）がなかったか」を確認する。コスト0・即実施可能で、原因が判明すれば①②の結論を再評価できる。", {
    x: MARGIN + 0.3, y: 5.7, w: W - MARGIN * 2 - 0.6, h: 1.0, valign: "middle", fontFace: "Calibri", fontSize: 13, bold: true, color: "E8EDF7", isTextBox: true, margin: 0
  });
  addFooter(s, "データ出典：14日間_for_AI.xlsx（FreeStyleリブレ連続血糖データ）／condition_app_2026-08-25_2026-09-07.xlsx", true);
}

pres.writeFile({ fileName: "output_cgm14days.pptx" }).then(() => console.log("done"));
