# R43 Label-Generation Robustness Audit (RDD2020 v1 vs RDD2022)

Context: RDD2020 train images for Czech/India/Japan are a 100% filename subset of RDD2022 train (verified 2026-06-12: 2,829 / 7,706 / 10,506 images each, full overlap). RDD2020 therefore cannot serve as independent external validation; it is used here as a second, independent annotation generation over identical images to audit the label boundary of the framework.

| domain | images | xml both | boxes 2020 | boxes 2022 | primary 2020 | primary 2022 | matched (IoU>=0.5, same class) | match/2020 | match/2022 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Czech_Republic | 2829 | 2829 | 1745 | 1745 | 1745 | 1745 | 1745 | 1.000 | 1.000 |
| India | 7706 | 7706 | 8203 | 8203 | 6831 | 6831 | 6831 | 1.000 | 1.000 |
| Japan | 10506 | 10506 | 24754 | 24754 | 16470 | 16470 | 16469 | 1.000 | 1.000 |

## Per-class box counts by annotation generation

| domain | class | RDD2020 v1 | RDD2022 |
| --- | --- | ---: | ---: |
| Czech_Republic | D00 | 988 | 988 |
| Czech_Republic | D10 | 399 | 399 |
| Czech_Republic | D20 | 161 | 161 |
| Czech_Republic | D40 | 197 | 197 |
| India | D00 | 1555 | 1555 |
| India | D01 | 179 | 179 |
| India | D0w0 | 1 | 1 |
| India | D10 | 68 | 68 |
| India | D11 | 45 | 45 |
| India | D20 | 2021 | 2021 |
| India | D40 | 3187 | 3187 |
| India | D43 | 57 | 57 |
| India | D44 | 1062 | 1062 |
| India | D50 | 28 | 28 |
| Japan | D00 | 4049 | 4049 |
| Japan | D10 | 3979 | 3979 |
| Japan | D20 | 6199 | 6199 |
| Japan | D40 | 2243 | 2243 |
| Japan | D43 | 736 | 736 |
| Japan | D44 | 3995 | 3995 |
| Japan | D50 | 3553 | 3553 |

## Decisive conclusion (P1-level project correction)

Image sets are 100% filename-contained in RDD2022 AND the primary-class annotations are box-for-box identical (match rates 1.000; Japan differs by a single box out of 16,470). RDD2022 absorbed RDD2020 wholesale for Czech/India/Japan.

Therefore: **RDD2020 provides no independent information relative to RDD2022 — it is invalid as external validation AND empty as a label-generation robustness check.** The R41 plan's 'RDD2020 external validation' module must be removed from the evidence plan. External generalization of acceptance-test workflow remains future work pending a genuinely independent, license-verified dataset; the manuscript must keep the corresponding claim downgraded.

Recommended claim-evidence-map update (for Codex ingest): change the 'method generalizes beyond RDD2022 / RDD2020 candidate' row to 'RDD2020 ruled out 2026-06-12: 100% image+label containment in RDD2022 (verified by sha256-checked download, full filename enumeration, and IoU-matched annotation comparison)'.
