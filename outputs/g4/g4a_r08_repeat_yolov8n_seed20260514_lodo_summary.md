# G2 Pretrained Smoke Matrix Summary

Generated: 2026-05-13 20:51, local time

Purpose: verify that the pretrained-detector leave-one-domain-out pipeline can run across all seven RDD2022 domains and expose early cross-domain signal. This is not a full paper-grade result.

## Configuration

- Subset root: `data_processed/g4/g4a_r08_repeat_yolov8n_seed20260514_lodo`
- Model: `yolov8n.pt`
- Epochs: `4`
- Image size: `320`
- Batch: `8`
- Device: `cuda`
- Workers: `0`
- YOLO project: `outputs/g4/g4a_r08_repeat_yolov8n_seed20260514_lodo_train`

## Matrix

| Held-out domain | Status | Train images | Val images | Precision | Recall | mAP50 | mAP50-95 |
|---|---|---:|---:|---:|---:|---:|---:|
| China_Drone | ran | 960 | 80 | 0.0986 | 0.1382 | 0.0756 | 0.0265 |
| China_MotorBike | ran | 960 | 80 | 0.0987 | 0.1413 | 0.0792 | 0.0218 |
| Czech_Republic | ran | 960 | 80 | 0.1666 | 0.1030 | 0.0784 | 0.0268 |
| India | ran | 960 | 80 | 0.4538 | 0.0590 | 0.0619 | 0.0237 |
| Japan | ran | 960 | 80 | 0.0717 | 0.1569 | 0.0527 | 0.0202 |
| Norway | ran | 960 | 80 | 0.0416 | 0.0152 | 0.0104 | 0.0030 |
| United_States | ran | 960 | 80 | 0.1728 | 0.1636 | 0.1027 | 0.0375 |

## Smoke Signal

- Mean mAP50 across held-out domains: `0.0658`
- Mean mAP50-95 across held-out domains: `0.0228`
- Highest held-out mAP50: `United_States` = `0.1027`
- Lowest held-out mAP50: `Norway` = `0.0104`

## Boundary

- Treat these numbers as a reproducibility and go/no-go signal only.
- The run uses the subset sizes shown in the matrix; if those sizes are below the full dataset, label the result as subset-scale.
- A manuscript claim still requires fixed full-scale training, saved predictions, calibration/selective-prediction analysis, and failure taxonomy.
- Low absolute scores from short CPU runs do not invalidate the topic; cross-domain variation and pipeline viability are the useful signal at this gate.
