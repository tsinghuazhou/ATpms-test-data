# Input manifest — 2026-09-09 final-draft audit (tpms-pcm-v5)

Audited artifact: paper text of TPMS_PCM_Paper_v5.docx, source of truth =
`scripts/generate_paper_docx_v5.js` (docx 二进制本会话无法读取内嵌图片，见 image track)。

Materials examined:
- `scripts/generate_paper_docx_v5.js` — 38 inline references + full manuscript text (post number-migration commit 38868a0)
- `references_extracted.json` — refs [1]-[38] strings extracted programmatically
- `references_crossref.json` / `references_crossref_v2.json` — Crossref top-3 hits per reference (2026-09-09, bibliographic queries, mailto set)
- `output/paper/data/tpms_comprehensive_comparison.csv` — canonical metrics (real-timestamp basis, 2026-09-09)
- `verify_matrix_20260909.py`, `compute_canonical_matrix_20260909.py` — independent recomputation (Δ=0.000)
- `.openscience/provenance.jsonl` (301 records, excerpted)

Blocked / not examined:
- `output/paper/figures/*.png` (4 images embedded in docx): unreadable this session (cloud offline placeholders; open() → errno 22 / indefinite hang)
- v4/v5 docx binaries: not part of this audit scope beyond generator text
- Poppler/PDF pipeline: not applicable (no PDF manuscript under audit; LaTeX output/paper/main.pdf is the superseded 2-structure generation of 2026-08-04)
