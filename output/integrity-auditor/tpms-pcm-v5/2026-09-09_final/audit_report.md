# Audit report — tpms-pcm-v5 (final draft, 2026-09-09)

Scope: manuscript text embedded in `scripts/generate_paper_docx_v5.js`
(TPMS_PCM_Paper_v5.docx source), canonical data, and figure provenance.
Audit performed on the post-migration commit 38868a0.
This report grades findings; it is evidence, not a verdict on authorship.

## Finding summary

| ID | Track | Level | Short |
|----|-------|-------|-------|
| c01 | citation | 2 | Reference list [1]–[38] largely untraceable; ≥3 exact-volume:page collisions with unrelated real papers |
| n01 | numerical | ok | All headline numbers reconcile with canonical CSV (Δ=0 after migration) |
| n02 | numerical | 1 | Methodological numbers without in-repo sources (±0.5 °C, <3% loss, 200 kJ/kg, 99% micro-CT, ±2% loading …) |
| i01 | image | blocked | Figures unreadable this session (offline placeholders) — image forensics not run |
| i02 | image | 2 | All 4 embedded figures (2026-08-10) predate canonical CSV (2026-09-09); pixel labels still row-index numbers |
| l01 | logical | 1–2 | Single runs w/o repeats; unequal B/C group definitions across topologies; mechanism claims beyond measured data; "melting duration" = near-heater T1 window; novelty claim rides on untraceable refs |
| l02 | logical | ok | Sensor exclusions, thermocouple layout, window definition internally consistent |

## Priority order for the author

1. **Rebuild the reference list** from DOI-verified sources (use
   `output/paper/bibliography.bib`, 217 CrossRef-verified entries) and re-check
   each in-text attribution (c01). Highest risk item for submission.
2. **Regenerate all four figures** from the canonical CSV (fix/retire
   `compare_all_structures.py` first) and rebuild the docx (i02).
3. **State the limitations explicitly**: single runs per cell; unequal sensor
   groups across structures; T1-window definition of melting; method numbers
   traceable only to lab notebooks (l01-1/2/4, n02).
4. Decide whether the mechanism paragraphs stay as hypotheses or get CFD
   support (l01-3).

## Requested raw data (to resolve Level ≥2 items)

- c01: DOI-validated replacement list for all 38 references, plus the specific
  papers behind the intro attributions ([1], [2], [3], [5], [6], [21], [23]).
- i02: regenerated figure files (from canonical CSV) + the CSV-driven figure
  script used.
- l01-4: top-layer temperature evidence or a wording change to "near-heater
  melting window".

No editorial verdicts are implied. Absence of a finding in a track means the
track was not applicable or was blocked, as recorded in
`findings/{image,i01-i02,logical,numerical}/*.md` and `input_manifest.md`.
