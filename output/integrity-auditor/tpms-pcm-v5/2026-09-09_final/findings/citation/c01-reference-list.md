# C1 — Reference list [1]–[38] largely untraceable (38/38 queried)

## Evidence

All 38 references from the v5 generator were queried against Crossref
(bibliographic query, top-3 hits, 2026-09-09; raw data in
`references_crossref.json`, `references_crossref_v2.json`).

Outcomes by class:

1. **Confirmed real (exact match found)** — 3 refs, e.g.:
   - [29] Zalba et al. 2003 → DOI 10.1016/s1359-4311(02)00192-8, Applied Thermal
     Engineering, title/journal/year identical.
   - [37] Li/Wu/Kao 2011 → DOI 10.1016/j.apenergy.2011.02.030, title/journal/year
     identical.
   - [34] Agyenim et al. 2010 → DOI 10.1016/j.rser.2009.10.015 identical.

2. **No Crossref hit for the claimed title/journal/year combination** — the
   majority of refs (≈25). A bibliographic query returning nothing is not proof
   of absence, but for several refs the claimed volume:page collides exactly
   with a **different, real article**, which is the strong signal:
   - [1] claimed "Qureshi … TPMS-based metal foam heat sinks, IJHMT
     2021;173:121001" → real record at 10.1016/j.ijheatmasstransfer.2021.121001
     is "Heat transfer performance of a finned metal foam-phase change material
     (FMF-PCM) system" — different title, different authors.
   - [15] claimed "Solar Energy Materials and Solar Cells 2011;95:2009-2022" →
     nearest real record is Solar Energy 2011 (10.1016/j.solener.2011.03.021)
     with a near-identical title ("Experimental investigations of porous
     materials in high temperature thermal energy storage systems") — journal
     and pagination differ.
   - [22] claimed "IEEE TCPMT 2014;4:226-252" → real Lau record found is
     TCPMT 2022 (10.1109/tcpmt.2022.3144461); year does not match.
   - [6],[7],[8],[9],[19],[21],[23],[25],[26],[27],[31],[32] and others return
     only unrelated articles in the same broad field.

3. In-text claim citations ride on these entries, e.g. intro: "Qureshi et al.
   [1] … reported significant improvements in temperature uniformity and
   charging time reduction", "Gado [3] … showed Gyroid outperformed Primitive
   and Diamond", "Kaur and Singh [5] established design correlations" — none of
   the supporting records could be traced.

## Finding

- Level 2 (obvious anomaly): a large share of the numbered reference list is
  untraceable against Crossref; several claimed volume:page strings sit on top
  of unrelated real papers. Draft-stage artifact, so not a misconduct verdict,
  but the list must be rebuilt before submission.
- Fix path available in-workspace: `output/paper/bibliography.bib` (217
  CrossRef-verified entries, per notes/2026-08-04) plus the LaTeX manuscript
  citations already resolved there; re-map every in-text claim to a verified
  entry, or replace with newly verified literature.

## Requested raw data / action

Author to supply a verified reference list (DOI-validated) for all 38 slots and
re-check each in-text attribution ("[1] reported …" etc.) against the actual
content of the chosen paper.
