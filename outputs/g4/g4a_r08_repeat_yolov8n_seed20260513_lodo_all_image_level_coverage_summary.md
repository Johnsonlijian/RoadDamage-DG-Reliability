# G4 Image-Level Coverage (g4a_r08_repeat_yolov8n_seed20260513_lodo_all)

Generated: 2026-05-13 20:36, local time

Source predictions: `data_processed\predictions\g4a_r08_repeat_yolov8n_seed20260513_lodo_all_predictions.csv`

This table converts prediction-row thresholding into an image-trigger proxy. It is closer to review workload than prediction-row coverage, but it is still not an agency work-order, road-segment, cost, or safety model.

| Threshold | Selected images | Image review coverage | Selected-image TP rate | Selected-image FP flag rate | GT-image recall proxy |
|---:|---:|---:|---:|---:|---:|
| 0.000 | 560 | 1.000000 | 0.757143 | 1.000000 | 0.757143 |
| 0.050 | 419 | 0.748214 | 0.372315 | 0.988067 | 0.278571 |
| 0.100 | 273 | 0.487500 | 0.315018 | 0.923077 | 0.153571 |
| 0.200 | 113 | 0.201786 | 0.292035 | 0.858407 | 0.058929 |
| 0.500 | 20 | 0.035714 | 0.300000 | 0.750000 | 0.010714 |

## Definitions

- Image review coverage: fraction of validation images with at least one accepted prediction at the threshold.
- Selected-image TP rate: among selected images, fraction with at least one accepted true-positive prediction.
- Selected-image FP flag rate: among selected images, fraction with at least one accepted false-positive prediction.
- GT-image recall proxy: fraction of ground-truth-positive images with at least one accepted true-positive prediction.

## Boundary

This is a post-processing workload proxy from existing prediction exports. It does not validate road-agency review cost, road-segment prioritization, or safety thresholds.
