"""独立复算 TPMS-PCM 9 组加热实验指标 (纯标准库, 无 pandas)。

复现 compare_all_structures.py 的统计口径:
- B组: Gyroid/Primitive = mean(T2,T3,T5); IWP = mean(T2,T3)
- C组: Gyroid/Primitive = T9; IWP 10W/20W = mean(T8,T9); IWP 30W = T9
- t9_42 一律用 T9 单点; 熔融窗口 T1 in [42,52]
- 梯度取 |T1-目标| 最小的采样点 (idxmin 口径, 与旧脚本一致)
时间轴: 秒精度文件用真实时间差; IWP20W 仅分钟精度, 退化为行号(=1Hz)。
"""
import io
import os
import re
import sys
import csv
import math
import zipfile
import datetime
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.abspath(__file__))
XLSX_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

FILES = {
    "Gyroid_10W":  "tpms_gyroid10w_20260808_165138.csv",
    "Gyroid_20W":  "tpms_gyroid20w_20260808_190451.csv",
    "Gyroid_30W":  "tpms_gyroid30w_20260808_203206.csv",
    "IWP_10W":     "tpms_iwp10w_20260809_170915.xlsx",
    "IWP_20W":     "tpms_iwp20w_20260809_201218.csv",
    "IWP_30W":     "tpms_iwp30w_20260810_152336.csv",
    "Primitive_10W": "tpms_primitive10w_20260805_200423.csv",
    "Primitive_20W": "tpms_primitive20w_20260806_214551.csv",
    "Primitive_30W": "tpms_primitive30w_20260807_193935.csv",
}

SUPERSEDED = {
    "G10_run1_xlsx": "tpms_gyroid10w_20260730_193152.xlsx",
    "G10_old":       "tpms_gyroid10w_20260804_163501.csv",
    "G20_old":       "tpms_gyroid20w_20260731_195755.csv",
    "G20_heat_0802": "tpms_gyroid20w_20260802_203604.csv",
    "G20_cool_0802": "tpms_gyroid20w_20260802_204933.csv",
    "G30_old":       "tpms_gyroid30w_20260803_171111.csv",
    "P20_deprecated": "deprecated/tpms_primitive20w_20260806_162603.csv",
}

TS_FMT_S = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
TS_FMT_M = re.compile(r"^\d{4}/\d{1,2}/\d{1,2} \d{1,2}:\d{2}$")


def parse_dt(text):
    t = text.strip()
    if TS_FMT_S.match(t):
        return datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
    if TS_FMT_M.match(t):
        return datetime.datetime.strptime(t, "%Y/%m/%d %H:%M")
    return None


def xlsx_rows(path):
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        ss = ET.fromstring(z.read("xl/sharedStrings.xml"))
        shared = ["".join(x.text or "" for x in si.iter(XLSX_NS + "t"))
                  for si in ss.iter(XLSX_NS + "si")]
    sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    out = []
    for row in sheet.iter(XLSX_NS + "row"):
        vals = []
        for c in row.iter(XLSX_NS + "c"):
            v = c.find(XLSX_NS + "v")
            if v is None:
                vals.append("")
                continue
            if c.get("t") == "s":
                vals.append(shared[int(v.text)])
            else:
                vals.append(v.text)
        out.append(vals)
    return out


def excel_serial_to_dt(serial):
    base = datetime.datetime(1899, 12, 30)
    return base + datetime.timedelta(days=float(serial))


def load_file(path):
    """返回 dict(ts=None|list, T=9列list, elapsed_min list, rows)"""
    full = os.path.join(ROOT, path)
    if path.endswith(".xlsx"):
        rows = xlsx_rows(full)
    else:
        raw = io.open(full, "rb").read().decode("utf-8-sig", errors="replace")
        rows = [r for r in csv.reader(io.StringIO(raw))]
    header = rows[0]
    data = []
    for r in rows[1:]:
        if len(r) < 10 or not r[0].strip():
            continue
        try:
            tvals = [float(x) for x in r[1:10]]
        except ValueError:
            continue
        if all(math.isfinite(x) for x in tvals):
            data.append((r[0].strip(), tvals))
    if not data:
        raise ValueError("empty: " + path)
    n = len(data)
    ts_text = [d[0] for d in data]
    tvals_all = [d[1] for d in data]
    elapsed_idx = list(range(n))  # 旧脚本口径: 行号 = 1s
    dts = [parse_dt(t) for t in ts_text]
    if path.endswith(".xlsx"):
        try:
            dts = [excel_serial_to_dt(t) for t in ts_text]
        except ValueError:
            dts = [None] * n
    n_dt = sum(1 for x in dts if x is not None)
    elapsed_real = None
    has_real_sec = False
    if n_dt > n * 0.9:
        t0 = next(x for x in dts if x is not None)
        gaps = [(dts[i] - dts[i - 1]).total_seconds() for i in range(1, n)
                if dts[i] is not None and dts[i - 1] is not None]
        med_gap = sorted(gaps)[len(gaps) // 2] if gaps else 0.0
        has_real_sec = 0.8 <= med_gap <= 1.2
        if has_real_sec:
            elapsed_real = [(x - t0).total_seconds() if x is not None
                            else math.nan for x in dts]
            for i in range(1, n):
                if math.isnan(elapsed_real[i]):
                    elapsed_real[i] = elapsed_real[i - 1] + 1.0
    T = {f"T{i+1}": [r[i] for r in tvals_all] for i in range(9)}
    return {"n": n, "T": T, "elapsed": elapsed_idx,
            "elapsed_real": elapsed_real, "has_real_sec": has_real_sec}


def interp_time(el, vals, target):
    """返回 vals 首次达到 target 的时间(min) (线性插值跨点)"""
    for i in range(1, len(vals)):
        a, b = vals[i - 1], vals[i]
        if a < target <= b:
            f = (target - a) / (b - a) if b > a else 0.0
            return (el[i - 1] + f * (el[i] - el[i - 1])) / 60.0
        if a >= target:
            return el[i - 1] / 60.0
    return math.nan


def calc_metrics(d, structure, power_w, use_real=False):
    n = d["n"]
    el = (d["elapsed_real"] if (use_real and d["has_real_sec"])
          else d["elapsed"])
    T = d["T"]
    Bm = ["T2", "T3"] if structure == "IWP" else ["T2", "T3", "T5"]
    Cm = ["T8", "T9"] if (structure == "IWP" and power_w in (10, 20)) else ["T9"]
    B = [sum(T[m][i] for m in Bm) / len(Bm) for i in range(n)]
    C = [sum(T[m][i] for m in Cm) / len(Cm) for i in range(n)]
    ab = [T["T1"][i] - B[i] for i in range(n)]
    ac = [T["T1"][i] - C[i] for i in range(n)]
    el_min = [e / 60.0 for e in el]

    def first_ge(vals, thr):
        for i, v in enumerate(vals):
            if v >= thr:
                return el_min[i]
        return math.nan

    mask = [i for i in range(n) if 42.0 <= T["T1"][i] <= 52.0]
    melt = (el_min[mask[-1]] - el_min[mask[0]]) if len(mask) > 1 else 0.0

    def grad_at(vals, target):
        j = min(range(n), key=lambda i: abs(T["T1"][i] - target))
        return vals[j]

    # C 组 T9 单独 (与旧脚本 t9_42 一致)
    t9_raw = T["T9"]
    g = {
        "n": n,
        "melt_min": melt,
        "t1_42": first_ge(T["T1"], 42),
        "t9_42": first_ge(t9_raw, 42),
        "ab_42": grad_at(ab, 42), "ab_50": grad_at(ab, 50),
        "ab_55": grad_at(ab, 55),
        "ac_42": grad_at(ac, 42), "ac_50": grad_at(ac, 50),
        "ac_55": grad_at(ac, 55),
        "duration_min": el_min[-1] - el_min[0],
        "t1_end": T["T1"][-1],
        "t1_peak": max(T["T1"]),
        "b_spread_win": max(max(T[m][i] for m in Bm) - min(T[m][i] for m in Bm)
                            for i in mask) if mask else math.nan,
        "c_dev_win": {m: sum(T[m][i] - T["T9"][i] for i in mask) / len(mask)
                      if mask else math.nan for m in ["T6", "T7", "T8"]},
    }
    g["ab_expansion"] = (g["ab_55"] - g["ab_42"]) / g["ab_42"] * 100.0
    return g


def main():
    out = []
    print("=" * 96)
    print("TPMS-PCM 加热实验 9 组矩阵独立复算 (纯标准库)")
    print("=" * 96)
    rows = []
    for key, fname in FILES.items():
        struct, pw = key.rsplit("_", 1)
        pw = int(pw[:-1])
        d = load_file(fname)
        m = calc_metrics(d, struct, pw)
        med_dt = _median([d["elapsed"][i] - d["elapsed"][i - 1]
                          for i in range(1, d["n"])])
        dur_real = (d["elapsed_real"][-1] - d["elapsed_real"][0]) / 60.0 \
            if d["elapsed_real"] is not None else math.nan
        row = [key, m["n"], m["duration_min"], dur_real, med_dt,
               m["melt_min"], m["t1_42"], m["t9_42"],
               m["ab_42"], m["ab_50"], m["ab_55"],
               m["ac_42"], m["ac_50"], m["ac_55"],
               m["ab_expansion"], m["t1_end"], m["t1_peak"]]
        rows.append((key, row))
        print(f"{key:<15} rows={row[1]:>5} dur_idx={row[2]:>6.2f} "
              f"dur_real={row[3]:>6.2f} dt_med={row[4]:.2f}s | "
              f"melt={row[5]:>6.2f} t1_42={row[6]:>6.2f} "
              f"t9_42={row[7]:>6.2f} | AB@42/55={row[8]:>5.2f}/{row[10]:>5.2f} "
              f"AC@42/55={row[11]:>5.2f}/{row[13]:>5.2f} "
              f"exp%={row[14]:>6.2f} | T1_end={row[15]:>6.1f} "
              f"T1_peak={row[16]:>6.1f}")

    # 与定稿综合表比对 (规范化口径 = 真实时间戳, 见 compute_canonical_matrix_20260909.py)
    csvp = os.path.join(ROOT, "output", "paper", "data",
                        "tpms_comprehensive_comparison.csv")
    existing = {}
    with io.open(csvp, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            existing[f"{r['Structure']}_{r['Power']}"] = r
    print("\n-- 对规范化综合表复算 (真实时间戳口径, 期望Δ≈0) --")
    max_diff = {}
    for key, fname in FILES.items():
        struct, pw = key.rsplit("_", 1)
        pw = int(pw[:-1])
        d = load_file(fname)
        m = calc_metrics(d, struct, pw, use_real=True)
        old = existing[f"{struct}_{pw}W"]
        diff = {
            "melt": abs(m["melt_min"] - float(old["melting_duration"])),
            "ab42": abs(m["ab_42"] - float(old["ab_42"])),
            "exp": abs(m["ab_expansion"] - float(old["ab_expansion"])),
            "dur": abs(m["duration_min"] - float(old["duration"])),
        }
        for k, v in diff.items():
            max_diff[k] = max(max_diff.get(k, 0), v)
        print(f"{key:<15} |Dmelt|={diff['melt']:.3f} |Dab42|={diff['ab42']:.3f} "
              f"|Dexp|={diff['exp']:.2f} |Ddur|={diff['dur']:.3f}")
    print("max diff per metric:", {k: round(v, 3) for k, v in max_diff.items()})

    # 失效/旧 runs 诊断
    print("\n-- 已废弃/旧 runs 诊断 (同口径指标 + 接触诊断) --")
    for key, fname in SUPERSEDED.items():
        try:
            d = load_file(fname)
        except FileNotFoundError:
            print(f"{key:<16} MISSING")
            continue
        struct, pw = {"G10": ("Gyroid", 10), "G20": ("Gyroid", 20),
                      "G30": ("Gyroid", 30), "P20": ("Primitive", 20)}[
            key[:3]]
        m = calc_metrics(d, struct, pw)
        Bm = ["T2", "T3"] if struct == "IWP" else ["T2", "T3", "T5"]
        B = [sum(d["T"][x][i] for x in Bm) / len(Bm)
             for i in range(d["n"])]
        j120 = min(range(d["n"]), key=lambda i: abs(d["elapsed"][i] - 120))
        t1b2 = d["T"]["T1"][j120] - B[j120]
        rate30 = (d["T"]["T1"][30] - d["T"]["T1"][0]) / 0.5 if d["n"] > 30 \
            else math.nan
        print(f"{key:<16} n={d['n']:>5} dur={m['duration_min']:>6.2f}min "
              f"T1_end={m['t1_end']:>6.1f} peak={m['t1_peak']:>6.1f} "
              f"melt={m['melt_min']:>5.2f} | T1-B@2min={t1b2:>6.1f}C "
              f"T1首30s速率~{rate30:>6.1f}C/min")

    # 保存复算表
    os.makedirs(os.path.join(ROOT, "output", "data"), exist_ok=True)
    outp = os.path.join(ROOT, "output", "data",
                        "verified_matrix_20260909.csv")
    with io.open(outp, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["run", "rows", "duration_min_idx", "duration_min_real",
                    "dt_med_s", "melt_min", "t1_42", "t9_42", "ab_42",
                    "ab_50", "ab_55", "ac_42", "ac_50", "ac_55",
                    "ab_exp_pct", "t1_end", "t1_peak"])
        for key, row in rows:
            w.writerow([key] + row[1:])
    print("\n[已保存] output/data/verified_matrix_20260909.csv")


def _median(xs):
    s = sorted(xs)
    k = len(s)
    if k == 0:
        return math.nan
    return s[k // 2] if k % 2 else (s[k // 2 - 1] + s[k // 2]) / 2.0


if __name__ == "__main__":
    main()
