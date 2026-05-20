# RoadDamage-DG Reliability Package

Clean public reproducibility package for the RoadDamage-DG paper project:

**Domain-Aware Reliability Boundaries for Infrastructure Image-Based Road-Damage Detection**

Status: v19 public release candidate, 2026-05-20. This repository contains code, configs, compact derived summaries, manuscript-facing derived tables, script-generated figures, a bounded Faster R-CNN detector-family check, and v19 calibration/domain-descriptor audit outputs for the reliability-audit route. Raw RDD2022 archives, extracted images, active manuscript drafts, cover letters, reviewer-response drafts, internal rounds, and logs are not redistributed here.

## Scope

This repository is intended to reproduce:

- RDD2022 source metadata checks;
- archive and nested-ZIP validation;
- domain and label-boundary inventories;
- domain-holdout subset construction;
- YOLO frozen subset baselines;
- a one-epoch torchvision Faster R-CNN MobileNetV3-320-FPN ordinary-plus-seven-LODO detector-family check;
- prediction export, calibration, risk-coverage, image-level coverage, label-boundary overlap, and failure-taxonomy tables;
- the completed G4 evidence matrix, run manifest, summaries, and figures;
- the v19 manuscript-facing derived tables and generated figures.

## Current G4 Evidence Layer

The included G4 evidence layer is bounded subset evidence. It does not reproduce raw RDD2022 data, downloaded archives, extracted images, or full prediction exports. It contains compact derived summaries for:

- G4a: repeated YOLOv8n 320 px / 4 epoch subset evidence across seeds 20260512, 20260513, and 20260514;
- G4b: YOLOv8s 640 px / 8 epoch detector-capacity bridge across the same three seeds;
- calibration diagnostics, image-level workload proxies, and label-boundary false-positive overlap summaries for manuscript-used ordinary and pooled LODO exports.

The original R08 baseline uses YOLOv8n pretrained weights with:

- 160 training images per training domain;
- 80 validation images per target domain;
- 4 CPU epochs;
- image size 320;
- batch size 8;
- seven domain-holdout runs plus an ordinary mixed-domain reference.

Key G4 derived files:

- `outputs/g4/g4a_multiseed_summary.md`
- `outputs/g4/g4b_bridge_summary.md`
- `outputs/g4/g4_label_boundary_overlap_summary.md`
- `data_processed/g4/g4a_multiseed_runs.csv`
- `data_processed/g4/g4a_multiseed_ordinary_summary.csv`
- `data_processed/g4/g4a_multiseed_lodo_overall_summary.csv`
- `data_processed/g4/g4a_multiseed_lodo_by_domain_summary.csv`
- `data_processed/g4/g4b_bridge_setting_summary.csv`
- `data_processed/g4/g4b_bridge_domain_summary.csv`
- `data_processed/g4/g4b_bridge_calibration_summary.csv`
- `data_processed/g4/g4b_bridge_image_level_thresholds.csv`
- `data_processed/g4/g4_label_boundary_overlap_summary.csv`
- `figures/fig09_g4a_multiseed_lodo_map50.svg`
- `figures/fig10_g4a_image_level_thresholds.svg`
- `figures/fig11_g4b_yolov8n_vs_yolov8s_bridge.svg`
- `configs/g4_run_manifest.yaml`
- `gates/G4_Execution_Report_2026-05-14.md`

## Manuscript-Facing Derived Outputs

The `data_processed/paper_tables/` directory contains non-sensitive derived CSV tables used to audit the v19 manuscript numbers. These files are copied from the submission package's source-table export and include domain diagnostics, ordinary-vs-LODO summaries, budget-sweep summaries, per-class/domain error audits, non-YOLO Faster R-CNN results, threshold-frontier tables, calibration diagnostics, deterministic domain image descriptors, domain-descriptor screening correlations, and the six-boundary reporting-standard table.

The `figures/paper_figures/` directory contains generated PNG/SVG versions of the v19 manuscript figures. These are figure outputs only; no raw images from RDD2022 are redistributed.

Key non-YOLO detector-family check files:

- `scripts/55_run_fasterrcnn_probe.py`
- `data_processed/non_yolo/fasterrcnn_all_lodo_results.csv`
- `outputs/non_yolo/fasterrcnn_all_lodo_summary.md`
- `figures/paper_figures/fig11_fasterrcnn_non_yolo_probe.png`
- `figures/paper_figures/fig11_fasterrcnn_non_yolo_probe.svg`

Key v19 reliability-guidance additions:

- `data_processed/paper_tables/v19_canonical_calibration_summary.csv`
- `data_processed/paper_tables/v19_domain_image_descriptors.csv`
- `data_processed/paper_tables/v19_domain_descriptor_table.csv`
- `data_processed/paper_tables/v19_domain_descriptor_correlations.csv`
- `data_processed/paper_tables/v19_six_boundary_reporting_standard.csv`
- `figures/paper_figures/fig12_calibration_descriptor_audit.png`
- `figures/paper_figures/fig12_calibration_descriptor_audit.svg`

Key R08 derived files retained for traceability:

- `outputs/g3_frozen_subset_baseline_summary.md`
- `data_processed/yolo_g3_frozen_subset_ordinary_result.csv`
- `data_processed/yolo_g3_frozen_subset_lodo_results.csv`
- `outputs/g3_frozen_subset_prediction_calibration_batch_summary.md`
- `outputs/g3_frozen_subset_error_taxonomy_summary.md`
- `outputs/g3_frozen_subset_lodo_all_image_level_coverage_summary.md`
- `outputs/g3_frozen_subset_lodo_all_calibration_diagnostics_summary.md`
- `outputs/g3_frozen_subset_lodo_all_label_boundary_overlap_summary.md`
- `configs/g4_evidence_matrix.yaml`
- `gates/G4_Evidence_Plan.md`
- `gates/G4_Compute_Feasibility_Memo.md`
- `figures/fig06_g3_frozen_ordinary_vs_lodo.svg`
- `figures/fig07_g3_frozen_risk_tradeoff.svg`
- `figures/fig08_g3_frozen_pooled_risk_coverage.svg`

The former internal protocol schematic `figures/fig01_roaddamagedg_audit_protocol.svg` has been removed from the public release candidate because it is not a submission-facing scientific result figure.

## Exclusions

This repository must not contain:

- raw RDD2022 archives or extracted images;
- active manuscript drafts;
- internal `rounds/` or `logs/`;
- reviewer-response or cover-letter drafts;
- credentials or local virtual environments.

## Intended Remote

`https://github.com/Johnsonlijian/RoadDamage-DG-Reliability`
