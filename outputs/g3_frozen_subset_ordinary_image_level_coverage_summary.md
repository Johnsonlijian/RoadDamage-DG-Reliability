# R08 Ordinary Image-Level Coverage Summary

Generated: 2026-05-13 17:38, local time

Source predictions: `data_processed\predictions\g3_frozen_subset_ordinary_predictions.csv`

This table converts prediction-row thresholding into an image-trigger proxy. It is closer to review workload than prediction-row coverage, but it is still not an agency work-order, road-segment, cost, or safety model.

| Threshold | Selected images | Image review coverage | Selected-image TP rate | Selected-image FP flag rate | GT-image recall proxy |
|---:|---:|---:|---:|---:|---:|
| 0.000 | 560 | 1.000000 | 0.855357 | 1.000000 | 0.855357 |
| 0.050 | 478 | 0.853571 | 0.562762 | 0.974895 | 0.480357 |
| 0.100 | 349 | 0.623214 | 0.521490 | 0.922636 | 0.325000 |
| 0.200 | 195 | 0.348214 | 0.569231 | 0.758974 | 0.198214 |
| 0.500 | 34 | 0.060714 | 0.676471 | 0.676471 | 0.041071 |

## Definitions

- Image review coverage: fraction of validation images with at least one accepted prediction at the threshold.
- Selected-image TP rate: among selected images, fraction with at least one accepted true-positive prediction.
- Selected-image FP flag rate: among selected images, fraction with at least one accepted false-positive prediction.
- GT-image recall proxy: fraction of ground-truth-positive images with at least one accepted true-positive prediction.

## Boundary

This is a post-processing workload proxy from existing prediction exports. It does not validate road-agency review cost, road-segment prioritization, or safety thresholds.
