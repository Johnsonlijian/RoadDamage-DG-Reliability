# R33 Non-YOLO 640-Subset Validation Summary

Date: 2026-05-21

This public summary reports derived, non-sensitive detector-family validation
results on the frozen 640-image/source-domain ordinary and seven-domain LODO
subsets. Raw RDD2022 archives, extracted images, and model checkpoints are not
redistributed.

## Model-Level Results

| model | epochs | ordinary mAP50 | mean LODO mAP50 | gap | weakest LODO domain | weakest mAP50 |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| YOLOv8s 640 budget | 8 | 0.3325 | 0.2233 | 0.1093 | Norway | 0.0867 |
| Faster R-CNN MobileNetV3-320-FPN | 8 | 0.1983 | 0.0862 | 0.1121 | United_States | 0.0306 |
| RetinaNet ResNet50-FPN | 4 | 0.1660 | 0.1330 | 0.0330 | Norway | 0.0531 |

## Boundary

The Faster R-CNN check is a completed eight-epoch two-stage detector-family
validation. The RetinaNet check is a four-epoch dense one-stage minimal
architecture validation. Neither result is a tuned detector leaderboard or
deployment claim; both are used to test whether the ordinary-vs-LODO reliability
boundary remains visible outside the YOLOv8 training path.

