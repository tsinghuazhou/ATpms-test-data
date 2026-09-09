# 论文数字迁移映射表（行号口径 → 真实时间戳口径）

**日期**: 2026-09-09
**目的**: `compare_all_structures.py` 及以其数字写成的论文正文（含 docx 生成器
`scripts/generate_paper_docx.js`、`generate_paper_docx_v5.js`）采用"行号=1s"时间轴，
在采样丢秒文件（主要是 Primitive 10W，真实 26.93 min vs 行号 22.33 min）上低估了
时间类指标。规范口径已定为**真实时间戳**（见 `compute_canonical_matrix_20260909.py`
与 `output/paper/data/tpms_comprehensive_comparison.csv`，`time_base` 列注明例外）。

梯度类指标（A-B/A-C、膨胀率）不受时间口径影响，**无需修改**。

## 1. 主指标替换表（熔融时长 / 时长，分钟）

| 结构 | 功率 | 旧值(行号) | 新值(真实) |
|------|------|-----------|-----------|
| Gyroid | 10W | 11.75 | **11.83** |
| Gyroid | 20W | 2.10 | **2.22** |
| Gyroid | 30W | 0.62 | 0.62（不变） |
| IWP | 10W | 12.33（本就真实） | 12.33（不变） |
| IWP | 20W | 0.93（行号=唯一时间） | 0.93（不变） |
| IWP | 30W | 0.40 | 0.40（不变） |
| Primitive | 10W | 8.28 | **9.43** |
| Primitive | 20W | 0.57 | **0.60** |
| Primitive | 30W | 0.28 | 0.28（不变） |

总时长（若正文引用）: G10 31.97→32.48；G20 11.47→12.15；P10 22.33→26.93；
P20 11.68→11.93；P30 12.03→12.45；I10 29.78（不变）；G30/I30 不变。
T1/T9 达 42°C（若正文引用）以规范 CSV 的 `t1_42`/`t9_42` 列为准。

## 2. 派生数值重算表（正文叙述需改写）

| 表述 | 旧值 | 新值 | 计算 |
|------|------|------|------|
| G 熔融缩短 10→20W | 5.60x | **5.3x** | 11.83/2.22 |
| G 熔融缩短 10→30W | 18.95x | **19.1x** | 11.83/0.62 |
| G 熔融缩短 20→30W | 3.39x | **3.6x** | 2.22/0.62 |
| IWP 熔融缩短 10→20W | 13.26x | 13.3x（不变） | 12.33/0.93 |
| IWP 熔融缩短 10→30W | 30.83x | 30.8x（不变） | 12.33/0.40 |
| P 熔融缩短 10→20W | 14.6x | **15.7x** | 9.43/0.60 |
| P 熔融缩短 10→30W | 29.57x/29.6x | **33.7x** | 9.43/0.28 |
| P 熔融缩短 20→30W | 2.03x | **2.1x** | 0.60/0.28 |
| IWP 比 P 长 (10W) | 48.9% | **30.8%** | 12.33/9.43−1 |
| IWP 比 G 长 (10W) | 4.9% | **4.2%** | 12.33/11.83−1 |
| G 比 P 长 (10W) | ~25% | ~25%（不变） | 11.83/9.43−1=25.4% |
| G 20W 熔融 = IWP 的 | 2.3x | **2.4x** | 2.22/0.93 |

## 3. 更新状态（2026-09-09 执行后）

| 文件 | 状态 |
|------|------|
| `paper_drafts/paper_v3_zh.md` | ✅ 已更新（11 处替换，128% 中文句已改 138%） |
| `paper_drafts/paper_v3_en.md` | ✅ 已更新（15 处替换） |
| `paper_drafts/paper_v4_en.md` | ✅ 已更新（15 处替换） |
| `paper_drafts/results_v2_en.md` | ✅ 已更新（14 处替换） |
| `paper_drafts/MULTI_AGENT_SUMMARY.md` | ✅ 已更新（2 处替换） |
| `scripts/generate_paper_docx_v5.js` | ✅ 已更新（25 处替换 + 1 句改写；`node --check` 通过） |
| `TPMS_PCM_Paper_v5.docx` | ⏳ 待重建（见下） |
| `scripts/generate_paper_docx.js`（v4 docx 来源） | 未改（v4 已被 v5 取代，如需可照同一映射处理） |

**为什么 docx 未能在这里重建**: 本次会话所在机器的云盘上
`output/paper/figures/*.png`（docx 内嵌的 4 张图）处于离线占位状态，读取即报错，
node/git 均无法取到图像字节，因此 `node scripts/generate_paper_docx_v5.js`
无法运行。文本层（本文件 + 各 md + 生成器 js）已全部是规范数字。

**重建 docx 的命令**（在能正常读取 figures 的机器/会话上执行）:
```bash
# 1) 用规范口径重出 4 张图（先确认图内数字来自规范 CSV）
python scripts/plot_fig3_comprehensive.py     # Fig.3 新脚本, 读规范 CSV (compare_all_structures.py 已退役)
python scripts/plot_power_sensitivity.py      # Fig.5 (读规范 CSV)
python scripts/plot_performance_ranking.py    # Fig.6 (读规范 CSV)
python scripts/plot_temperature_curves.py     # Fig.4
# 注: 后三个脚本原为 D:\qqhru.edu.cn\... 机器编写, 路径常量需按机器调整
# 2) 重建 docx
node scripts/generate_paper_docx_v5.js
# 3) 校验: 解包 TPMS_PCM_Paper_v5.docx, 确认旧 token 清零
#    (8.28/11.75/2.10/0.57/29.6×/48.9%/Kaur/Tang et al./Zhou and Qiao 等)
```

> 注意：fig3/fig5 图内柱状图带数值标注（图5 的 × 倍数），图内数字来自
> `output/paper/data/tpms_comprehensive_comparison.csv`——该 CSV 已是规范口径，
> 若原机器上有旧图缓存需用 scripts/plot_power_sensitivity.py、
> plot_performance_ranking.py 等重新出图再嵌入。

## 4. 无需修改

- 所有梯度、膨胀率数值与结论（Δ=0.000）
- 排名结论与机制叙述（排序在两种口径下完全一致）
- 已按真实口径撰写的早期两结构稿（`paper_complete_en/zh`、`results_en/zh`、
  `results_zh.md`、`results_en.md` 等，11.8/9.4 min 即真实口径）
- 各单结构/对比报告 md（`report_primitive_vs_gyroid_10w_update.md`、
  `report_tpms_10w/20w_comprehensive.md`、`report_iwp_*.md` 等，均为真实口径 9.4 min）
