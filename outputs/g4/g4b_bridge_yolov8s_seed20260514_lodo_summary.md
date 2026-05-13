# G2 Pretrained Smoke Matrix Summary

Generated: 2026-05-14 00:23, local time

Purpose: verify that the pretrained-detector leave-one-domain-out pipeline can run across all seven RDD2022 domains and expose early cross-domain signal. This is not a full paper-grade result.

## Configuration

- Subset root: `data_processed/g4/g4b_bridge_yolov8s_seed20260514_lodo`
- Model: `yolov8s.pt`
- Epochs: `8`
- Image size: `640`
- Batch: `8`
- Device: `cuda`
- Workers: `0`
- YOLO project: `outputs/g4/g4b_bridge_yolov8s_seed20260514_lodo_train`

## Matrix

| Held-out domain | Status | Train images | Val images | Precision | Recall | mAP50 | mAP50-95 |
|---|---|---:|---:|---:|---:|---:|---:|
| China_Drone | ran | 960 | 80 | 0.1348 | 0.1665 | 0.1064 | 0.0414 |
| China_MotorBike | ran | 960 | 80 | 0.1618 | 0.1588 | 0.1442 | 0.0544 |
| Czech_Republic | ran | 960 | 80 | 0.2207 | 0.1950 | 0.1395 | 0.0503 |
| India | ran | 960 | 80 | 0.2026 | 0.0917 | 0.0698 | 0.0243 |
| Japan | ran | 960 | 80 | 0.2090 | 0.1956 | 0.1480 | 0.0543 |
| Norway | ran | 960 | 80 | 0.1910 | 0.0839 | 0.0626 | 0.0215 |
| United_States | ran | 960 | 80 | 0.2457 | 0.2996 | 0.2265 | 0.0886 |

## Smoke Signal

- Mean mAP50 across held-out domains: `0.1281`
- Mean mAP50-95 across held-out domains: `0.0478`
- Highest held-out mAP50: `United_States` = `0.2265`
- Lowest held-out mAP50: `Norway` = `0.0626`

## Boundary

- Treat these numbers as a reproducibility and go/no-go signal only.
- The run uses the subset sizes shown in the matrix; if those sizes are below the full dataset, label the result as subset-scale.
- A manuscript claim still requires fixed full-scale training, saved predictions, calibration/selective-prediction analysis, and failure taxonomy.
- Low absolute scores from short CPU runs do not invalidate the topic; cross-domain variation and pipeline viability are the useful signal at this gate.
