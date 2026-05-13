# Label-Boundary Overlap Summary

Generated: 2026-05-13 18:30, local time

## Configuration

- Prediction table: `data_processed\predictions\g3_frozen_subset_ordinary_predictions.csv`
- XML box table: `data_processed\rdd2022_boxes.csv`
- Primary labels excluded from boundary boxes: `D00, D10, D20, D40`

## False-Positive Overlap With Non-Primary XML Boxes

| IoU threshold | FP predictions | FP overlapping non-primary XML | Share of FP | Non-primary labels | Domains |
| ---: | ---: | ---: | ---: | --- | --- |
| 0.100 | 151091 | 2120 | 0.014031 | D44:1252; Repair:518; D50:262; D01:61; D43:27 | Japan:1184; India:418; China_MotorBike:291; China_Drone:227 |
| 0.300 | 151091 | 662 | 0.004381 | D44:409; Repair:167; D50:64; D01:18; D43:4 | Japan:370; India:125; China_MotorBike:93; China_Drone:74 |
| 0.500 | 151091 | 236 | 0.001562 | D44:129; Repair:70; D50:28; D01:7; D43:2 | Japan:124; India:42; China_MotorBike:35; China_Drone:35 |

## Boundary

This post-processing audit asks whether predictions counted as false positives in the four-class task overlap labels that were present in XML but excluded from the supervised label set. It does not redefine the primary task and does not replace a full exclude-vs-merge training sensitivity study.
