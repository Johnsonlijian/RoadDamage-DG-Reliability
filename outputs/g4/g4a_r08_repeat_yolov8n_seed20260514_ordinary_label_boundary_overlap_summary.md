# Label-Boundary Overlap Summary

Generated: 2026-05-14 00:31, local time

## Configuration

- Prediction table: `<local_project_root>\data_processed\predictions\g4a_r08_repeat_yolov8n_seed20260514_ordinary_predictions.csv`
- XML box table: `<local_project_root>\data_processed\rdd2022_boxes.csv`
- Primary labels excluded from boundary boxes: `D00, D10, D20, D40`

## False-Positive Overlap With Non-Primary XML Boxes

| IoU threshold | FP predictions | FP overlapping non-primary XML | Share of FP | Non-primary labels | Domains |
| ---: | ---: | ---: | ---: | --- | --- |
| 0.100 | 157396 | 3372 | 0.021424 | D44:1725; Repair:1157; D50:336; D43:102; D01:52 | Japan:1685; China_MotorBike:903; India:530; China_Drone:254 |
| 0.300 | 157396 | 1029 | 0.006538 | D44:562; Repair:342; D50:95; D43:16; D01:14 | Japan:513; China_MotorBike:252; India:174; China_Drone:90 |
| 0.500 | 157396 | 302 | 0.001919 | D44:165; Repair:96; D50:33; D43:5; D01:3 | Japan:149; China_MotorBike:61; India:57; China_Drone:35 |

## Boundary

This post-processing audit asks whether predictions counted as false positives in the four-class task overlap labels that were present in XML but excluded from the supervised label set. It does not redefine the primary task and does not replace a full exclude-vs-merge training sensitivity study.
