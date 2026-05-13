# Label-Boundary Overlap Summary

Generated: 2026-05-14 00:31, local time

## Configuration

- Prediction table: `R:\NAS_DRIVE\IMUT\1-Research_Output\1-Papers\1-In_Preparation\2026-TRC-RoadDamage-DomainGeneralization\data_processed\predictions\g4a_r08_repeat_yolov8n_seed20260513_lodo_all_predictions.csv`
- XML box table: `R:\NAS_DRIVE\IMUT\1-Research_Output\1-Papers\1-In_Preparation\2026-TRC-RoadDamage-DomainGeneralization\data_processed\rdd2022_boxes.csv`
- Primary labels excluded from boundary boxes: `D00, D10, D20, D40`

## False-Positive Overlap With Non-Primary XML Boxes

| IoU threshold | FP predictions | FP overlapping non-primary XML | Share of FP | Non-primary labels | Domains |
| ---: | ---: | ---: | ---: | --- | --- |
| 0.100 | 144041 | 3875 | 0.026902 | D44:2285; Repair:1152; D43:343; D50:95 | Japan:2170; China_MotorBike:768; India:553; China_Drone:384 |
| 0.300 | 144041 | 1209 | 0.008393 | D44:794; Repair:321; D43:63; D50:31 | Japan:696; China_MotorBike:211; India:192; China_Drone:110 |
| 0.500 | 144041 | 364 | 0.002527 | D44:259; Repair:87; D50:11; D43:7 | Japan:202; India:75; China_MotorBike:54; China_Drone:33 |

## Boundary

This post-processing audit asks whether predictions counted as false positives in the four-class task overlap labels that were present in XML but excluded from the supervised label set. It does not redefine the primary task and does not replace a full exclude-vs-merge training sensitivity study.
