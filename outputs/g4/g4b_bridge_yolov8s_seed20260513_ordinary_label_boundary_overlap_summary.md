# Label-Boundary Overlap Summary

Generated: 2026-05-14 00:32, local time

## Configuration

- Prediction table: `<local_project_root>\data_processed\predictions\g4b_bridge_yolov8s_seed20260513_ordinary_predictions.csv`
- XML box table: `<local_project_root>\data_processed\rdd2022_boxes.csv`
- Primary labels excluded from boundary boxes: `D00, D10, D20, D40`

## False-Positive Overlap With Non-Primary XML Boxes

| IoU threshold | FP predictions | FP overlapping non-primary XML | Share of FP | Non-primary labels | Domains |
| ---: | ---: | ---: | ---: | --- | --- |
| 0.100 | 131643 | 2032 | 0.015436 | D44:1108; Repair:538; D50:219; D11:80; D01:50; D43:37 | Japan:1209; China_MotorBike:429; India:285; China_Drone:109 |
| 0.300 | 131643 | 604 | 0.004588 | D44:338; Repair:146; D50:73; D01:22; D11:22; D43:3 | Japan:366; China_MotorBike:110; India:92; China_Drone:36 |
| 0.500 | 131643 | 175 | 0.001329 | D44:93; Repair:41; D50:34; D01:6; D11:1 | Japan:107; China_MotorBike:35; India:27; China_Drone:6 |

## Boundary

This post-processing audit asks whether predictions counted as false positives in the four-class task overlap labels that were present in XML but excluded from the supervised label set. It does not redefine the primary task and does not replace a full exclude-vs-merge training sensitivity study.
