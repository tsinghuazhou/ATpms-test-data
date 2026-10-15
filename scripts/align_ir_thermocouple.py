"""Time-align an IR camera record (25 Hz) with a thermocouple record (1 Hz).

Usage:
  python scripts/align_ir_thermocouple.py TC_CSV IR_CSV
    TC_CSV: thermocouple log, e.g. tpms_gyroid30w_20261014_183455.csv (T1-T5, 1 Hz)
    IR_CSV: IR export, e.g. tpms_gyroid30w_20261014_183450_ir.csv
        (UTF-8-BOM, 2 header rows; columns: wall clock, elapsed,
         image max (= top-layer temp), image min)

Outputs (named after the TC file's structure+date):
  aligned_<structure>_<date>.csv  - one row per TC timestamp: T1-T5,
      B_mean (T2/T3/T5 per project convention), ir_max, ir_n
  lag_profile_<structure>_<date>.csv - first-difference cross-correlation
      vs lag (-15..+15 s), columns lag_s, corr_T1, corr_B

Method:
  - freeze-frame rows (camera paused, sentinel 0.0) -> NaN
  - duplicate IR timestamps -> keep first
  - clock offset estimated by cross-correlation of 1 Hz first differences
    over +/-15 s; seconds with no valid IR (freeze/gap) are MASKED, not
    interpolated. Score profile around the optimum is printed so the
    resolution (limited by the 1 Hz TC grid) is visible.
  - Per decision: lag is REPORTED but NOT applied; rows are matched on
    wall clock (nearest within +/-0.5 s).
  - Level (non-differenced) correlations are printed only as a caution:
    both series are monotone ramps, so their lag-0 peak is not evidence
    of clock sync.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

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


def lag_report(tc, ir, tag):
    """First-difference cross-correlation on the common 1 s grid.

    IR seconds without valid samples (freeze/gap) stay NaN and are masked;
    no interpolation is performed across invalid windows.
    """
    ir1 = ir.set_index("time")["ir_max"].resample("1s").mean()
    lo = max(tc["time"].min(), ir1.index.min())
    hi = min(tc["time"].max(), ir1.index.max())
    tcw = tc.set_index("time")[["T1", "B_mean"]].loc[lo:hi]
    irw = ir1.loc[lo:hi]  # NaN where freeze/gap - masked below, never filled

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
    profile = {"lag_s": list(range(-MAX_LAG, MAX_LAG + 1))}
    for name in ("T1", "B_mean"):
        sc = scores(tcw[name], irw)
        best = max(sc, key=sc.get)
        results[name] = (best, sc[best])
        profile[f"corr_{name.split('_')[0]}"] = [sc[l] for l in profile["lag_s"]]
        neighbors = ", ".join(
            f"{lag:+d}s:{sc[lag]:.3f}" for lag in range(best - 2, best + 3)
        )
        print(f"diff-lag ir vs {name}: best {best:+d}s (corr {sc[best]:.3f})  "
              f"profile {neighbors}")
    pd.DataFrame(profile).to_csv(f"lag_profile_{tag}.csv", index=False)
    # level correlations: printed as caution only (monotone ramps -> lag-0 peak
    # regardless of true offset; NOT clock-sync evidence)
    lvl = {}
    for name in ("T1", "B_mean"):
        a, c = tcw[name], irw
        m = a.notna() & c.notna()
        lvl[name] = float(np.corrcoef(a[m], c[m])[0, 1])
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


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("tc_csv")
    ap.add_argument("ir_csv")
    args = ap.parse_args(argv)

    parts = Path(args.tc_csv).stem.split("_")  # tpms_<structure>_<date>_<time>
    tag = f"{parts[1]}_{parts[2]}"
    out_path = f"aligned_{tag}.csv"

    ir, diag = load_ir(args.ir_csv)
    tc = load_tc(args.tc_csv)
    print(f"IR rows={len(ir)}  {ir['time'].iloc[0]} -> {ir['time'].iloc[-1]}")
    print(f"IR diagnostics: freeze_rows={diag['freeze_rows']} "
          f"dup_ts_removed={diag['dup_ts']}")
    if len(diag["gaps_gt_0.1s"]):
        print(f"  gaps >0.1s: {len(diag['gaps_gt_0.1s'])} "
              f"(max {diag['gaps_gt_0.1s'].max():.3f}s)")
    print(f"TC rows={len(tc)}  {tc['time'].iloc[0]} -> {tc['time'].iloc[-1]}")
    print(f"IR starts {(tc['time'].iloc[0] - ir['time'].iloc[0]).total_seconds():+.3f}s "
          f"vs TC start; ends "
          f"{(ir['time'].iloc[-1] - tc['time'].iloc[-1]).total_seconds():+.3f}s "
          f"vs TC end")

    results = lag_report(tc, ir, tag)
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
    merged[cols].to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"wrote {out_path}  ({len(merged)} rows)")
    return merged, ir, results


if __name__ == "__main__":
    main(sys.argv[1:])
