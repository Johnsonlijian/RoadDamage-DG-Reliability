# Label-Boundary Overlap Summary

Generated: 2026-05-14 00:32, local time

## Configuration

- Prediction table: `R:\NAS_DRIVE\IMUT\1-Research_Output\1-Papers\1-In_Preparation\2026-TRC-RoadDamage-DomainGeneralization\data_processed\predictions\g4b_bridge_yolov8s_seed20260514_lodo_all_predictions.csv`
- XML box table: `R:\NAS_DRIVE\IMUT\1-Research_Output\1-Papers\1-In_Preparation\2026-TRC-RoadDamage-DomainGeneralization\data_processed\rdd2022_boxes.csv`
- Primary labels excluded from boundary boxes: `D00, D10, D20, D40`

## False-Positive Overlap With Non-Primary XML Boxes

| IoU threshold | FP predictions | FP overlapping non-primary XML | Share of FP | Non-primary labels | Domains |
| ---: | ---: | ---: | ---: | --- | --- |
| 0.100 | 111841 | 1715 | 0.015334 | D44:831; Repair:342; D50:210; D01:129; D11:125; D43:78 | Japan:901; India:472; China_Drone:205; China_MotorBike:137 |
| 0.300 | 111841 | 536 | 0.004793 | D44:268; Repair:100; D50:59; D01:55; D11:38; D43:16 | Japan:257; India:179; China_Drone:78; China_MotorBike:22 |
| 0.500 | 111841 | 181 | 0.001618 | D44:96; Repair:27; D50:27; D01:20; D11:10; D43:1 | Japan:88; India:66; China_Drone:22; China_MotorBike:5 |

## Boundary

This post-processing audit asks whether predictions counted as false positives in the four-class task overlap labels that were present in XML but excluded from the supervised label set. It does not redefine the primary task and does not replace a full exclude-vs-merge training sensitivity study.
