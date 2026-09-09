# 实验溯源文件夹

本目录存放论文方法节所有参数的原始证据文件。**投稿前必须补齐**，否则审稿人会质疑数据来源。

## 审计发现（2026-09-09 integrity-auditor）

论文 v5 方法节（§2.2–2.4）包含以下**无源参数**（审计 n02 项）：

| 参数 | 论文位置 | 需要证据 |
|---|---|---|
| ±0.5 °C 测量不确定度 | §2.2 | 热电偶校准证书 / 标定记录 |
| <3% 侧面与顶面热损失 | §2.2 | 热损失标定实验数据 |
| 石蜡熔点 42 °C、潜热 200 kJ/kg | §2.1 | 石蜡规格书 / DSC 测试报告 |
| 石蜡"negligible supercooling" | §2.1 | DSC 冷却曲线 |
| 金属晶格相对密度 >99% | §2.1 | 微-CT 报告 / 阿基米德法测量 |
| 激光功率 200 W、扫描速度 800 mm/s、层厚 30 μm、搭接间距 0.12 mm、旋转角 67° | §2.1 | SLM 打印参数记录 |
| 应力消除：300 °C / 2 h | §2.1 | 热处理炉温曲线记录 |
| 真空灌注：−0.09 MPa | §2.1 | 真空系统压力记录 |
| PCM 装载量 ±2%、称重 ±0.01 g | §2.1 | 天平校准证书 + 称重记录 |
| 环境温度 23 ± 1 °C | §2.2 | 实验室温控记录 |
| 热电偶线径 0.25 mm、 bead 直径 ~0.5 mm | §2.2 | 热电偶规格书 |
| NI-9213 数据采集 | §2.2 | 设备手册 / 校准证书 |
| 导热膏 >1.5 W/(m·K) | §2.2 | 导热膏规格书 |

## 文件组织建议

```
experimental_provenance/
├── README.md                          ← 本文件
├── thermocouple_calibration/
│   ├── calibration_certificate.pdf    ← 热电偶校准证书
│   └── calibration_log_20260730.md    ← 每次实验前的标定记录
├── pcm_material/
│   ├── paraffin_datasheet.pdf         ← 石蜡规格书（含熔点、潜热、导热系数）
│   ├── dsc_heating_curve.png          ← DSC 升温曲线（验证熔点 42 °C）
│   └── dsc_cooling_curve.png          ← DSC 冷却曲线（验证 negligible supercooling）
├── lattice_manufacturing/
│   ├── slm_parameters_20260725.md     ← SLM 打印参数记录（激光功率、扫描速度等）
│   ├── micro_ct_report.pdf            ← 微-CT 报告（相对密度 >99%）
│   └── stress_relief_log.md           ← 热处理炉温曲线
├── experimental_setup/
│   ├── heater_calibration.md          ← 加热片功率标定
│   ├── insulation_loss_test.md        ← 热损失标定实验（<3%）
│   ├── thermal_paste_spec.pdf         ← 导热膏规格书
│   └── daq_manual.pdf                 ← NI-9213 手册
└── experimental_logs/
    ├── log_20260730_gyroid_10w.md     ← 每次实验的详细记录
    ├── log_20260808_gyroid_10w_new.md
    └── ...
```

## 模板

- `calibration_template.md` — 热电偶校准记录模板
- `material_specs_template.md` — 材料规格书模板
- `experimental_log_template.md` — 实验记录模板

## 下一步

1. 按模板填写原件，扫描/拍照后放入对应子目录
2. 在论文方法节加一句："详细参数与原始数据见 `experimental_provenance/`"
3. 投稿时作为 supplementary material 上传

---

**审计状态**：n02 项待消（等原件补齐）
