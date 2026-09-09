# I2 — All four docx figures predate the canonical dataset (stale)

- `tpms_comprehensive_comparison.png` (Fig. 3), `temperature_curves.png`
  (Fig. 4), `power_sensitivity.png` (Fig. 5), `performance_ranking.png`
  (Fig. 6) were generated 2026-08-10 (file mtimes; pre-commit 52c1aac).
- The canonical CSV they must display was finalized 2026-09-09 (real-timestamp
  basis, commit 52c1aac). Fig. 5 annotates bars with numeric × labels and
  Fig. 3 panel (a) shows melting-duration bars — those pixels still encode the
  row-index numbers (e.g., 8.28 min, 29.6×) and now contradict the corrected
  text (9.43 min, 33.7×).
- Provenance: `.openscience/provenance.jsonl` holds no newer record for these
  four PNGs than the Aug-10 run records; text generator
  `scripts/generate_paper_docx_v5.js` itself was updated 2026-09-09
  (commit 38868a0) — so figure (older) vs text (newer) mismatch is confirmed
  by file chronology alone.

Level 2 — figures must be regenerated before the docx is rebuilt.
Note: `scripts/plot_power_sensitivity.py` and `plot_performance_ranking.py`
read the canonical CSV (good), but `compare_all_structures.py` — the source of
Fig. 3 — still recomputes row-index metrics internally and overwrites the
canonical CSV; it must be retired/replaced with a CSV-driven plotter.
