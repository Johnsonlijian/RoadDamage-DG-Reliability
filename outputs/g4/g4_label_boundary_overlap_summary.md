# G4 Label-Boundary Overlap Summary

Boundary: this is post-processing of false-positive prediction rows against non-primary XML boxes. It does not merge labels, retrain a detector, or define an alternative benchmark task.

| model_label | split | iou_threshold | false_positive_predictions | fp_overlapping_non_primary_xml | share_of_fp | non_primary_label_counts | domain_counts |
| --- | --- | --- | --- | --- | --- | --- | --- |
| YOLOv8n seed20260512 | lodo_all | 0.1000 | 141032.0000 | 3319.0000 | 0.0235 | D44:1794; Repair:1243; D50:226; D43:29; D01:27 | Japan:1849; China_MotorBike:750; China_Drone:493; India:227 |
| YOLOv8n seed20260512 | lodo_all | 0.3000 | 141032.0000 | 996.0000 | 0.0071 | D44:539; Repair:373; D50:67; D01:13; D43:4 | Japan:557; China_MotorBike:225; China_Drone:148; India:66 |
| YOLOv8n seed20260512 | lodo_all | 0.5000 | 141032.0000 | 295.0000 | 0.0021 | D44:157; Repair:108; D50:25; D01:5 | Japan:163; China_MotorBike:72; China_Drone:36; India:24 |
| YOLOv8n seed20260512 | ordinary | 0.1000 | 151091.0000 | 2120.0000 | 0.0140 | D44:1252; Repair:518; D50:262; D01:61; D43:27 | Japan:1184; India:418; China_MotorBike:291; China_Drone:227 |
| YOLOv8n seed20260512 | ordinary | 0.3000 | 151091.0000 | 662.0000 | 0.0044 | D44:409; Repair:167; D50:64; D01:18; D43:4 | Japan:370; India:125; China_MotorBike:93; China_Drone:74 |
| YOLOv8n seed20260512 | ordinary | 0.5000 | 151091.0000 | 236.0000 | 0.0016 | D44:129; Repair:70; D50:28; D01:7; D43:2 | Japan:124; India:42; China_MotorBike:35; China_Drone:35 |
| YOLOv8n seed20260513 | lodo_all | 0.1000 | 144041.0000 | 3875.0000 | 0.0269 | D44:2285; Repair:1152; D43:343; D50:95 | Japan:2170; China_MotorBike:768; India:553; China_Drone:384 |
| YOLOv8n seed20260513 | lodo_all | 0.3000 | 144041.0000 | 1209.0000 | 0.0084 | D44:794; Repair:321; D43:63; D50:31 | Japan:696; China_MotorBike:211; India:192; China_Drone:110 |
| YOLOv8n seed20260513 | lodo_all | 0.5000 | 144041.0000 | 364.0000 | 0.0025 | D44:259; Repair:87; D50:11; D43:7 | Japan:202; India:75; China_MotorBike:54; China_Drone:33 |
| YOLOv8n seed20260513 | ordinary | 0.1000 | 153927.0000 | 2888.0000 | 0.0188 | D44:1713; Repair:683; D50:226; D43:146; D11:69; D01:51 | Japan:1925; China_MotorBike:552; India:280; China_Drone:131 |
| YOLOv8n seed20260513 | ordinary | 0.3000 | 153927.0000 | 863.0000 | 0.0056 | D44:496; Repair:245; D50:62; D01:22; D11:20; D43:18 | Japan:527; China_MotorBike:200; India:91; China_Drone:45 |
| YOLOv8n seed20260513 | ordinary | 0.5000 | 153927.0000 | 263.0000 | 0.0017 | D44:150; Repair:76; D50:28; D01:6; D11:2; D43:1 | Japan:159; China_MotorBike:60; India:28; China_Drone:16 |
| YOLOv8n seed20260514 | lodo_all | 0.1000 | 152905.0000 | 2865.0000 | 0.0187 | D44:1661; Repair:494; D50:260; D01:177; D43:173; D11:100 | Japan:1692; India:679; China_Drone:269; China_MotorBike:225 |
| YOLOv8n seed20260514 | lodo_all | 0.3000 | 152905.0000 | 874.0000 | 0.0057 | D44:510; Repair:166; D50:68; D01:54; D43:44; D11:32 | Japan:500; India:208; China_Drone:88; China_MotorBike:78 |
| YOLOv8n seed20260514 | lodo_all | 0.5000 | 152905.0000 | 270.0000 | 0.0018 | D44:162; Repair:55; D50:23; D01:20; D11:5; D43:5 | Japan:145; India:70; China_Drone:30; China_MotorBike:25 |
| YOLOv8n seed20260514 | ordinary | 0.1000 | 157396.0000 | 3372.0000 | 0.0214 | D44:1725; Repair:1157; D50:336; D43:102; D01:52 | Japan:1685; China_MotorBike:903; India:530; China_Drone:254 |
| YOLOv8n seed20260514 | ordinary | 0.3000 | 157396.0000 | 1029.0000 | 0.0065 | D44:562; Repair:342; D50:95; D43:16; D01:14 | Japan:513; China_MotorBike:252; India:174; China_Drone:90 |
| YOLOv8n seed20260514 | ordinary | 0.5000 | 157396.0000 | 302.0000 | 0.0019 | D44:165; Repair:96; D50:33; D43:5; D01:3 | Japan:149; China_MotorBike:61; India:57; China_Drone:35 |
| YOLOv8s seed20260512 | lodo_all | 0.1000 | 111282.0000 | 2116.0000 | 0.0190 | D44:1037; Repair:851; D50:192; D01:19; D43:17 | Japan:1104; China_MotorBike:428; China_Drone:423; India:161 |
| YOLOv8s seed20260512 | lodo_all | 0.3000 | 111282.0000 | 648.0000 | 0.0058 | D44:364; Repair:199; D50:71; D01:14 | Japan:398; China_Drone:114; China_MotorBike:85; India:51 |
| YOLOv8s seed20260512 | lodo_all | 0.5000 | 111282.0000 | 204.0000 | 0.0018 | D44:104; Repair:55; D50:34; D01:11 | Japan:125; China_Drone:33; India:24; China_MotorBike:22 |
| YOLOv8s seed20260512 | ordinary | 0.1000 | 118746.0000 | 1462.0000 | 0.0123 | D44:742; Repair:353; D50:312; D01:55 | Japan:705; India:404; China_MotorBike:177; China_Drone:176 |
| YOLOv8s seed20260512 | ordinary | 0.3000 | 118746.0000 | 492.0000 | 0.0041 | D44:233; D50:130; Repair:111; D01:18 | Japan:235; India:146; China_Drone:69; China_MotorBike:42 |
| YOLOv8s seed20260512 | ordinary | 0.5000 | 118746.0000 | 151.0000 | 0.0013 | D44:65; D50:47; Repair:34; D01:5 | Japan:74; India:43; China_Drone:19; China_MotorBike:15 |
| YOLOv8s seed20260513 | lodo_all | 0.1000 | 97077.0000 | 2043.0000 | 0.0210 | D44:1091; Repair:830; D43:110; D50:12 | Japan:1047; China_MotorBike:572; China_Drone:258; India:166 |
| YOLOv8s seed20260513 | lodo_all | 0.3000 | 97077.0000 | 644.0000 | 0.0066 | D44:391; Repair:224; D43:23; D50:6 | Japan:363; China_MotorBike:147; China_Drone:77; India:57 |
| YOLOv8s seed20260513 | lodo_all | 0.5000 | 97077.0000 | 196.0000 | 0.0020 | D44:137; Repair:54; D43:4; D50:1 | Japan:115; China_MotorBike:41; India:27; China_Drone:13 |
| YOLOv8s seed20260513 | ordinary | 0.1000 | 131643.0000 | 2032.0000 | 0.0154 | D44:1108; Repair:538; D50:219; D11:80; D01:50; D43:37 | Japan:1209; China_MotorBike:429; India:285; China_Drone:109 |
| YOLOv8s seed20260513 | ordinary | 0.3000 | 131643.0000 | 604.0000 | 0.0046 | D44:338; Repair:146; D50:73; D01:22; D11:22; D43:3 | Japan:366; China_MotorBike:110; India:92; China_Drone:36 |
| YOLOv8s seed20260513 | ordinary | 0.5000 | 131643.0000 | 175.0000 | 0.0013 | D44:93; Repair:41; D50:34; D01:6; D11:1 | Japan:107; China_MotorBike:35; India:27; China_Drone:6 |
| YOLOv8s seed20260514 | lodo_all | 0.1000 | 111841.0000 | 1715.0000 | 0.0153 | D44:831; Repair:342; D50:210; D01:129; D11:125; D43:78 | Japan:901; India:472; China_Drone:205; China_MotorBike:137 |
| YOLOv8s seed20260514 | lodo_all | 0.3000 | 111841.0000 | 536.0000 | 0.0048 | D44:268; Repair:100; D50:59; D01:55; D11:38; D43:16 | Japan:257; India:179; China_Drone:78; China_MotorBike:22 |
| YOLOv8s seed20260514 | lodo_all | 0.5000 | 111841.0000 | 181.0000 | 0.0016 | D44:96; Repair:27; D50:27; D01:20; D11:10; D43:1 | Japan:88; India:66; China_Drone:22; China_MotorBike:5 |
| YOLOv8s seed20260514 | ordinary | 0.1000 | 121288.0000 | 2227.0000 | 0.0184 | D44:1035; Repair:827; D50:250; D01:71; D43:44 | Japan:859; China_MotorBike:706; India:541; China_Drone:121 |
| YOLOv8s seed20260514 | ordinary | 0.3000 | 121288.0000 | 713.0000 | 0.0059 | D44:366; Repair:225; D50:97; D01:21; D43:4 | Japan:296; India:192; China_MotorBike:190; China_Drone:35 |
| YOLOv8s seed20260514 | ordinary | 0.5000 | 121288.0000 | 226.0000 | 0.0019 | D44:114; Repair:70; D50:37; D01:5 | Japan:100; India:56; China_MotorBike:56; China_Drone:14 |

## Compact Interpretation

At IoU 0.100, the highest non-primary-overlap share is 0.0269 for YOLOv8n seed20260513 / lodo_all; the lowest is 0.0123 for YOLOv8s seed20260512 / ordinary.
Across completed runs, non-primary XML labels explain a small but nonzero share of false positives; this supports label-boundary transparency rather than a claim that relabeling would solve the detector errors.

## Output File

- `data_processed/g4/g4_label_boundary_overlap_summary.csv`
