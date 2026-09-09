# I1 — Figure files blocked in this session (evidence path, not a finding on content)

The four images embedded in the docx live under `output/paper/figures/` and are
offline placeholders on this machine: `open()` on
`tpms_comprehensive_comparison.png` raises `OSError: [Errno 22]` (chunked read)
or hangs indefinitely (whole-file read); same for `power_sensitivity.png`,
`performance_ranking.png`, `temperature_curves.png`; `copy`, node fs and git
pack reads fail identically (git: `fatal: mmap failed: Invalid argument`).
Per-session limitation → image-content forensics (dup / splice checks) not
performed. Re-run when the folder hydrates.
