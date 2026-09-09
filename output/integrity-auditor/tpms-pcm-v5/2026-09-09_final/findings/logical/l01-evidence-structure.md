# L1 — Claims stronger than the evidence structure (draft-stage gaps)

1. **Single-run cells, no error bars** — every Power×Structure cell is one run
   except Gyroid 10W (two valid runs). Headline statements ("Gyroid exhibits
   the lowest gradients across all power levels", "ranking reversal") have no
   quantified uncertainty; spread between the two G10 runs (~1 °C on A–B
   gradients) suggests run-to-run variation of the same order as some
   cross-structure differences (e.g., IWP 6.12 vs Gyroid 4.43 °C @42 °C).
   Level 1 — needs repeats (10W trio first) or a stated limitation paragraph.

2. **Group definitions differ across structures** — B = mean(T2,T3,T5) for
   Gyroid/Primitive vs mean(T2,T3) for IWP; C = T9 vs mean(T8,T9) (IWP 10/20W).
   Cross-topology gradient comparisons therefore mix sensor count/location;
   methods §2.4 states the exclusions (T4, IWP T5) but the paper never says the
   remaining group sizes are unequal. Level 2 — state explicitly in §2.4/§3
   and, ideally, re-derive the IWP gradients with a same-sensor rule as a
   robustness check.

3. **Mechanism claims go beyond the measurements** — the discussion attributes
   results to "chiral secondary flows that promote fluid mixing" (Gyroid),
   "thermal saturation" (IWP), "thermal bottlenecking / limited connectivity"
   (Primitive). Only 9 surface/interior thermocouple traces were measured; no
   flow visualization, pressure data, or pore-scale simulation supports the
   mechanism statements. Level 1 — reword as hypotheses, or add a supporting
   CFD/numerical section.

4. **Melting-window metric is a near-heater, T1-only construct** — "complete
   melting duration" is the time T1 spends in [42, 52] °C; the top layer (T9)
   in several runs never leaves the sensible-heating regime within the record,
   and multiple records end while T1 is still rising above 100 °C (truncated
   before thermal equilibrium). The phrase "indicating full melting of PCM near
   the heater" (§2.4) is accurate, but "melting duration … latent heat
   utilization" (§3.1–3.4) overstates sample-wide melting. Level 2 — rename to
   "near-heater melting window" or add top-layer evidence (T9 ≥42 °C fraction).

5. **"No prior experimental study compared three TPMS topologies"** — a strong
   novelty claim carried by untraceable references (see c01); re-verify with
   the rebuilt reference list before submission.
