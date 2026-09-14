"""Recompute glucose metrics (delta-peak, incremental AUC, CV, etc.) from
analysis/data/glucose_raw.csv.

Source data: 15-min blood glucose readings for 4 breakfast conditions
(solid / smoothie / onigiri+smoothie / onigiri+reduced-carb), averaged
across the 3 test days per condition. Extracted from the athlete's
"赤字区間_AUC分析 (まとめ2h)" sheet.

Run: python3 compute_metrics.py
"""
import numpy as np
import pandas as pd

df = pd.read_csv("../data/glucose_raw.csv", index_col=0)
df.index = pd.to_datetime(df.index, format="%H:%M:%S")
t_min = (df.index - df.index[0]).total_seconds() / 60.0

results = {}
for cond in df.columns:
    y = df[cond].values
    baseline = y[0]
    peak = y.max()
    y_incr = np.clip(y - baseline, 0, None)
    mask_2h = t_min <= 120

    results[cond] = dict(
        baseline=baseline,
        peak=peak,
        delta_peak=peak - baseline,
        mean_6h=y.mean(),
        sd_6h=y.std(ddof=1),
        cv_pct=y.std(ddof=1) / y.mean() * 100,
        auc_raw_6h=np.trapezoid(y, t_min),
        iauc_6h=np.trapezoid(y_incr, t_min),
        auc_raw_2h=np.trapezoid(y[mask_2h], t_min[mask_2h]),
        iauc_2h=np.trapezoid(y_incr[mask_2h], t_min[mask_2h]),
        late_mean_4_6h=y[t_min >= 240].mean(),
    )

out = pd.DataFrame(results).T
print(out.round(1))
out.to_csv("../data/glucose_metrics.csv")
