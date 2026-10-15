"""Comparison figures for the 2026-10-15 runs.

Fig 1 (TC reproducibility): middle-layer temperature, new 10-15 runs vs old.
  (a) Gyroid 10W: B(T2/T3/T5) new vs 08-04/08-08.
  (b) IWP 30W: new B(T2/T3/T5) vs old B23(T2/T3; T5 is a bad channel in 08-10).
Fig 2 (30W cross-structure, same IR methodology):
  (a) B_mean, (b) IR max - Gyroid (10-14) vs IWP (10-15).
"""
import sys
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

STYLE = Path(r"C:\Users\tsing\AppData\Roaming\com.ai4s.workbench\runtime"
             r"\xdg-config\opencode\skills\publication-figures\openscience.mplstyle")
plt.style.use(str(STYLE))

ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "output" / "paper" / "figures"
C_BLUE, C_AQUA, C_YEL, C_RED, C_GREY = ("#2a78d6", "#1baf7a", "#eda100",
                                        "#d1495b", "#8c877d")


def load_aligned(name):
    df = pd.read_csv(ROOT / name, encoding="utf-8-sig")
    t = (pd.to_datetime(df["time"]) - pd.to_datetime(df["time"].iloc[0])
         ).dt.total_seconds() / 60.0
    return t.to_numpy(), df


def load_old(path, b_cols):
    df = pd.read_csv(ROOT / path, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]
    t = (pd.to_datetime(df[df.columns[0]]) - pd.to_datetime(df[df.columns[0]].iloc[0])
         ).dt.total_seconds() / 60.0
    return t.to_numpy(), df[b_cols].mean(axis=1).to_numpy()


def style_ax(ax):
    ax.axhspan(42, 52, color="#e7e3da", alpha=0.55, zorder=0)
    ax.set_xlabel("Time (min)")
    ax.set_ylabel("Temperature (°C)")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def fig1():
    fig, axes = plt.subplots(1, 2, figsize=(7.09, 2.9))
    # (a) Gyroid 10W
    ax = axes[0]
    t, b = load_aligned("aligned_gyroid10w_20261015.csv")
    ax.plot(t, b["B_mean"], color=C_BLUE, lw=1.4, label="new 10-15 (IR day)")
    for label, f, c in (("08-04", "tpms_gyroid10w_20260804_163501.csv", C_AQUA),
                        ("08-08", "tpms_gyroid10w_20260808_165138.csv", C_YEL)):
        to, bo = load_old(f, ["T2", "T3", "T5"])
        ax.plot(to, bo, color=c, lw=1.2, alpha=0.9, label=f"old {label}")
    style_ax(ax)
    ax.set_title("(a) Gyroid 10 W - middle layer", fontsize=8)
    ax.legend(fontsize=6.5, loc="upper left", framealpha=0.9)
    # (b) IWP 30W
    ax = axes[1]
    t, b = load_aligned("aligned_iwp30w_20261015.csv")
    ax.plot(t, b["B_mean"], color=C_BLUE, lw=1.4, label="new 10-15 (T2/T3/T5)")
    to, bo = load_old("tpms_iwp30w_20260810_152336.csv", ["T2", "T3"])
    ax.plot(to, bo, color=C_RED, lw=1.2, alpha=0.9,
            label="old 08-10 (T2/T3; T5 bad)")
    style_ax(ax)
    ax.set_title("(b) IWP 30 W - middle layer", fontsize=8)
    ax.legend(fontsize=6.5, loc="upper left", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "runs_20261015_tc_reproducibility.png", dpi=300)
    fig.savefig(FIG_DIR / "runs_20261015_tc_reproducibility.pdf")
    print("saved runs_20261015_tc_reproducibility.{png,pdf}")


def fig2():
    fig, axes = plt.subplots(1, 2, figsize=(7.09, 2.9))
    t_g, g = load_aligned("aligned_gyroid30w_20261014.csv")
    t_i, i = load_aligned("aligned_iwp30w_20261015.csv")
    ax = axes[0]
    ax.plot(t_g, g["B_mean"], color=C_BLUE, lw=1.4, label="Gyroid 10-14")
    ax.plot(t_i, i["B_mean"], color=C_RED, lw=1.4, label="IWP 10-15")
    style_ax(ax)
    ax.set_title("(a) 30 W middle layer (TC)", fontsize=8)
    ax.legend(fontsize=6.5, loc="upper left", framealpha=0.9)
    ax = axes[1]
    ax.plot(t_g, g["ir_max"], color=C_BLUE, lw=1.4, label="Gyroid 10-14")
    ax.plot(t_i, i["ir_max"], color=C_RED, lw=1.4, label="IWP 10-15")
    style_ax(ax)
    ax.set_title("(b) 30 W top surface (IR max)", fontsize=8)
    ax.legend(fontsize=6.5, loc="lower right", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "ir_top_30w_gyroid_vs_iwp.png", dpi=300)
    fig.savefig(FIG_DIR / "ir_top_30w_gyroid_vs_iwp.pdf")
    print("saved ir_top_30w_gyroid_vs_iwp.{png,pdf}")


if __name__ == "__main__":
    fig1()
    fig2()
