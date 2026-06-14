# R43 K-Grid Dose Curves And K* Estimates

Grid cells available: 147 / 147 fine-tuned (+ 21 K=0 baselines).
Criterion (predeclared, scripts/72 default): mAP50 >= 0.20.
Protocol: fixed 80-image eval split per seed suite; nested K pools; YOLOv8s ft 4ep/640px from per-seed r14lc640 LODO checkpoints.

| domain | K=0 | K=5 | K=10 | K=20 | K=40 | K=80 | K=160 | K=320 | K* (3-seed mean) | K* (same-K all-seed clearance) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| China_Drone | 0.304 | 0.308 | 0.283 | 0.295 | 0.310 | 0.271 | 0.332 | 0.353 | 0 | 0 |
| China_MotorBike | 0.245 | 0.268 | 0.268 | 0.237 | 0.238 | 0.237 | 0.293 | 0.373 | 0 | 0 |
| Czech_Republic | 0.213 | 0.189 | 0.178 | 0.191 | 0.215 | 0.227 | 0.222 | 0.226 | 0 | 160 |
| India | 0.091 | 0.076 | 0.060 | 0.076 | 0.067 | 0.109 | 0.137 | 0.130 | > 320* | > 320* |
| Japan | 0.261 | 0.261 | 0.229 | 0.254 | 0.257 | 0.236 | 0.269 | 0.299 | 0 | 0 |
| Norway | 0.087 | 0.073 | 0.078 | 0.087 | 0.079 | 0.087 | 0.093 | 0.108 | > 320* | > 320* |
| United_States | 0.362 | 0.360 | 0.355 | 0.362 | 0.361 | 0.383 | 0.406 | 0.424 | 0 | 0 |

`> 320*` = censored: criterion not reached on the tested grid, or grid still incomplete for that domain.

Boundary: single detector family (YOLOv8s), random nested label selection, 3 seeds; K* values, including same-K all-seed clearance, are subset-scale audit estimates, not full-scale deployment guarantees.
