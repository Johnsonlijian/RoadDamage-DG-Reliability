# Label-Boundary Overlap Summary

Generated: 2026-05-13 18:29, local time

## Configuration

- Prediction table: `data_processed\predictions\g3_frozen_subset_lodo_all_predictions.csv`
- XML box table: `data_processed\rdd2022_boxes.csv`
- Primary labels excluded from boundary boxes: `D00, D10, D20, D40`

## False-Positive Overlap With Non-Primary XML Boxes

| IoU threshold | FP predictions | FP overlapping non-primary XML | Share of FP | Non-primary labels | Domains |
| ---: | ---: | ---: | ---: | --- | --- |
| 0.100 | 141032 | 3319 | 0.023534 | D44:1794; Repair:1243; D50:226; D43:29; D01:27 | Japan:1849; China_MotorBike:750; China_Drone:493; India:227 |
| 0.300 | 141032 | 996 | 0.007062 | D44:539; Repair:373; D50:67; D01:13; D43:4 | Japan:557; China_MotorBike:225; China_Drone:148; India:66 |
| 0.500 | 141032 | 295 | 0.002092 | D44:157; Repair:108; D50:25; D01:5 | Japan:163; China_MotorBike:72; China_Drone:36; India:24 |

## Boundary

This post-processing audit asks whether predictions counted as false positives in the four-class task overlap labels that were present in XML but excluded from the supervised label set. It does not redefine the primary task and does not replace a full exclude-vs-merge training sensitivity study.
