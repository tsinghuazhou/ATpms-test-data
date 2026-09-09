# N1 — Experimental numbers reconcile against canonical CSV (verified)

Every headline quantitative claim in the v5 text (abstract + §3) was checked
against `tpms_comprehensive_comparison.csv` (real-timestamp basis) after the
number-migration commit 38868a0:

| Claim in text | CSV value | Match |
|---|---|---|
| G10 melt 11.83 min; P10 9.43 min; G20 2.22 min; P20 0.60 min | same | ok |
| IWP10 12.33; G30 0.62; IWP20 0.93; IWP30 0.40; P30 0.28 min | same | ok |
| A–B gradients 4.43/6.12/7.44 (42 °C) and 5.50/7.33/11.25 (55 °C) @10W | same | ok |
| 20W: 9.08/11.12/13.96 and 12.70/14.64/19.44; 30W: 12.41/14.66/16.08 and 15.75/19.76/24.13 | same | ok |
| expansion 24.25/19.77/51.14 (10W), 39.87/31.64/39.31 (20W), 26.91/34.79/50.01 (30W) | same | ok |
| reduction factors 19.1× (G), 30.8× (IWP), 33.7× (P) | ratios of CSV melts | ok |
| 27.6% / 40.5% better than IWP/Primitive | (6.12−4.43)/6.12, (7.44−4.43)/7.44 | ok |
| 30.8% longer (IWP vs P @10W); 4.2% (IWP vs G); 138% (G vs IWP @20W); 55% (G vs IWP @30W) | recomputed from CSV | ok |
| 64.4% rise in G expansion 24.25→39.87 | recomputed | ok |

No mismatch found in the measured-data claims after migration.
Independent re-derivation script: `verify_matrix_20260909.py` (Δ=0.000 vs CSV).

Residual caution (not a mismatch): Fig. 3/Fig. 5 in the docx are **images**
generated 2026-08-10 from the row-index numbers (see i02): after regeneration
they will match the text above.
