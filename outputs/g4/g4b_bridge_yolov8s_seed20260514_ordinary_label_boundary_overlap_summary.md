# Label-Boundary Overlap Summary

Generated: 2026-05-14 00:32, local time

## Configuration

- Prediction table: `<local_project_root>\data_processed\predictions\g4b_bridge_yolov8s_seed20260514_ordinary_predictions.csv`
- XML box table: `<local_project_root>\data_processed\rdd2022_boxes.csv`
- Primary labels excluded from boundary boxes: `D00, D10, D20, D40`

## False-Positive Overlap With Non-Primary XML Boxes

| IoU threshold | FP predictions | FP overlapping non-primary XML | Share of FP | Non-primary labels | Domains |
| ---: | ---: | ---: | ---: | --- | --- |
| 0.100 | 121288 | 2227 | 0.018361 | D44:1035; Repair:827; D50:250; D01:71; D43:44 | Japan:859; China_MotorBike:706; India:541; China_Drone:121 |
| 0.300 | 121288 | 713 | 0.005879 | D44:366; Repair:225; D50:97; D01:21; D43:4 | Japan:296; India:192; China_MotorBike:190; China_Drone:35 |
| 0.500 | 121288 | 226 | 0.001863 | D44:114; Repair:70; D50:37; D01:5 | Japan:100; India:56; China_MotorBike:56; China_Drone:14 |

## Boundary

This post-processing audit asks whether predictions counted as false positives in the four-class task overlap labels that were present in XML but excluded from the supervised label set. It does not redefine the primary task and does not replace a full exclude-vs-merge training sensitivity study.
