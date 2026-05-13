# Label-Boundary Overlap Summary

Generated: 2026-05-14 00:32, local time

## Configuration

- Prediction table: `R:\NAS_DRIVE\IMUT\1-Research_Output\1-Papers\1-In_Preparation\2026-TRC-RoadDamage-DomainGeneralization\data_processed\predictions\g4b_bridge_yolov8s_seed20260512_lodo_all_predictions.csv`
- XML box table: `R:\NAS_DRIVE\IMUT\1-Research_Output\1-Papers\1-In_Preparation\2026-TRC-RoadDamage-DomainGeneralization\data_processed\rdd2022_boxes.csv`
- Primary labels excluded from boundary boxes: `D00, D10, D20, D40`

## False-Positive Overlap With Non-Primary XML Boxes

| IoU threshold | FP predictions | FP overlapping non-primary XML | Share of FP | Non-primary labels | Domains |
| ---: | ---: | ---: | ---: | --- | --- |
| 0.100 | 111282 | 2116 | 0.019015 | D44:1037; Repair:851; D50:192; D01:19; D43:17 | Japan:1104; China_MotorBike:428; China_Drone:423; India:161 |
| 0.300 | 111282 | 648 | 0.005823 | D44:364; Repair:199; D50:71; D01:14 | Japan:398; China_Drone:114; China_MotorBike:85; India:51 |
| 0.500 | 111282 | 204 | 0.001833 | D44:104; Repair:55; D50:34; D01:11 | Japan:125; China_Drone:33; India:24; China_MotorBike:22 |

## Boundary

This post-processing audit asks whether predictions counted as false positives in the four-class task overlap labels that were present in XML but excluded from the supervised label set. It does not redefine the primary task and does not replace a full exclude-vs-merge training sensitivity study.
