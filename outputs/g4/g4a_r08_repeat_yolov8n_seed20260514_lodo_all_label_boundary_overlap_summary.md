# Label-Boundary Overlap Summary

Generated: 2026-05-14 00:31, local time

## Configuration

- Prediction table: `<local_project_root>\data_processed\predictions\g4a_r08_repeat_yolov8n_seed20260514_lodo_all_predictions.csv`
- XML box table: `<local_project_root>\data_processed\rdd2022_boxes.csv`
- Primary labels excluded from boundary boxes: `D00, D10, D20, D40`

## False-Positive Overlap With Non-Primary XML Boxes

| IoU threshold | FP predictions | FP overlapping non-primary XML | Share of FP | Non-primary labels | Domains |
| ---: | ---: | ---: | ---: | --- | --- |
| 0.100 | 152905 | 2865 | 0.018737 | D44:1661; Repair:494; D50:260; D01:177; D43:173; D11:100 | Japan:1692; India:679; China_Drone:269; China_MotorBike:225 |
| 0.300 | 152905 | 874 | 0.005716 | D44:510; Repair:166; D50:68; D01:54; D43:44; D11:32 | Japan:500; India:208; China_Drone:88; China_MotorBike:78 |
| 0.500 | 152905 | 270 | 0.001766 | D44:162; Repair:55; D50:23; D01:20; D11:5; D43:5 | Japan:145; India:70; China_Drone:30; China_MotorBike:25 |

## Boundary

This post-processing audit asks whether predictions counted as false positives in the four-class task overlap labels that were present in XML but excluded from the supervised label set. It does not redefine the primary task and does not replace a full exclude-vs-merge training sensitivity study.
