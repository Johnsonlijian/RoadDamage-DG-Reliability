# Label-Boundary Overlap Summary

Generated: 2026-05-14 00:31, local time

## Configuration

- Prediction table: `R:\NAS_DRIVE\IMUT\1-Research_Output\1-Papers\1-In_Preparation\2026-TRC-RoadDamage-DomainGeneralization\data_processed\predictions\g4a_r08_repeat_yolov8n_seed20260513_ordinary_predictions.csv`
- XML box table: `R:\NAS_DRIVE\IMUT\1-Research_Output\1-Papers\1-In_Preparation\2026-TRC-RoadDamage-DomainGeneralization\data_processed\rdd2022_boxes.csv`
- Primary labels excluded from boundary boxes: `D00, D10, D20, D40`

## False-Positive Overlap With Non-Primary XML Boxes

| IoU threshold | FP predictions | FP overlapping non-primary XML | Share of FP | Non-primary labels | Domains |
| ---: | ---: | ---: | ---: | --- | --- |
| 0.100 | 153927 | 2888 | 0.018762 | D44:1713; Repair:683; D50:226; D43:146; D11:69; D01:51 | Japan:1925; China_MotorBike:552; India:280; China_Drone:131 |
| 0.300 | 153927 | 863 | 0.005607 | D44:496; Repair:245; D50:62; D01:22; D11:20; D43:18 | Japan:527; China_MotorBike:200; India:91; China_Drone:45 |
| 0.500 | 153927 | 263 | 0.001709 | D44:150; Repair:76; D50:28; D01:6; D11:2; D43:1 | Japan:159; China_MotorBike:60; India:28; China_Drone:16 |

## Boundary

This post-processing audit asks whether predictions counted as false positives in the four-class task overlap labels that were present in XML but excluded from the supervised label set. It does not redefine the primary task and does not replace a full exclude-vs-merge training sensitivity study.
