# Reproducible Runbook

Status: R08 frozen subset, completed G4 release-candidate runbook, manuscript-facing derived-table/figure export, Faster R-CNN detector-family validation, RetinaNet minimal architecture validation, RT-DETR-L transformer-family validation, previous technical-paper framework-figure export, R36 small target-domain evidence check, R37 post-local-evidence confidence-frontier audit, R41 FAIR-InfraAudit split/job/pilot-card infrastructure, and R59 AutCon fixed-evaluation acceptance-gate derived tables/figures.

## Expected Local Inputs

- Download RDD2022 from Figshare.
- Place raw archives under `data_raw/` locally.
- Do not commit raw archives or extracted images.

## Stages

1. Fetch or verify RDD2022 metadata.
2. Validate archive size and MD5.
3. Extract nested domain ZIPs.
4. Index images and parse XML annotations.
5. Build four-class YOLO subsets.
6. Run ordinary and leave-one-domain-out baselines.
7. Export prediction-level TP/FP/FN rows.
8. Compute calibration, risk-coverage, image-level coverage, label-boundary overlap, and error taxonomy tables.
9. Generate figures.
10. Run the G4 evidence layer and regenerate compact summaries.
11. Export non-sensitive manuscript-facing source tables and generated figures for submission traceability.
12. Run the bounded one-epoch Faster R-CNN detector-family probe on the same frozen ordinary and LODO subsets.
13. Run the R33 640-subset non-YOLO validation layer: eight-epoch Faster R-CNN and four-epoch RetinaNet.
14. Run the R34 RT-DETR-L transformer-family validation layer: eight-epoch ordinary and seven-domain LODO.
15. Export v19/v20/v21 calibration, domain-descriptor, six-boundary reporting-standard, and detector-family derived tables.
16. Export the v22 previous technical-paper framework figure and target-specific reproducibility references.
17. Run the R36 small target-domain evidence check and export the local-evidence sufficiency figure.
18. Run the R37 post-local-evidence prediction-export, calibration, and confidence-frontier audit.
19. Run the R41 FAIR-InfraAudit preparation chain: fairness/K* pilot summaries, full K-grid split registry, GPU job manifest, completion dashboard, and pilot readiness cards.
20. Rebuild the public-safe R59 acceptance-gate summary from included derived source tables.

## R08 Frozen Subset Commands

Run from the repository root after installing `requirements-experiment.txt` and placing RDD2022 raw inputs under local `data_raw/`:

```powershell
python scripts/19_run_g3_timing_pilot.py --model yolov8n.pt --train-per-domain 160 --val-per-domain 80 --epochs 4 --imgsz 320 --batch 8 --device cpu --workers 0 --copy-mode copy --overwrite --ordinary-root data_processed/yolo_g3_frozen_subset_ordinary --lodo-root data_processed/yolo_g3_frozen_subset_lodo --ordinary-project outputs/yolo_g3_frozen_subset_ordinary --lodo-project outputs/yolo_g3_frozen_subset_lodo --ordinary-csv data_processed/yolo_g3_frozen_subset_ordinary_result.csv --lodo-csv data_processed/yolo_g3_frozen_subset_lodo_results.csv --ordinary-summary outputs/g3_frozen_subset_ordinary_summary.md --lodo-summary outputs/g3_frozen_subset_lodo_summary.md --combined-summary outputs/g3_frozen_subset_baseline_summary.md --summary-title "G3 Frozen Subset Baseline Summary" --purpose-text "Purpose: provide a frozen, CPU-feasible ordinary-vs-LODO subset baseline with saved prediction outputs for manuscript evidence. These results are subset-scale evidence only." --boundary-text "This frozen subset baseline can support a bounded reliability-audit manuscript, but it does not replace full-scale GPU training for a detector-performance claim."

python scripts/20_run_g3_prediction_calibration.py --ordinary-csv data_processed/yolo_g3_frozen_subset_ordinary_result.csv --lodo-csv data_processed/yolo_g3_frozen_subset_lodo_results.csv --label-prefix g3_frozen_subset --combined-lodo-predictions data_processed/predictions/g3_frozen_subset_lodo_all_predictions.csv --summary outputs/g3_frozen_subset_prediction_calibration_batch_summary.md

python scripts/20_plot_g3_timing_outputs.py --ordinary data_processed/yolo_g3_frozen_subset_ordinary_result.csv --lodo data_processed/yolo_g3_frozen_subset_lodo_results.csv --ordinary-risk data_processed/calibration/g3_frozen_subset_ordinary_risk_coverage.csv --norway-risk data_processed/calibration/g3_frozen_subset_lodo_Norway_risk_coverage.csv --matrix-svg figures/fig06_g3_frozen_ordinary_vs_lodo.svg --risk-svg figures/fig07_g3_frozen_risk_tradeoff.svg --summary figures/fig06_fig07_g3_frozen_inputs.md --matrix-title "G3 frozen subset: ordinary vs held-out-domain transfer" --matrix-subtitle "YOLOv8n pretrained, 4 CPU epochs, 320 px. Frozen subset-scale evidence." --matrix-detail "Ordinary: 160 train and 80 validation images/domain. LODO: 160 train images/domain from six source domains, 80 validation images from the held-out domain." --matrix-source-note "Source: data_processed/yolo_g3_frozen_subset_ordinary_result.csv and data_processed/yolo_g3_frozen_subset_lodo_results.csv." --risk-title "G3 frozen subset: confidence threshold tradeoffs" --risk-subtitle "Prediction-level risk-coverage curves from exported TP/FP/FN tables." --risk-ordinary-label "Ordinary mixed-domain frozen subset" --risk-lodo-label "LODO held-out Norway frozen subset"

python scripts/21_plot_g3_reliability.py --ordinary-risk data_processed/calibration/g3_frozen_subset_ordinary_risk_coverage.csv --lodo-risk data_processed/calibration/g3_frozen_subset_lodo_all_risk_coverage.csv --svg figures/fig08_g3_frozen_pooled_risk_coverage.svg --summary figures/fig08_g3_frozen_pooled_risk_coverage_inputs.md --title "G3 frozen subset: pooled risk-coverage curves" --subtitle "Prediction-level precision versus retained prediction coverage under ordinary and pooled LODO settings." --ordinary-label "Ordinary frozen subset" --lodo-label "LODO frozen subset, pooled" --footer "Boundary: thresholds are analysis probes for reliability auditing; they are not operational deployment thresholds."

python scripts/22_summarize_prediction_errors.py --predictions data_processed/predictions/g3_frozen_subset_lodo_all_predictions.csv --domain-csv data_processed/g3_frozen_subset_lodo_error_by_domain.csv --domain-class-csv data_processed/g3_frozen_subset_lodo_error_by_domain_class.csv --class-csv data_processed/g3_frozen_subset_lodo_error_by_class.csv --summary outputs/g3_frozen_subset_error_taxonomy_summary.md --title "G3 Frozen Subset Error Taxonomy Summary" --boundary "frozen subset-scale prediction export. Use for manuscript failure analysis with an explicit subset-scale boundary; do not treat as full-scale detector performance."
```

## R08 Post-Processing Audit Commands

These commands operate on already exported R08 prediction tables. They are single-run post-processing diagnostics, not G4 multi-seed evidence.

```powershell
python scripts/23_image_level_coverage.py --predictions data_processed/predictions/g3_frozen_subset_lodo_all_predictions.csv --csv data_processed/calibration/g3_frozen_subset_lodo_all_image_level_coverage.csv --summary outputs/g3_frozen_subset_lodo_all_image_level_coverage_summary.md --title "R08 Pooled Domain-Holdout Image-Level Coverage Summary"

python scripts/23_image_level_coverage.py --predictions data_processed/predictions/g3_frozen_subset_ordinary_predictions.csv --csv data_processed/calibration/g3_frozen_subset_ordinary_image_level_coverage.csv --summary outputs/g3_frozen_subset_ordinary_image_level_coverage_summary.md --title "R08 Ordinary Image-Level Coverage Summary"

python scripts/25_calibration_diagnostics.py --predictions data_processed/predictions/g3_frozen_subset_lodo_all_predictions.csv --group-by domain --csv data_processed/calibration/g3_frozen_subset_lodo_all_calibration_diagnostics.csv --summary outputs/g3_frozen_subset_lodo_all_calibration_diagnostics_summary.md

python scripts/25_calibration_diagnostics.py --predictions data_processed/predictions/g3_frozen_subset_ordinary_predictions.csv --group-by domain --csv data_processed/calibration/g3_frozen_subset_ordinary_calibration_diagnostics.csv --summary outputs/g3_frozen_subset_ordinary_calibration_diagnostics_summary.md

python scripts/26_label_boundary_overlap.py --predictions data_processed/predictions/g3_frozen_subset_lodo_all_predictions.csv --boxes data_processed/rdd2022_boxes.csv --csv data_processed/calibration/g3_frozen_subset_lodo_all_label_boundary_overlap.csv --summary outputs/g3_frozen_subset_lodo_all_label_boundary_overlap_summary.md

python scripts/26_label_boundary_overlap.py --predictions data_processed/predictions/g3_frozen_subset_ordinary_predictions.csv --boxes data_processed/rdd2022_boxes.csv --csv data_processed/calibration/g3_frozen_subset_ordinary_label_boundary_overlap.csv --summary outputs/g3_frozen_subset_ordinary_label_boundary_overlap_summary.md
```

## G4 Completed Evidence Commands

G4a repeated YOLOv8n subset evidence:

```powershell
python scripts/24_run_g4_evidence_layer.py --suite g4a_r08_repeat --models yolov8n.pt --seeds 20260513 20260514 --train-per-domain 160 --val-per-domain 80 --epochs 4 --imgsz 320 --batch 8 --device cuda --workers 0 --copy-mode copy --overwrite --overwrite-runs --postprocess
```

G4b YOLOv8s detector-capacity bridge:

```powershell
python scripts/24_run_g4_evidence_layer.py --suite g4b_bridge --models yolov8s.pt --seeds 20260512 20260513 20260514 --train-per-domain 160 --val-per-domain 80 --epochs 8 --imgsz 640 --batch 8 --device cuda --workers 0 --copy-mode copy --overwrite --overwrite-runs --postprocess
```

G4 summary and figure regeneration:

```powershell
python scripts/27_summarize_g4a_multiseed.py
python scripts/29_summarize_g4b_bridge.py
python scripts/28_make_g4_figures.py
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/31_run_g4_label_boundary_batch.ps1
```

Prediction CSVs and detailed calibration/annotated overlap tables can be large and are ignored by default. The repository includes compact summaries and final metric/error tables.

## V17 Non-YOLO Detector-Family Check

The v17 manuscript includes a bounded non-YOLO check using torchvision Faster R-CNN MobileNetV3-320-FPN. It is a one-epoch family-diversity probe, not a tuned detector-performance baseline.

```powershell
python scripts/55_run_fasterrcnn_probe.py --settings ordinary heldout_China_Drone heldout_China_MotorBike heldout_Czech_Republic heldout_India heldout_Japan heldout_Norway heldout_United_States --epochs 1 --batch-size 2 --csv data_processed/non_yolo/fasterrcnn_all_lodo_results.csv --summary outputs/non_yolo/fasterrcnn_all_lodo_summary.md
```

The resulting compact table is `data_processed/non_yolo/fasterrcnn_all_lodo_results.csv`. The summary is `outputs/non_yolo/fasterrcnn_all_lodo_summary.md`.

## R33 Non-YOLO 640-Subset Validation Layer

The v20 evidence layer replaces the earlier one-epoch Faster R-CNN probe in the manuscript narrative with a completed eight-epoch Faster R-CNN MobileNetV3-320-FPN ordinary-plus-seven-LODO validation on the frozen 640-image/source-domain subsets. It also adds a four-epoch RetinaNet ResNet50-FPN minimal architecture check. These are detector-family reliability checks, not tuned detector leaderboards.

Faster R-CNN 8-epoch run:

```powershell
python scripts/59_run_r33_non_yolo_full.py --models fasterrcnn_mobilenet320 --settings ordinary heldout_China_Drone heldout_China_MotorBike heldout_Czech_Republic heldout_India heldout_Japan heldout_Norway heldout_United_States --epochs 8 --batch-size 2 --lr 0.0025 --csv data_processed/non_yolo/r33_fasterrcnn_8ep_640_lodo_results.csv --summary outputs/non_yolo/r33_fasterrcnn_8ep_640_lodo_summary.md --skip-existing
```

RetinaNet 4-epoch minimal architecture check:

```powershell
python scripts/59_run_r33_non_yolo_full.py --models retinanet_resnet50_fpn --settings ordinary heldout_China_Drone heldout_China_MotorBike heldout_Czech_Republic heldout_India heldout_Japan heldout_Norway heldout_United_States --epochs 4 --retinanet-epochs 4 --retinanet-batch-size 1 --retinanet-lr 0.001 --csv data_processed/non_yolo/r33_retinanet_4ep_640_lodo_results.csv --summary outputs/non_yolo/r33_retinanet_4ep_640_lodo_summary.md --skip-existing
```

R33 key derived outputs:

- `data_processed/non_yolo/r33_fasterrcnn_8ep_640_lodo_results.csv`
- `data_processed/non_yolo/r33_retinanet_4ep_640_lodo_results.csv`
- `data_processed/non_yolo/r33_non_yolo_640_combined_results.csv`
- `data_processed/non_yolo/r33_non_yolo_640_model_summary.csv`
- `data_processed/non_yolo/r33_non_yolo_640_domain_summary.csv`
- `outputs/non_yolo/r33_non_yolo_640_validation_summary.md`
- `figures/paper_figures/fig13_r33_non_yolo_full_validation.png`
- `figures/paper_figures/fig13_r33_non_yolo_full_validation.svg`

Boundary: the RetinaNet 1-epoch run is retained as `data_processed/non_yolo/r33_retinanet_1ep_640_lodo_results.csv` for transparency because it was too shallow to support the manuscript detector-family claim. The v20 manuscript uses the four-epoch RetinaNet check.

## R34 RT-DETR-L Transformer-Family Validation Layer

The v21 evidence layer adds RT-DETR-L on the same frozen 640-image/source-domain ordinary and seven-domain LODO subsets. This is a transformer-family reliability check, not a tuned detector leaderboard. The command below assumes `rtdetr-l.pt` is available locally or can be downloaded by the Ultralytics runtime.

RT-DETR-L 8-epoch run:

```powershell
python scripts/61_run_r34_rtdetr_lodo.py --settings ordinary heldout_China_Drone heldout_China_MotorBike heldout_Czech_Republic heldout_India heldout_Japan heldout_Norway heldout_United_States --epochs 8 --imgsz 640 --batch 2 --project outputs/r34/rtdetr_l_640_train --csv data_processed/non_yolo/r34_rtdetr_l_8ep_640_lodo_results.csv --summary outputs/non_yolo/r34_rtdetr_l_8ep_640_lodo_summary.md --skip-existing
```

R34 key derived outputs:

- `data_processed/non_yolo/r34_rtdetr_l_8ep_640_lodo_results.csv`
- `data_processed/non_yolo/r34_detector_family_640_combined_results.csv`
- `data_processed/non_yolo/r34_detector_family_640_model_summary.csv`
- `data_processed/non_yolo/r34_detector_family_640_domain_summary.csv`
- `outputs/non_yolo/r34_rtdetr_l_8ep_640_lodo_summary.md`
- `data_processed/paper_tables/v21_r34_rtdetr_l_8ep_640_lodo_results.csv`
- `data_processed/paper_tables/v21_r34_detector_family_640_combined_results.csv`
- `data_processed/paper_tables/v21_r34_detector_family_640_model_summary.csv`
- `data_processed/paper_tables/v21_r34_detector_family_640_domain_summary.csv`
- `figures/paper_figures/fig14_r34_rtdetr_detector_family_validation.png`
- `figures/paper_figures/fig14_r34_rtdetr_detector_family_validation.svg`

Boundary: RT-DETR-L is trained for eight epochs with a fixed seed on subset-scale data. It reduces detector-family specificity risk but does not establish tuned architecture superiority, full-scale leaderboard performance, or deployment readiness.

## V22 Previous Technical-Paper Figure Export

The v22 route generated a previous technical-paper framework figure. The public repository includes the generated framework figure but does not include any active manuscript, cover letter, reviewer-response material, or private submission-package build script.

Public v22 figure outputs:

- `figures/paper_figures/fig01_jcice_domain_aware_reliability_audit_framework.png`
- `figures/paper_figures/fig01_jcice_domain_aware_reliability_audit_framework.svg`

## R36 Small Target-Domain Evidence Check

The v23 evidence layer fine-tunes each source-only YOLOv8s 640-image/source-domain LODO checkpoint after adding a small number of labelled images from the held-out target domain. The added target-domain images are removed from the target evaluation split. This is a local-evidence sufficiency check, not a tuned domain-adaptation leaderboard.

Full seven-domain K=20 check:

```powershell
python scripts/64_run_r36_target_domain_finetune.py --target-ks 20 --epochs 4 --imgsz 640 --batch 8 --device 0 --workers 0 --seed 20260512 --skip-existing
```

Weak/informative-domain dose check:

```powershell
python scripts/64_run_r36_target_domain_finetune.py --domains India Norway China_MotorBike --target-ks 10 40 --epochs 4 --imgsz 640 --batch 8 --device 0 --workers 0 --seed 20260512 --skip-existing
```

R36 key derived outputs:

- `data_processed/r36_target_domain_evidence/r36_yolov8s_target_domain_evidence_results.csv`
- `outputs/r36/r36_target_domain_evidence_summary.md`
- `figures/paper_figures/fig15_r36_target_domain_evidence_check.png`
- `figures/paper_figures/fig15_r36_target_domain_evidence_check.svg`

Boundary: R36 uses single-seed local fine-tuning from existing source-only LODO checkpoints. It supports an evidence-boundary claim about local target labels, not deployment readiness, final calibration policy, or a domain-adaptation method ranking.

## R37 Post-Local-Evidence Confidence-Frontier Audit

The v24 evidence layer compares prediction exports from source-only YOLOv8s LODO checkpoints and the K=20 target-evidence checkpoints on the same R36 target-evaluation splits. It tests whether local-evidence mAP gains also change fixed-threshold precision and retained prediction coverage.

```powershell
python scripts/66_run_r37_target_evidence_frontier.py --imgsz 640 --conf 0.001 --iou-threshold 0.5 --device 0 --bins 10 --skip-existing
```

R37 key derived outputs:

- `data_processed/r37_target_evidence_frontier/r37_target_evidence_frontier_summary.csv`
- `outputs/r37/r37_target_evidence_frontier_summary.md`
- `figures/paper_figures/fig16_r37_target_evidence_confidence_frontier.png`
- `figures/paper_figures/fig16_r37_target_evidence_confidence_frontier.svg`

Boundary: R37 uses single-seed prediction exports and fixed threshold grids. It supports a confidence-frontier evidence-boundary claim, not an operational referral threshold or agency workload model.

## R41 FAIR-InfraAudit Preparation Chain

R41 reframes the project as a reliability, fairness, calibration, selective-risk, and local-data-demand audit framework. The public package contains the preparation chain and pilot summaries only. It does not contain final full-grid training results, final K* estimates, final uncertainty intervals, RDD2020 external-validation results, or submission-ready audit cards.

Generate pilot fairness and K* gap summaries from existing R36/R37 derived outputs:

```powershell
python scripts/71_fair_infraaudit_metrics.py
python scripts/72_estimate_kstar_from_results.py
python scripts/81_build_audit_cards.py
```

Freeze the public-safe image-ID split registry and training job manifest:

```powershell
python scripts/73_make_r41_kgrid_splits.py
python scripts/75_build_r41_training_manifest.py
python scripts/77_r41_completion_dashboard.py
```

Dry-run one local training job without materializing or training:

```powershell
python scripts/76_run_r41_yolo_job.py --domain India --K 20 --seed 20260609 --strategy random --model yolov8s.pt --epochs 1 --imgsz 320 --batch 4 --device cpu --dry-run
```

Local-only commands that materialize YOLO datasets or train models may create raw-image hardlinks/copies under ignored directories. Do not commit those generated directories:

- `data_processed/r41_yolo_kgrid/`
- `data_processed/r41_kgrid_results/`
- `outputs/r41/kgrid_train/`

R41 public-safe outputs:

- `splits/r41/rdd2022_fair_infraaudit_splits.json`
- `data_processed/r41_kgrid_splits/rdd2022_r41_domain_splits.csv`
- `data_processed/r41_kgrid_splits/rdd2022_r41_budget_plan.csv`
- `data_processed/r41_kgrid_splits/r41_training_job_manifest.csv`
- `data_processed/r41_fair_infraaudit/audit_cards_pilot.csv`
- `data_processed/r41_fair_infraaudit/r41_full_sprint_status.csv`
- `data_processed/r41_external_validation/rdd2020_provenance_check.csv`
- `outputs/r41/*.md`

R41 local-only outputs that must not be redistributed:

- `data_processed/r41_kgrid_splits/rdd2022_r41_image_registry.csv`
- `data_processed/r41_kgrid_splits/rdd2022_r41_budget_samples.csv`

Boundary: R41 currently proves that the full-evidence route is executable. It does not prove final fairness, final K*, deployment readiness, or external generality until the full K-grid, multi-seed uncertainty, prediction exports, and RDD2020 external validation are complete.

## R59 AutCon Acceptance-Gate Derived Layer

The R59 layer contains the public-safe derived tables and figure assets for the current Automation in Construction route. It centers a fixed-evaluation K* audit: each service domain is evaluated on an unchanged target split, and local-label demand is reported as finite, seed-sensitive, or censored under a predeclared mAP50 audit criterion.

Rebuild the public-safe summary:

```powershell
python scripts/84_r59_acceptance_gate_public.py
```

R59 key derived outputs:

- `data_processed/r59_acceptance_gate/source_tables/r43_kgrid_results.csv`
- `data_processed/r59_acceptance_gate/source_tables/r43_dose_curves.csv`
- `data_processed/r59_acceptance_gate/source_tables/r43_kstar_summary.md`
- `data_processed/r59_acceptance_gate/source_tables/r43_fairness_multiseed_domain_class.csv`
- `data_processed/r59_acceptance_gate/source_tables/r43_active_results.csv`
- `data_processed/r59_acceptance_gate/source_tables/r43_family8n_results.csv`
- `data_processed/r59_acceptance_gate/source_tables/r59_acceptance_decision_dashboard.csv`
- `data_processed/r59_acceptance_gate/source_tables/r59_error_burden_two_seed_summary.csv`
- `data_processed/r59_acceptance_gate/source_tables/r59_public_literature_additions.csv`
- `outputs/r59/r59_acceptance_gate_summary.md`
- `figures/autcon_r59/`

Boundary: the R59 source tables are derived, non-sensitive outputs. Raw RDD images, downloaded archives, trained weights, active manuscripts, cover letters, internal round reports, and local path registries are not redistributed. The error-burden table is a two-seed diagnostic and should not be cited as a three-seed pooled statistic.

## V19 Manuscript-Facing Derived Outputs

The following directories provide the public, non-sensitive traceability layer for the v19 manuscript text:

- `data_processed/paper_tables/`: derived CSV tables used for manuscript numbers, including domain inventories, ordinary-vs-LODO summaries, budget-sweep summaries, domain/class diagnostics, detector-family results for Faster R-CNN, RetinaNet, and RT-DETR-L, threshold-frontier tables, canonical calibration diagnostics, sampled domain image descriptors, domain-descriptor screening correlations, and the six-boundary reporting-standard table.
- `figures/paper_figures/`: generated PNG/SVG manuscript figures, including `fig12_calibration_descriptor_audit`.

Key v19 additions:

- `data_processed/paper_tables/v19_canonical_calibration_summary.csv`
- `data_processed/paper_tables/v19_domain_image_descriptors.csv`
- `data_processed/paper_tables/v19_domain_descriptor_table.csv`
- `data_processed/paper_tables/v19_domain_descriptor_correlations.csv`
- `data_processed/paper_tables/v19_six_boundary_reporting_standard.csv`
- `figures/paper_figures/fig12_calibration_descriptor_audit.png`
- `figures/paper_figures/fig12_calibration_descriptor_audit.svg`

These files do not include raw RDD2022 images, raw archives, full prediction exports, active manuscript drafts, cover letters, reviewer-response drafts, or internal `rounds/` and `logs/` material.
