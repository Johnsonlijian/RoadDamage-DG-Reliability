# R08 Pooled Domain-Holdout Image-Level Coverage Summary

Generated: 2026-05-13 17:38, local time

Source predictions: `data_processed\predictions\g3_frozen_subset_lodo_all_predictions.csv`

This table converts prediction-row thresholding into an image-trigger proxy. It is closer to review workload than prediction-row coverage, but it is still not an agency work-order, road-segment, cost, or safety model.

| Threshold | Selected images | Image review coverage | Selected-image TP rate | Selected-image FP flag rate | GT-image recall proxy |
|---:|---:|---:|---:|---:|---:|
| 0.000 | 560 | 1.000000 | 0.760714 | 1.000000 | 0.760714 |
| 0.050 | 457 | 0.816071 | 0.365427 | 0.969365 | 0.298214 |
| 0.100 | 315 | 0.562500 | 0.314286 | 0.939683 | 0.176786 |
| 0.200 | 172 | 0.307143 | 0.279070 | 0.877907 | 0.085714 |
| 0.500 | 82 | 0.146429 | 0.109756 | 0.963415 | 0.016071 |

## Definitions

- Image review coverage: fraction of validation images with at least one accepted prediction at the threshold.
- Selected-image TP rate: among selected images, fraction with at least one accepted true-positive prediction.
- Selected-image FP flag rate: among selected images, fraction with at least one accepted false-positive prediction.
- GT-image recall proxy: fraction of ground-truth-positive images with at least one accepted true-positive prediction.

## Boundary

This is a post-processing workload proxy from existing prediction exports. It does not validate road-agency review cost, road-segment prioritization, or safety thresholds.
