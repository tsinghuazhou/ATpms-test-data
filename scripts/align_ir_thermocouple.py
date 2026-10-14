"""Align IR camera (top-surface max temp) with thermocouple log, Gyroid 30W 2026-10-14.

Wall-clock alignment only. Lag is estimated and REPORTED but NOT applied
(decision 2026-10-15: residual lag is within +-1s uncertainty at 1Hz).
Outputs:
  aligned_gyroid30w_20261014.csv
    时间, T1..T5, B均值 (mean of T2/T3/T5, project convention drops T4),
    ir_max (mean of valid IR samples in [t-0.5s, t+0.5s]; empty if none),
    ir_n   (count of valid IR samples in that window).
  lag_profile_gyroid30w_20261014.csv
    lag_s, corr_T1 (d/dt cross-corr of T1 vs ir_max), corr_B (B均值 vs ir_max).
    Report-only diagnostic; not applied to the aligned table.
"""
import numpy as np
import pandas as pd

IR = "tpms_gyroid30w_20261014_183450_ir.csv"
TC = "tpms_gyroid30w_20261014_183455.csv"
OUT = "aligned_gyroid30w_20261014.csv"
OUT_LAG = "lag_profile_gyroid30w_20261014.csv"

# --- load IR: 2 metadata rows; "freeze frame" rows carry invalid 0.0 ---
ir = pd.read_csv(IR, skiprows=2, header=None, encoding="utf-8-sig",
                 names=["time", "elapsed", "ir_max", "ir_min"])
ir["freeze"] = ir["time"].str.strip().str.startswith("freeze frame")
ir["time"] = ir["time"].str.replace("freeze frame ", "", regex=False).str.strip()
ir["time"] = pd.to_datetime(ir["time"])
for c in ("ir_max", "ir_min"):
    ir[c] = pd.to_numeric(ir[c], errors="coerce")
ir.loc[ir["freeze"], ["ir_max", "ir_min"]] = np.nan
n_raw = len(ir)
ir = (ir.drop_duplicates(subset="time", keep="first")
        .sort_values("time").reset_index(drop=True))
print(f"IR: {n_raw} rows -> {len(ir)} unique timestamps "
      f"({n_raw - len(ir)} duplicates dropped); "
      f"freeze rows -> NaN: {int(ir['freeze'].sum())}")

# --- load thermocouples (utf-8-sig; header 时间,T1..T5) ---
tc = pd.read_csv(TC, encoding="utf-8-sig")
tc.columns = ["time"] + [f"T{i}" for i in range(1, len(tc.columns))]
tc["time"] = pd.to_datetime(tc["time"])
tc["B均值"] = tc[["T2", "T3", "T5"]].mean(axis=1)
print(f"TC: {len(tc)} rows, B均值 = mean(T2,T3,T5) per project convention")

# --- merge onto TC 1Hz grid: window [t-0.5s, t+0.5s] ---
ir_t = ir["time"].values
ir_v = ir["ir_max"].values.astype(float)
n_any, ir_max_col, ir_n_col = [], [], []
for t in tc["time"].values:
    lo = np.searchsorted(ir_t, t - np.timedelta64(500, "ms"), side="left")
    hi = np.searchsorted(ir_t, t + np.timedelta64(500, "ms"), side="right")
    win = ir_v[lo:hi]
    valid = win[~np.isnan(win)]
    n_any.append(len(win))
    ir_max_col.append(valid.mean() if len(valid) else np.nan)
    ir_n_col.append(len(valid))
tc["ir_max"] = ir_max_col
tc["ir_n"] = ir_n_col
tc["_n_any"] = n_any

# report the two match counts separately (review finding: do not conflate)
m_any = int((tc["_n_any"] > 0).sum())
m_val = int((tc["ir_n"] > 0).sum())
print(f"Match semantics, TC rows {len(tc)}:")
print(f"  with ANY IR row in +-0.5s window (incl. freeze NaN): {m_any}")
print(f"  with >=1 VALID ir_max in window:                      {m_val}")
print(f"  unmatched (no IR row in window):                      {len(tc) - m_any}")
vn = tc.loc[tc["ir_n"] > 0, "ir_n"]
print(f"  ir_n among matched rows: min={vn.min()} median={vn.median():.0f} max={vn.max()}")

# --- lag estimate on derivatives (integer 1s grid, report only) ---
t1 = tc.set_index("time")["T1"]
b = tc.set_index("time")["B均值"]
irr = ir.set_index("time")["ir_max"].resample("1s").mean()
lo_w = max(t1.index.min(), irr.index.min())
hi_w = min(t1.index.max(), irr.index.max())
t1w = t1.loc[lo_w:hi_w].interpolate()
bw = b.loc[lo_w:hi_w].interpolate()
irw = irr.loc[lo_w:hi_w].interpolate()


def lag_profile(a, b, max_lag=15):
    """Normalized cross-correlation of a with b shifted by lag (integer steps).
    Positive best lag => b lags a (b's pattern appears later)."""
    a = (a - a.mean()) / (a.std() + 1e-12)
    b = (b - b.mean()) / (b.std() + 1e-12)
    scores = {}
    for lag in range(-max_lag, max_lag + 1):
        bb = b.shift(-lag)
        m = a.notna() & bb.notna()
        scores[lag] = float((a[m] * bb[m]).mean())
    return scores


print(f"Lag estimate (derivatives, 1s grid, overlap {lo_w} -> {hi_w}; "
      f"REPORT ONLY, not applied):")
prof_t1 = lag_profile(t1w.diff(), irw.diff())
prof_b = lag_profile(bw.diff(), irw.diff())
for name, scores in (("T1", prof_t1), ("B均值", prof_b)):
    best = max(scores, key=scores.get)
    prof = "  ".join(f"{l:+d}s:{scores[l]:.3f}" for l in range(-2, 3))
    print(f"  d{name}/dt vs d(ir_max)/dt: best {best:+d}s "
          f"corr={scores[best]:.3f}  | profile -2..+2s: {prof}")

lag_df = pd.DataFrame({
    "lag_s": sorted(prof_t1),
    "corr_T1": [prof_t1[l] for l in sorted(prof_t1)],
    "corr_B": [prof_b[l] for l in sorted(prof_b)],
})
lag_df.to_csv(OUT_LAG, index=False, encoding="utf-8-sig", float_format="%.4f")
print(f"wrote {OUT_LAG}: {len(lag_df)} rows")

# --- write aligned table ---
tc = tc.drop(columns=["_n_any"])
tc["time"] = tc["time"].dt.strftime("%Y-%m-%d %H:%M:%S")
out = tc[["time", "T1", "T2", "T3", "T4", "T5", "B均值", "ir_max", "ir_n"]]
out.to_csv(OUT, index=False, encoding="utf-8-sig")
print(f"wrote {OUT}: {len(out)} rows x {len(out.columns)} cols")
