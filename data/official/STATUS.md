# Official vocabulary migration status

Last updated: 2026-10-06

## Source verification

| Dataset | Authority | Version/current basis | Status | Production |
|---|---|---|---|---|
| MOE basic 1200 | MOE / NAER curriculum appendix 5 | current 12-year curriculum list | source confirmed; parser added; extraction/normalization pending | not switched |
| MOE common 2000 | MOE / NAER curriculum appendix 5 | 1200 + other common 800 | source confirmed; parser added; extraction/normalization pending | not switched |
| GEPT Elementary | LTTC | revision completed 2024-02 | source/download confirmed; level-aware parser added; full extraction pending | not switched |
| GEPT Intermediate | LTTC | revision completed 2024-02 | source/download confirmed; level-aware parser added; full extraction pending | hidden/unlockable |
| GEPT High-Intermediate | LTTC | revision completed 2024-02 | source/download confirmed; level-aware parser added; full extraction pending | hidden/unlockable |

## Migration policy

The current playable pools remain unchanged until official snapshots are normalized and validated. No difficulty-derived list may be relabeled as official.

## Next validation outputs

- normalized official entries per source/list
- canonical word matching report against current master vocabulary
- added/removed/shared counts
- variants and phrase exceptions
- source-specific POS/gloss conflicts
- unresolved items requiring review
- final production migration report

## Unlock route

GEPT Intermediate is a B1 vocabulary challenge and is unlockable only after the main path requirements are met.
GEPT High-Intermediate is a B2 vocabulary challenge and requires the B1 challenge first.
These labels describe vocabulary challenge alignment and must not be presented as a formal CEFR proficiency diagnosis.


## Confirmed source semantics (2026-10-06)

- NAER Appendix 5 explicitly separates Table 1 basic 1,200 and Table 2 other common 800; the 2,000 pool is their union.
- The separate country/festival recognition appendix is not counted inside the basic 1,200.
- LTTC states the revised GEPT lists were completed in 2024-02 and contain 7,000+ words across the published levels.
- LTTC cumulative PDFs contain lower-level rows; import must use each row's official 級數 field, not the PDF filename.
- A single word may have multiple POS/senses. Source-specific senses are preserved before creating gameplay content.
- LTTC identifies Elementary / Intermediate / High-Intermediate with CEFR A2 / B1 / B2 respectively; unlock labels are vocabulary challenges, not proficiency certification.
