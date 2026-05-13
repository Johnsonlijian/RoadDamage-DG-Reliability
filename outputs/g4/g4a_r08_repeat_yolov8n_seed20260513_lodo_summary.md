# G2 Pretrained Smoke Matrix Summary

Generated: 2026-05-13 20:34, local time

Purpose: verify that the pretrained-detector leave-one-domain-out pipeline can run across all seven RDD2022 domains and expose early cross-domain signal. This is not a full paper-grade result.

## Configuration

- Subset root: `data_processed/g4/g4a_r08_repeat_yolov8n_seed20260513_lodo`
- Model: `yolov8n.pt`
- Epochs: `4`
- Image size: `320`
- Batch: `8`
- Device: `cuda`
- Workers: `0`
- YOLO project: `outputs/g4/g4a_r08_repeat_yolov8n_seed20260513_lodo_train`

## Matrix

| Held-out domain | Status | Train images | Val images | Precision | Recall | mAP50 | mAP50-95 |
|---|---|---:|---:|---:|---:|---:|---:|
| China_Drone | ran | 960 | 80 | 0.1075 | 0.1632 | 0.0827 | 0.0215 |
| China_MotorBike | ran | 960 | 80 | 0.1565 | 0.1099 | 0.0670 | 0.0131 |
| Czech_Republic | ran | 960 | 80 | 0.2411 | 0.1067 | 0.0878 | 0.0208 |
| India | ran | 960 | 80 | 0.4176 | 0.0998 | 0.0406 | 0.0140 |
| Japan | ran | 960 | 80 | 0.4555 | 0.1077 | 0.0699 | 0.0232 |
| Norway | ran | 960 | 80 | 0.0507 | 0.0148 | 0.0086 | 0.0030 |
| United_States | ran | 960 | 80 | 0.1650 | 0.1724 | 0.1177 | 0.0426 |

## Smoke Signal

- Mean mAP50 across held-out domains: `0.0677`
- Mean mAP50-95 across held-out domains: `0.0197`
- Highest held-out mAP50: `United_States` = `0.1177`
- Lowest held-out mAP50: `Norway` = `0.0086`

## Boundary

- Treat these numbers as a reproducibility and go/no-go signal only.
- The run uses the subset sizes shown in the matrix; if those sizes are below the full dataset, label the result as subset-scale.
- A manuscript claim still requires fixed full-scale training, saved predictions, calibration/selective-prediction analysis, and failure taxonomy.
- Low absolute scores from short CPU runs do not invalidate the topic; cross-domain variation and pipeline viability are the useful signal at this gate.
