# Label-Boundary Overlap Summary

Generated: 2026-05-14 00:32, local time

## Configuration

- Prediction table: `<local_project_root>\data_processed\predictions\g4b_bridge_yolov8s_seed20260512_ordinary_predictions.csv`
- XML box table: `<local_project_root>\data_processed\rdd2022_boxes.csv`
- Primary labels excluded from boundary boxes: `D00, D10, D20, D40`

## False-Positive Overlap With Non-Primary XML Boxes

| IoU threshold | FP predictions | FP overlapping non-primary XML | Share of FP | Non-primary labels | Domains |
| ---: | ---: | ---: | ---: | --- | --- |
| 0.100 | 118746 | 1462 | 0.012312 | D44:742; Repair:353; D50:312; D01:55 | Japan:705; India:404; China_MotorBike:177; China_Drone:176 |
| 0.300 | 118746 | 492 | 0.004143 | D44:233; D50:130; Repair:111; D01:18 | Japan:235; India:146; China_Drone:69; China_MotorBike:42 |
| 0.500 | 118746 | 151 | 0.001272 | D44:65; D50:47; Repair:34; D01:5 | Japan:74; India:43; China_Drone:19; China_MotorBike:15 |

## Boundary

This post-processing audit asks whether predictions counted as false positives in the four-class task overlap labels that were present in XML but excluded from the supervised label set. It does not redefine the primary task and does not replace a full exclude-vs-merge training sensitivity study.
