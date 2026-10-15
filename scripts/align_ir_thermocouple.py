"""Time-align the IR camera record (25 Hz) with the thermocouple record (1 Hz).

Input:
  tpms_gyroid30w_20261014_183450_ir.csv  - IR export (UTF-8-BOM, 2 header rows,
      columns: wall clock, elapsed, image max (= top-layer temp), image min)
  tpms_gyroid30w_20261014_183455.csv     - thermocouple log T1-T5, 1 Hz

Output:
  aligned_gyroid30w_20261014.csv - one row per thermocouple timestamp with
      T1-T5, B_mean (T2/T3/T5 per project convention), ir_max, ir_n.

Method:
  - freeze-frame rows (camera paused, sentinel 0.0) -> NaN
  - duplicate IR timestamps -> keep first
  - clock offset estimated by cross-correlation of 1 Hz first differences
    over +/-15 s; the score profile around the optimum is printed so the
    resolution (limited by the 1 Hz thermocouple grid) is visible.
  - Per decision: lag is REPORTED but NOT applied; rows are matched on
    wall clock (nearest within +/-0.5 s).
  - Level (non-differenced) correlations are printed only as a caution:
    both series are monotone ramps, so their lag-0 peak is not evidence
    of clock sync.
"""
from pathlib import Path

import numpy as np
import pandas as pd

IR_PATH = "tpms_gyroid30w_20261014_183450_ir.csv"
TC_PATH = "tpms_gyroid30w_20261014_183455.csv"
OUT_PATH = "aligned_gyroid30w_20261014.csv"
MAX_LAG = 15  # seconds


def load_ir(path):
    ir = pd.read_csv(
        path, skiprows=2, header=None, encoding="utf-8-sig",
        names=["time", "elapsed", "ir_max", "ir_min"],
    )
    freeze = ir["time"].str.strip().str.startswith("freeze frame")
    n_freeze = int(freeze.sum())
    ir["time"] = pd.to_datetime(
        ir["time"].str.replace("freeze frame ", "", regex=False).str.strip()
    )
    for c in ("ir_max", "ir_min"):
        ir[c] = pd.to_numeric(ir[c], errors="coerce")
    ir.loc[freeze, ["ir_max", "ir_min"]] = np.nan  # sentinel 0.0 invalid
    dt = ir["time"].diff().dt.total_seconds()
    n_dup = int((dt == 0).sum())
    ir = ir.drop_duplicates(subset="time", keep="first")
    gaps = dt[dt > 0.1]
    return ir, {"freeze_rows": n_freeze, "dup_ts": n_dup, "gaps_gt_0.1s": gaps}


def load_tc(path):
    tc = pd.read_csv(path, encoding="utf-8-sig")
    tc.columns = ["time"] + [f"T{i}" for i in range(1, len(tc.columns))]
    tc["time"] = pd.to_datetime(tc["time"])
    tc["B_mean"] = tc[["T2", "T3", "T5"]].mean(axis=1)
    return tc


def lag_report(tc, ir):
    """First-difference cross-correlation on the common 1 s grid."""
    ir1 = ir.set_index("time")["ir_max"].resample("1s").mean()
    lo = max(tc["time"].min(), ir1.index.min())
    hi = min(tc["time"].max(), ir1.index.max())
    t1 = tc.set_index("time")["T1"].loc[lo:hi].interpolate()
    b = tc.set_index("time")["B_mean"].loc[lo:hi].interpolate()
    irw = ir1.loc[lo:hi].interpolate()

    def scores(a, c):
        da, dc = a.diff(), c.diff()
        da = (da - da.mean()) / (da.std() + 1e-12)
        dc = (dc - dc.mean()) / (dc.std() + 1e-12)
        out = {}
        for lag in range(-MAX_LAG, MAX_LAG + 1):
            shifted = dc.shift(-lag)
            m = da.notna() & shifted.notna()
            out[lag] = float((da[m] * shifted[m]).mean())
        return out

    print(f"overlap window: {lo} -> {hi}")
    results = {}
    parts = Path(TC_PATH).stem.split("_")  # tpms_gyroid30w_20261014_183455
    profile = {"lag_s": list(range(-MAX_LAG, MAX_LAG + 1))}
    for name, sig in (("T1", t1), ("B_mean", b)):
        sc = scores(sig, irw)
        best = max(sc, key=sc.get)
        results[name] = (best, sc[best])
        profile[f"corr_{name.split('_')[0]}"] = [sc[l] for l in profile["lag_s"]]
        neighbors = ", ".join(
            f"{lag:+d}s:{sc[lag]:.3f}" for lag in range(best - 2, best + 3)
        )
        print(f"diff-lag ir vs {name}: best {best:+d}s (corr {sc[best]:.3f})  "
              f"profile {neighbors}")
    pd.DataFrame(profile).to_csv(
        f"lag_profile_{parts[1]}_{parts[2]}.csv", index=False)
    # level correlations: printed as caution only (monotone ramps -> lag-0 peak
    # regardless of true offset; NOT clock-sync evidence)
    lvl = {}
    for name, sig in (("T1", t1), ("B_mean", b)):
        a = (sig - sig.mean()) / sig.std()
        c = (irw - irw.mean()) / irw.std()
        lvl[name] = float((a * c).mean())
    print(f"level corr (CAUTION: monotone ramps, not clock evidence): "
          + "  ".join(f"{k}={v:.3f}" for k, v in lvl.items()))
    return results


def merge(tc, ir):
    """Match each thermocouple timestamp to IR samples within +/-0.5 s."""
    half = pd.Timedelta("0.5s")
    times = tc["time"].to_numpy()
    ir_t = ir["time"].to_numpy()
    idx = np.searchsorted(ir_t, times.astype("datetime64[ns]") - half)
    idx_end = np.searchsorted(ir_t, times.astype("datetime64[ns]") + half,
                              side="right")
    rows, n_arr, in_win = [], [], []
    for a, b in zip(idx, idx_end):
        in_win.append(b > a)
        if b > a:
            vals = ir["ir_max"].iloc[a:b]
            rows.append(vals.mean() if vals.notna().any() else np.nan)
            n_arr.append(int(vals.notna().sum()))
        else:
            rows.append(np.nan)
            n_arr.append(0)
    out = tc.copy()
    out["ir_max"] = rows
    out["ir_n"] = n_arr
    out["ir_in_window"] = in_win
    return out


def main():
    ir, diag = load_ir(IR_PATH)
    tc = load_tc(TC_PATH)
    print(f"IR rows={len(ir)}  {ir['time'].iloc[0]} -> {ir['time'].iloc[-1]}")
    print(f"IR diagnostics: freeze_rows={diag['freeze_rows']} "
          f"dup_ts_removed={diag['dup_ts']}")
    if len(diag["gaps_gt_0.1s"]):
        for ts, g in diag["gaps_gt_0.1s"].items():
            print(f"  gap {g:.3f}s at {ir['time'].loc[ts]}")
    print(f"TC rows={len(tc)}  {tc['time'].iloc[0]} -> {tc['time'].iloc[-1]}")
    print(f"IR starts {(tc['time'].iloc[0] - ir['time'].iloc[0]).total_seconds():+.3f}s "
          f"vs TC start; ends "
          f"{(ir['time'].iloc[-1] - tc['time'].iloc[-1]).total_seconds():+.3f}s "
          f"vs TC end")

    results = lag_report(tc, ir)
    print("(decision: lag reported only, NOT applied - wall-clock matching)")

    merged = merge(tc, ir)
    n_in = int(merged["ir_in_window"].sum())
    n_valid = int(merged["ir_max"].notna().sum())
    n_freeze = int((merged["ir_in_window"] & (merged["ir_n"] == 0)).sum())
    print(f"within +/-0.5s of IR samples: {n_in}/{len(tc)}; "
          f"IR-valid pairs: {n_valid}; "
          f"window inside freeze block (all-NaN): {n_freeze}; "
          f"outside IR coverage: {len(tc) - n_in}")

    cols = ["time"] + [f"T{i}" for i in range(1, 6)] + ["B_mean", "ir_max", "ir_n"]
    merged[cols].to_csv(OUT_PATH, index=False, encoding="utf-8-sig")
    print(f"wrote {OUT_PATH}  ({len(merged)} rows)")
    return merged, ir, results


if __name__ == "__main__":
    main()
