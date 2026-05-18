# Faster R-CNN Non-YOLO Probe Summary

This is a bounded detector-family probe using torchvision Faster R-CNN MobileNetV3-320-FPN on existing frozen YOLO-format subsets.
It is intended to test whether a non-YOLO pipeline can be audited with the same ordinary/LODO boundary logic; it is not a tuned detector-performance claim.

| setting | train images | val images | epochs | mAP50 | precision | recall | gt | tp | fp | elapsed sec |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| ordinary | 1120 | 560 | 1 | 0.0530 | 0.1127 | 0.1657 | 1406 | 233 | 1834 | 62.5 |
| heldout_China_Drone | 960 | 80 | 1 | 0.0455 | 0.0711 | 0.2462 | 130 | 32 | 418 | 40.8 |
| heldout_China_MotorBike | 960 | 80 | 1 | 0.0340 | 0.0688 | 0.1628 | 215 | 35 | 474 | 40.4 |
| heldout_Czech_Republic | 960 | 80 | 1 | 0.0035 | 0.0053 | 0.0079 | 127 | 1 | 186 | 41.4 |
| heldout_India | 960 | 80 | 1 | 0.0131 | 0.0471 | 0.0432 | 185 | 8 | 162 | 42.2 |
| heldout_Japan | 960 | 80 | 1 | 0.0409 | 0.0641 | 0.2038 | 157 | 32 | 467 | 41.3 |
| heldout_Norway | 960 | 80 | 1 | 0.0260 | 0.0823 | 0.0800 | 325 | 26 | 290 | 33.0 |
| heldout_United_States | 960 | 80 | 1 | 0.0163 | 0.0558 | 0.1658 | 187 | 31 | 525 | 41.4 |
