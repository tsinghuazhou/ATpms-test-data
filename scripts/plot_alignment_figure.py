"""Alignment validation figure: Gyroid 30W 2026-10-14 thermocouple vs IR.

Main panel: T1 / B均值 / IR max on one temperature axis, wall-clock aligned
(no lag correction applied; see notes/2026-10-14.md). Freeze-frame gaps and
the 42-52 degC melt window are marked. Inset: d/dt cross-correlation
profiles vs lag (report-only diagnostic from the alignment script).
"""
import sys
from pathlib import Path

import pandas as pd
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

STYLE = Path(r"C:\Users\tsing\AppData\Roaming\com.ai4s.workbench\runtime"
             r"\xdg-config\opencode\skills\publication-figures\openscience.mplstyle")
plt.style.use(str(STYLE))

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "output" / "paper" / "figures"

# Palette slots: T1=blue, B mean=aqua, IR max=yellow (fixed slot order).
C_T1, C_B, C_IR = "#2a78d6", "#1baf7a", "#eda100"

ALIGNED = sys.argv[1] if len(sys.argv) > 1 else "aligned_gyroid30w_20261014.csv"
tag = Path(ALIGNED).stem.replace("aligned_", "")  # <structure>_<date>
df = pd.read_csv(ROOT / ALIGNED, encoding="utf-8-sig")
lag = pd.read_csv(ROOT / f"lag_profile_{tag}.csv", encoding="utf-8-sig")
bcol = next(c for c in df.columns if c.startswith("B"))

t0 = pd.Timestamp(df["time"].iloc[0])
tmin = (pd.to_datetime(df["time"]) - t0).dt.total_seconds().to_numpy() / 60.0

fig, ax = plt.subplots(figsize=(6.5, 4.2))

# melt window band
ax.axhspan(42, 52, color="#e7e3da", alpha=0.55, zorder=0)
ax.text(6.75, 47, "melt window\n42\u201352 \u00b0C", fontsize=6.5,
        color="#8c877d", ha="right", va="center", linespacing=1.2)

# freeze-frame gaps / IR-recording end: consecutive ir_n==0 runs
n = df["ir_n"].to_numpy()
runs, start = [], None
for i, bad in enumerate(n == 0):
    if bad and start is None:
        start = i
    elif not bad and start is not None:
        runs.append((start, i - 1))
        start = None
if start is not None:
    runs.append((start, len(n) - 1))
for a, b in runs:
    ax.axvspan(tmin[a] - 0.5 / 60.0, tmin[b] + 0.5 / 60.0,
               color="#cbc6bb", alpha=0.55, zorder=0)

ax.plot(tmin, df["T1"], color=C_T1, lw=1.6, label="T1 (bottom, heater)", zorder=3)
ax.plot(tmin, df[bcol], color=C_B, lw=1.6, label="B mean (mid, T2/T3/T5)", zorder=3)
ax.plot(tmin, df["ir_max"], color=C_IR, lw=1.6, label="IR max (top surface)", zorder=3)

ax.set_xlabel("Time (min)")
ax.set_ylabel("Temperature (\u00b0C)")
ax.set_xlim(tmin[0], tmin[-1] + 0.15)
ax.set_ylim(20, 100)

handles, labels = ax.get_legend_handles_labels()
handles.append(Patch(facecolor="#cbc6bb", alpha=0.55,
                     label="no valid IR (freeze/stop)"))
ax.legend(handles=handles, loc="lower right", fontsize=7, framealpha=0.95,
          borderpad=0.5, handlelength=1.6, bbox_to_anchor=(1.0, 0.02))

# inset: lag profiles (report-only); kept above the T1 curve
axin = ax.inset_axes([0.07, 0.62, 0.38, 0.32])
axin.axhline(0, color="#cbc6bb", lw=0.6)
best_b = int(lag.loc[lag["corr_B"].idxmax(), "lag_s"])
axin.axvline(best_b, color=C_B, lw=0.9, ls="--", alpha=0.8)
axin.plot(lag["lag_s"], lag["corr_T1"], color=C_T1, lw=1.1, alpha=0.85)
axin.plot(lag["lag_s"], lag["corr_B"], color=C_B, lw=1.3)
axin.set_xlim(-15, 15)
axin.set_ylim(-0.35, 1.0)
axin.set_xlabel("Lag (s)", fontsize=7.5)
axin.tick_params(labelsize=7)
axin.set_title(f"deriv. cross-corr vs IR; best(B)={best_b:+d}s",
               fontsize=7, pad=2)
for s in ("top", "right"):
    axin.spines[s].set_visible(False)

fig.savefig(FIG_DIR / f"ir_alignment_{tag}.png", dpi=300,
            bbox_inches="tight")
fig.savefig(FIG_DIR / f"ir_alignment_{tag}.pdf", bbox_inches="tight")
print(f"saved {FIG_DIR / f'ir_alignment_{tag}.png'}")
print(f"saved {FIG_DIR / f'ir_alignment_{tag}.pdf'}")
