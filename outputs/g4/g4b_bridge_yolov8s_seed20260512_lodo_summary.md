# G2 Pretrained Smoke Matrix Summary

Generated: 2026-05-13 22:09, local time

Purpose: verify that the pretrained-detector leave-one-domain-out pipeline can run across all seven RDD2022 domains and expose early cross-domain signal. This is not a full paper-grade result.

## Configuration

- Subset root: `data_processed/g4/g4b_bridge_yolov8s_seed20260512_lodo`
- Model: `yolov8s.pt`
- Epochs: `8`
- Image size: `640`
- Batch: `8`
- Device: `cuda`
- Workers: `0`
- YOLO project: `outputs/g4/g4b_bridge_yolov8s_seed20260512_lodo_train`

## Matrix

| Held-out domain | Status | Train images | Val images | Precision | Recall | mAP50 | mAP50-95 |
|---|---|---:|---:|---:|---:|---:|---:|
| China_Drone | ran | 960 | 80 | 0.9882 | 0.2500 | 0.2972 | 0.1794 |
| China_MotorBike | ran | 960 | 80 | 0.1210 | 0.2015 | 0.1145 | 0.0331 |
| Czech_Republic | ran | 960 | 80 | 0.2526 | 0.2246 | 0.1535 | 0.0502 |
| India | ran | 960 | 80 | 0.2987 | 0.0872 | 0.0593 | 0.0228 |
| Japan | ran | 960 | 80 | 0.1571 | 0.2621 | 0.1446 | 0.0609 |
| Norway | ran | 960 | 80 | 0.1758 | 0.0925 | 0.0601 | 0.0235 |
| United_States | ran | 960 | 80 | 0.1862 | 0.4127 | 0.1883 | 0.0673 |

## Smoke Signal

- Mean mAP50 across held-out domains: `0.1454`
- Mean mAP50-95 across held-out domains: `0.0625`
- Highest held-out mAP50: `China_Drone` = `0.2972`
- Lowest held-out mAP50: `India` = `0.0593`

## Boundary

- Treat these numbers as a reproducibility and go/no-go signal only.
- The run uses the subset sizes shown in the matrix; if those sizes are below the full dataset, label the result as subset-scale.
- A manuscript claim still requires fixed full-scale training, saved predictions, calibration/selective-prediction analysis, and failure taxonomy.
- Low absolute scores from short CPU runs do not invalidate the topic; cross-domain variation and pipeline viability are the useful signal at this gate.
