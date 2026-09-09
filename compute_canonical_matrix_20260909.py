"""生成规范化实验指标表 (真实时间戳口径, 2026-09-09 定稿)。

口径规则 (与 compare_all_structures.py 相同, 仅时间轴修正):
- B组: Gyroid/Primitive = mean(T2,T3,T5); IWP = mean(T2,T3)
- C组: Gyroid/Primitive = T9; IWP 10W/20W = mean(T8,T9); IWP 30W = T9
- t9_42 一律用 T9; 熔融窗口 = T1 ∈ [42,52]°C 首末样本
- 梯度取 |T1-目标| 最小采样点 (idxmin), 与旧脚本一致 → 梯度值不变
- 时间轴: 秒精度文件用真实时间戳 (修正旧版"行号=1s"在丢秒文件上低估
  时长的偏差, 如 Primitive 10W 真实 26.9 min vs 行号 22.3 min);
  IWP 20W 时间戳仅分钟精度, 无真实秒 → 用 1Hz 行号并注明 time_base=row
"""
import io
import os
import csv
import re
import math
import zipfile
import datetime
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.abspath(__file__))
XLSX_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

FILES = [
    ("10W", "Gyroid", "tpms_gyroid10w_20260808_165138.csv"),
    ("20W", "Gyroid", "tpms_gyroid20w_20260808_190451.csv"),
    ("30W", "Gyroid", "tpms_gyroid30w_20260808_203206.csv"),
    ("10W", "IWP", "tpms_iwp10w_20260809_170915.xlsx"),
    ("20W", "IWP", "tpms_iwp20w_20260809_201218.csv"),
    ("30W", "IWP", "tpms_iwp30w_20260810_152336.csv"),
    ("10W", "Primitive", "tpms_primitive10w_20260805_200423.csv"),
    ("20W", "Primitive", "tpms_primitive20w_20260806_214551.csv"),
    ("30W", "Primitive", "tpms_primitive30w_20260807_193935.csv"),
]
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
            vals.append(shared[int(v.text)] if c.get("t") == "s" else v.text)
        out.append(vals)
    return out


def excel_serial_to_dt(serial):
    return datetime.datetime(1899, 12, 30) + datetime.timedelta(days=float(serial))


def load_file(path):
    full = os.path.join(ROOT, path)
    if path.endswith(".xlsx"):
        rows = xlsx_rows(full)
    else:
        raw = io.open(full, "rb").read().decode("utf-8-sig", errors="replace")
        rows = [r for r in csv.reader(io.StringIO(raw))]
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
    n = len(data)
    ts_text = [d[0] for d in data]
    dts = [parse_dt(t) for t in ts_text]
    if path.endswith(".xlsx"):
        try:
            dts = [excel_serial_to_dt(t) for t in ts_text]
        except ValueError:
            dts = [None] * n
    ok = sum(1 for x in dts if x is not None)
    has_real_sec = False
    elapsed_real = None
    if ok > n * 0.9:
        t0 = next(x for x in dts if x is not None)
        gaps = [(dts[i] - dts[i - 1]).total_seconds() for i in range(1, n)
                if dts[i] is not None and dts[i - 1] is not None]
        med_gap = sorted(gaps)[len(gaps) // 2] if gaps else 0.0
        has_real_sec = 0.8 <= med_gap <= 1.2 and not path.endswith("_201218.csv")
        if has_real_sec:
            elapsed_real = [(x - t0).total_seconds() if x is not None else math.nan
                            for x in dts]
            for i in range(1, n):
                if math.isnan(elapsed_real[i]):
                    elapsed_real[i] = elapsed_real[i - 1] + 1.0
    T = {f"T{i+1}": [d[1][i] for d in data] for i in range(9)}
    return {"n": n, "T": T, "elapsed_real": elapsed_real,
            "has_real_sec": has_real_sec, "ts0": (dts[0] if dts[0] else None)}


def metrics(d, power_w, structure, use_real):
    n = d["n"]
    el = d["elapsed_real"] if (use_real and d["has_real_sec"]) else list(range(n))
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

    g = {"melting_duration": melt,
         "t1_42": first_ge(T["T1"], 42), "t9_42": first_ge(T["T9"], 42),
         "ab_42": grad_at(ab, 42), "ab_50": grad_at(ab, 50),
         "ab_55": grad_at(ab, 55),
         "ac_42": grad_at(ac, 42), "ac_50": grad_at(ac, 50),
         "ac_55": grad_at(ac, 55),
         "duration": el_min[-1] - el_min[0], "t1_end": T["T1"][-1]}
    g["ab_expansion"] = (g["ab_55"] - g["ab_42"]) / g["ab_42"] * 100.0
    return g


def main():
    out_rows = []
    print("规范口径复算 (真实时间戳; IWP 20W 例外=1Hz行号)")
    for power, structure, fname in FILES:
        d = load_file(fname)
        pw = int(power[:-1])
        m = metrics(d, pw, structure, use_real=True)
        m_row = metrics(d, pw, structure, use_real=False)
        tb = "real_ts" if d["has_real_sec"] else "row_1hz"
        row = {"Power": power, "Structure": structure}
        for k, v in m.items():
            row[k] = v
        row["time_base"] = tb
        row["melting_duration_row"] = m_row["melting_duration"]
        row["duration_row"] = m_row["duration"]
        out_rows.append(row)
        print(f"{structure:<10}{power:<4} melt={m['melting_duration']:>6.2f} "
              f"(row={m_row['melting_duration']:>6.2f})  "
              f"dur={m['duration']:>6.2f} (row={m_row['duration']:>6.2f})  "
              f"t1_42={m['t1_42']:>5.2f} t9_42={m['t9_42']:>5.2f} "
              f"ab42={m['ab_42']:>5.2f} ab55={m['ab_55']:>5.2f} "
              f"exp={m['ab_expansion']:>6.2f}% t1_end={m['t1_end']:>6.1f} "
              f"| time_base={tb}")

    outp = os.path.join(ROOT, "output", "paper", "data",
                        "tpms_comprehensive_comparison.csv")
    cols = ["Power", "Structure", "melting_duration", "t1_42", "t9_42",
            "ab_42", "ab_50", "ab_55", "ac_42", "ac_50", "ac_55",
            "ab_expansion", "duration", "t1_end", "time_base",
            "melting_duration_row", "duration_row"]
    with io.open(outp, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for r in out_rows:
            w.writerow(r)
    print("[已写入] output/paper/data/tpms_comprehensive_comparison.csv "
          "(列 + time_base/melting_duration_row/duration_row 供溯源)")


if __name__ == "__main__":
    main()
