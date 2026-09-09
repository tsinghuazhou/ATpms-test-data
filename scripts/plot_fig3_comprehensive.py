"""Fig. 3 (9-panel comprehensive comparison) generator — canonical CSV driven.

替换 compare_all_structures.py 的绘图职责(其内部仍按行号口径重算指标并覆盖
规范 CSV, 已退役)。本脚本只读:
- output/paper/data/tpms_comprehensive_comparison.csv (规范口径指标)
- 根目录原始数据文件 (仅用于底部 3 个 T1 时间曲线面板)
输出与旧图同布局的 9 面板图。用法:
    python scripts/plot_fig3_comprehensive.py [--out DIR]
"""
import argparse
import io
import os
import csv
import math
import zipfile
import datetime
import xml.etree.ElementTree as ET

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLSX_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

RAW = {
    "10W": {"Gyroid": "tpms_gyroid10w_20260808_165138.csv",
            "IWP": "tpms_iwp10w_20260809_170915.xlsx",
            "Primitive": "tpms_primitive10w_20260805_200423.csv"},
    "20W": {"Gyroid": "tpms_gyroid20w_20260808_190451.csv",
            "IWP": "tpms_iwp20w_20260809_201218.csv",
            "Primitive": "tpms_primitive20w_20260806_214551.csv"},
    "30W": {"Gyroid": "tpms_gyroid30w_20260808_203206.csv",
            "IWP": "tpms_iwp30w_20260810_152336.csv",
            "Primitive": "tpms_primitive30w_20260807_193935.csv"},
}


def xlsx_first_two(path):
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        ss = ET.fromstring(z.read("xl/sharedStrings.xml"))
        shared = ["".join(x.text or "" for x in si.iter(XLSX_NS + "t"))
                  for si in ss.iter(XLSX_NS + "si")]
    sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    ts, t1 = [], []
    for row in sheet.iter(XLSX_NS + "row"):
        vals = []
        for c in row.iter(XLSX_NS + "c"):
            v = c.find(XLSX_NS + "v")
            if v is None:
                vals.append("")
            else:
                vals.append(shared[int(v.text)] if c.get("t") == "s" else v.text)
        if len(vals) >= 2:
            try:
                if vals[0]:
                    base = datetime.datetime(1899, 12, 30)
                    t = base + datetime.timedelta(days=float(vals[0]))
                    ts.append(t)
                    t1.append(float(vals[1]))
            except (ValueError, TypeError):
                continue
    return ts, t1


def load_t1(power, structure):
    fname = RAW[power][structure]
    full = os.path.join(ROOT, fname)
    if fname.endswith(".xlsx"):
        ts, t1 = xlsx_first_two(full)
        t0 = ts[0]
        tmin = [(t - t0).total_seconds() / 60.0 for t in ts]
        return tmin, t1
    rows = [r for r in csv.reader(io.StringIO(
        io.open(full, "rb").read().decode("utf-8-sig", errors="replace")))]
    out_t, out_v = [], []
    for r in rows[1:]:
        if len(r) < 2 or not r[0].strip():
            continue
        try:
            dt = datetime.datetime.strptime(r[0].strip(), "%Y-%m-%d %H:%M:%S")
            v = float(r[1])
        except (ValueError, TypeError):
            continue
        out_t.append(dt)
        out_v.append(v)
    t0 = out_t[0]
    tmin = [(t - t0).total_seconds() / 60.0 for t in out_t]
    return tmin, out_v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "output", "paper",
                                                  "figures"))
    args = ap.parse_args()

    # 规范指标
    meta = {}
    with io.open(os.path.join(ROOT, "output", "paper", "data",
                              "tpms_comprehensive_comparison.csv"),
                 encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            meta[(r["Power"], r["Structure"])] = r

    powers = ["10W", "20W", "30W"]
    structures = ["Gyroid", "IWP", "Primitive"]
    colors = {"Gyroid": "blue", "IWP": "purple", "Primitive": "red"}

    fig = plt.figure(figsize=(20, 12))
    x = np.arange(3)
    width = 0.25

    def bars(ax, metric, ylabel, title, fmt="{:.2f}"):
        vals = {s: [float(meta[(p, s)][metric]) for p in powers]
                for s in structures}
        for i, s in enumerate(structures):
            ax.bar(x + i * width, vals[s], width, label=s, color=colors[s],
                   alpha=0.7)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.set_xticks(x + width)
        ax.set_xticklabels(powers)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    bars(plt.subplot(3, 3, 1), "melting_duration", "Melting Duration (min)",
         "Melting Duration (canonical)")
    bars(plt.subplot(3, 3, 2), "ab_42", "A-B Gradient @ 42C (C)",
         "A-B Gradient @ 42C")
    bars(plt.subplot(3, 3, 3), "ab_expansion", "A-B Expansion (%)",
         "A-B Gradient Expansion (42-55C)")
    bars(plt.subplot(3, 3, 4), "t1_42", "Time to 42C (min)", "T1 Reaches 42C")
    bars(plt.subplot(3, 3, 5), "t9_42", "Time to 42C (min)", "T9 Reaches 42C")
    bars(plt.subplot(3, 3, 6), "ab_55", "A-B Gradient @ 55C (C)",
         "A-B Gradient @ 55C")

    for idx, power in enumerate(powers):
        ax = plt.subplot(3, 3, 7 + idx)
        for struct in structures:
            t, v = load_t1(power, struct)
            ax.plot(t, v, label=struct, color=colors[struct], linewidth=2)
        ax.axhline(y=42, color="green", linestyle="--", alpha=0.5,
                   label="Melting 42C")
        ax.set_xlabel("Time (min)")
        ax.set_ylabel("T1 (C)")
        ax.set_title("T1 Temperature - " + power)
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    os.makedirs(args.out, exist_ok=True)
    for ext in ("png", "pdf"):
        fp = os.path.join(args.out, "tpms_comprehensive_comparison." + ext)
        fig.savefig(fp, dpi=300 if ext == "png" else None,
                    bbox_inches="tight")
        print("saved:", fp)


if __name__ == "__main__":
    main()
