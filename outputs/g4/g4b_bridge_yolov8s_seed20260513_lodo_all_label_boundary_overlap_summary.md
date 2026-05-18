# Label-Boundary Overlap Summary

Generated: 2026-05-14 00:32, local time

## Configuration

- Prediction table: `<local_project_root>\data_processed\predictions\g4b_bridge_yolov8s_seed20260513_lodo_all_predictions.csv`
- XML box table: `<local_project_root>\data_processed\rdd2022_boxes.csv`
- Primary labels excluded from boundary boxes: `D00, D10, D20, D40`

## False-Positive Overlap With Non-Primary XML Boxes

| IoU threshold | FP predictions | FP overlapping non-primary XML | Share of FP | Non-primary labels | Domains |
| ---: | ---: | ---: | ---: | --- | --- |
| 0.100 | 97077 | 2043 | 0.021045 | D44:1091; Repair:830; D43:110; D50:12 | Japan:1047; China_MotorBike:572; China_Drone:258; India:166 |
| 0.300 | 97077 | 644 | 0.006634 | D44:391; Repair:224; D43:23; D50:6 | Japan:363; China_MotorBike:147; China_Drone:77; India:57 |
| 0.500 | 97077 | 196 | 0.002019 | D44:137; Repair:54; D43:4; D50:1 | Japan:115; China_MotorBike:41; India:27; China_Drone:13 |

## Boundary

This post-processing audit asks whether predictions counted as false positives in the four-class task overlap labels that were present in XML but excluded from the supervised label set. It does not redefine the primary task and does not replace a full exclude-vs-merge training sensitivity study.
