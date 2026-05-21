# R33 Non-YOLO Minimal LODO Validation Summary

This summary reports non-YOLO detector-family checks on the frozen 640-image/source-domain subsets.
Faster R-CNN is run for the requested 8 epochs. RetinaNet is a minimal LODO architecture check when selected.

| model | setting | train images | val images | epochs | mAP50 | precision | recall | gt | tp | fp | elapsed sec |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| retinanet_resnet50_fpn | ordinary | 4480 | 560 | 4 | 0.1660 | 0.0094 | 0.6913 | 1393 | 963 | 101457 | 945.2 |
| retinanet_resnet50_fpn | heldout_China_Drone | 3840 | 80 | 4 | 0.1902 | 0.0088 | 0.8538 | 130 | 111 | 12475 | 815.3 |
| retinanet_resnet50_fpn | heldout_China_MotorBike | 3840 | 80 | 4 | 0.2162 | 0.0134 | 0.7674 | 215 | 165 | 12103 | 807.8 |
| retinanet_resnet50_fpn | heldout_Czech_Republic | 3840 | 80 | 4 | 0.1003 | 0.0088 | 0.6850 | 127 | 87 | 9769 | 800.3 |
| retinanet_resnet50_fpn | heldout_India | 3840 | 80 | 4 | 0.0725 | 0.0081 | 0.5027 | 185 | 93 | 11435 | 797.5 |
| retinanet_resnet50_fpn | heldout_Japan | 3840 | 80 | 4 | 0.1590 | 0.0097 | 0.6624 | 157 | 104 | 10646 | 805.2 |
| retinanet_resnet50_fpn | heldout_Norway | 3840 | 80 | 4 | 0.0531 | 0.0115 | 0.3723 | 325 | 121 | 10384 | 635.8 |
| retinanet_resnet50_fpn | heldout_United_States | 3840 | 80 | 4 | 0.1397 | 0.0091 | 0.7647 | 187 | 143 | 15531 | 807.8 |

## Ordinary vs mean LODO

| model | ordinary mAP50 | mean LODO mAP50 | gap | n LODO | weakest LODO domain | weakest mAP50 |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| retinanet_resnet50_fpn | 0.1660 | 0.1330 | 0.0330 | 7 | Norway | 0.0531 |
