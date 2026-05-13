# G2 Pretrained Smoke Matrix Summary

Generated: 2026-05-13 23:16, local time

Purpose: verify that the pretrained-detector leave-one-domain-out pipeline can run across all seven RDD2022 domains and expose early cross-domain signal. This is not a full paper-grade result.

## Configuration

- Subset root: `data_processed/g4/g4b_bridge_yolov8s_seed20260513_lodo`
- Model: `yolov8s.pt`
- Epochs: `8`
- Image size: `640`
- Batch: `8`
- Device: `cuda`
- Workers: `0`
- YOLO project: `outputs/g4/g4b_bridge_yolov8s_seed20260513_lodo_train`

## Matrix

| Held-out domain | Status | Train images | Val images | Precision | Recall | mAP50 | mAP50-95 |
|---|---|---:|---:|---:|---:|---:|---:|
| China_Drone | ran | 960 | 80 | 0.5461 | 0.1070 | 0.1226 | 0.0509 |
| China_MotorBike | ran | 960 | 80 | 0.1152 | 0.2307 | 0.0854 | 0.0235 |
| Czech_Republic | ran | 960 | 80 | 0.2488 | 0.2405 | 0.1492 | 0.0448 |
| India | ran | 960 | 80 | 0.3997 | 0.0735 | 0.0514 | 0.0272 |
| Japan | ran | 960 | 80 | 0.2560 | 0.2347 | 0.1701 | 0.0614 |
| Norway | ran | 960 | 80 | 0.0936 | 0.0696 | 0.0306 | 0.0107 |
| United_States | ran | 960 | 80 | 0.2263 | 0.3403 | 0.1931 | 0.0869 |

## Smoke Signal

- Mean mAP50 across held-out domains: `0.1146`
- Mean mAP50-95 across held-out domains: `0.0436`
- Highest held-out mAP50: `United_States` = `0.1931`
- Lowest held-out mAP50: `Norway` = `0.0306`

## Boundary

- Treat these numbers as a reproducibility and go/no-go signal only.
- The run uses the subset sizes shown in the matrix; if those sizes are below the full dataset, label the result as subset-scale.
- A manuscript claim still requires fixed full-scale training, saved predictions, calibration/selective-prediction analysis, and failure taxonomy.
- Low absolute scores from short CPU runs do not invalidate the topic; cross-domain variation and pipeline viability are the useful signal at this gate.
