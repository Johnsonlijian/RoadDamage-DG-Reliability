# G3 Frozen Subset Baseline Summary

Generated: 2026-05-12 16:15, local time

Purpose: provide a frozen, CPU-feasible ordinary-vs-LODO subset baseline with saved prediction outputs for manuscript evidence. These results are subset-scale evidence only.

## Configuration

- Train images per domain: `160`
- Validation images per domain: `80`
- Epochs: `4`
- Image size: `320`
- Batch: `8`
- Device: `cpu`
- Model: `yolov8n.pt`

## Ordinary Reference

| Split | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|
| Ordinary mixed-domain | 0.1664 | 0.1594 | 0.0745 | 0.0244 |

## LODO Matrix

| Held-out domain | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|
| China_Drone | 0.0913 | 0.0884 | 0.0699 | 0.0237 |
| China_MotorBike | 0.3710 | 0.1229 | 0.0657 | 0.0192 |
| Czech_Republic | 0.3832 | 0.1071 | 0.0542 | 0.0217 |
| India | 0.1085 | 0.0716 | 0.0601 | 0.0187 |
| Japan | 0.0870 | 0.1502 | 0.0797 | 0.0269 |
| Norway | 0.0358 | 0.0231 | 0.0120 | 0.0042 |
| United_States | 0.1291 | 0.1016 | 0.0680 | 0.0299 |

## Aggregate Signal

- Mean LODO mAP50: `0.0585`
- Mean LODO mAP50-95: `0.0206`
- Ordinary mAP50 minus mean LODO mAP50: `0.0160`

## Boundary

- This frozen subset baseline can support a bounded reliability-audit manuscript, but it does not replace full-scale GPU training for a detector-performance claim.
- It is not full-scale performance evidence unless the manuscript is explicitly framed as a subset-scale benchmark.
- Prediction export and calibration must be run on any baseline that is used in the manuscript.
