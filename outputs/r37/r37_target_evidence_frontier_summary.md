# R37 Target-Evidence Confidence-Frontier Audit

Generated: 2026-05-22 15:39, local time

## Scope

R37 recomputes prediction exports, calibration bins, and confidence frontiers on the R36 K=20 target-evaluation splits. Each held-out domain is evaluated twice on the same split: once with the original source-only YOLOv8s LODO checkpoint and once after fine-tuning that checkpoint with 20 labelled target-domain images. The 20 target images are not included in the evaluation split.

## Pooled Results

| Variant | Prediction rows | GT objects | Stream precision | Stream recall | ECE proxy | High-conf gap | Peak precision | Threshold at peak | Coverage at peak | Reaches 0.10 precision floor |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| source_only | 67788 | 974 | 0.0096 | 0.6674 | 0.0051 | 0.0943 | 0.6875 | 0.500000 | 0.0007 | yes |
| target_evidence_k20 | 76073 | 974 | 0.0091 | 0.7105 | 0.0027 | 0.1093 | 0.7273 | 0.500000 | 0.0001 | yes |

## Domain-Level Peak Precision

| Domain | Source-only peak precision | K=20 target-evidence peak precision | Source reaches 0.10 floor | Target-evidence reaches 0.10 floor |
|---|---:|---:|---|---|
| China_Drone | 1.0000 | 0.4375 | yes | yes |
| China_MotorBike | 0.5556 | 0.5588 | yes | yes |
| Czech_Republic | 1.0000 | 0.8889 | yes | yes |
| India | 0.2222 | 0.5000 | yes | yes |
| Japan | 0.7273 | 0.6667 | yes | yes |
| Norway | 0.7143 | 1.0000 | yes | yes |
| United_States | 0.9286 | 0.6667 | yes | yes |

## Interpretation Boundary

- R37 is a single-seed diagnostic pass designed to test whether the R36 local-evidence mAP gains also improve confidence-frontier interpretation.
- Prediction-row precision is not AP and should not be reported as a deployment operating point.
- If target evidence improves mAP but not the frontier, the manuscript should interpret local fine-tuning as necessary evidence collection rather than as a deployment solution.

## Files

- Summary CSV: `R:\NAS_DRIVE\IMUT\1-Research_Output\1-Papers\1_In_Preparation\2026-TRC-RoadDamage-DomainGeneralization\data_processed\r37_target_evidence_frontier\r37_target_evidence_frontier_summary.csv`
- Figure PNG: `R:\NAS_DRIVE\IMUT\1-Research_Output\1-Papers\1_In_Preparation\2026-TRC-RoadDamage-DomainGeneralization\submission_package\JCICE_RoadDamageDG_2026-05-22\figures_enhanced\fig16_r37_target_evidence_confidence_frontier.png`
- Figure SVG: `R:\NAS_DRIVE\IMUT\1-Research_Output\1-Papers\1_In_Preparation\2026-TRC-RoadDamage-DomainGeneralization\submission_package\JCICE_RoadDamageDG_2026-05-22\figures_enhanced\fig16_r37_target_evidence_confidence_frontier.svg`
