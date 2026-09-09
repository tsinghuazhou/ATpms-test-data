# Reference list rebuild — mapping and verification evidence

Date: 2026-09-09. All 13 entries were pulled from Crossref records
(`final_reference_metadata.json`, fetched 2026-09-09) — DOI, title, journal,
year, volume, page are verbatim from the registry. The old 38-entry list
contained at least ~10 entries with no Crossref record (see
`references_crossref_v2.json` + `c01-reference-list.md`); the rewrite keeps
only entries that resolve to a real record and that topically support the
sentence where they are cited.

## Old → new slot mapping

| New | Replaces | Verbatim Crossref record |
|-----|----------|--------------------------|
| 1 Ebrahimi K., Jones G.F., Fleischer A.S. RSER 2014;31:622-638 | [19]-type "data-center review" | 10.1016/j.rser.2013.12.007 |
| 2 Kandasamy R., Wang X.Q., Mujumdar A.S. ATE 2008;28:1047-1057 | [3]-type PCM buffering | 10.1016/j.applthermaleng.2007.06.010 |
| 3 Qureshi Z.A., Al-Omari S.A.B., Elnajjar E., Al-Ketan O., Abu Al-Rub R. IJTS 2022;173:107361 | [1,5]-type TPMS interest | 10.1016/j.ijthermalsci.2021.107361 |
| 4 Zhao W., Deng H., Xiao Y., Yan K. ATE 2026;303:132046 | [5]-type TPMS heat-exchanger design | 10.1016/j.applthermaleng.2026.132046 |
| 5 Peng H., Hu Z.C. ATE 2025;279:127707 | [6]-type Gyroid convective transfer | 10.1016/j.applthermaleng.2025.127707 |
| 6 Qureshi Z.A., Elnajjar E., Al-Ketan O., Al-Rub R.A., Al-Omari S.B. IJHMT 2021;170:121001 | [1] "Qureshi TPMS metal foams" (claimed vol 173 was wrong; real vol 170 and title differs) | 10.1016/j.ijheatmasstransfer.2021.121001 |
| 7 Qureshi Z.A., Al Omari S.A.B., Elnajjar E., Mahmoud F., Al-Ketan O., Al-Rub R.A. CSTE 2021;27:101315 | [2] "3D-printed TPMS + PCM" (claimed vol 28 wrong; real 27) | 10.1016/j.csite.2021.101315 |
| 8 Gado M.G. ATE 2025;258:124504 | [3] "Gado TPMS heat sinks" (claimed 2023;218:119534 does not exist) | 10.1016/j.applthermaleng.2024.124504 |
| 9 Qin K., Yang S., Lv T., Zhao X., Tang X. IJHFF 2026;118:110227 | [6] "Tang chiral secondary flows" | 10.1016/j.ijheatfluidflow.2025.110227 |
| 10 Qureshi Z.A., Al-Omari S.A.B., Elnajjar E., Al-Ketan O., Al-Rub R.A. IJHMT 2022;183:122111 | [2]-adjacent AM/porosity claim | 10.1016/j.ijheatmasstransfer.2021.122111 |
| 11 Guo Y., Yang H., Lin G., Jin H., Shen X., He J., et al. CJA 2021;34:373-385 | [21] (real paper found with same topic) | 10.1016/j.cja.2020.07.033 |
| 12 Zhang P., Meng Z., Zhu H., Wang Y., Peng S. Applied Energy 2017;185:1971-1983 | [23] "copper foam saturated with PCM" | 10.1016/j.apenergy.2015.10.075 |
| 13 Arqam M., Raffa L.S., Ryall M., Islam M.S., Bennett N.S. JES 2025;132:117784 | new (experimental TPMS-PCM now appearing) | 10.1016/j.est.2025.117784 |

## Claim wording

Attribution sentences were rewritten to the real papers' verifiable scope
(title/journal level; Crossref returned no abstracts for these records).
Old assertions that could not be attached to any real record (e.g., "Gado
showed Gyroid outperformed Primitive and Diamond", "Kaur and Singh established
Nusselt/friction correlations") were either removed or replaced by
title-supported statements.

## Verification

- `node --check scripts/generate_paper_docx_v5.js` passes.
- Body marker first-use order is strictly ascending: 1,2,3,4,5,3,6,7,8,9,4,7,10,11,12,8,10,13.
- Reference section holds exactly 13 entries matching every body marker.
- Residual scan for all old author names / old markers / old numbers: zero.

Remaining actions: figure regeneration + docx rebuild (see image findings);
md drafts (paper_v3/v4/results_v2) still carry the old 38-item lists and old
attribution prose — they are superseded drafts, update only if they are kept
as living documents.
