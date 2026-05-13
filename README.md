# RoadDamage-DG Reliability Benchmark

Clean public reproducibility package for the RoadDamage-DG paper project.

Status: R12/G4 release-candidate package, 2026-05-13. This repository contains code, configs, small derived summaries, metric tables, and script-generated SVG figures for the subset-scale reliability-audit route. It is a local release candidate only until the author approves public push/release.

## Scope

This repository is intended to reproduce:

- RDD2022 source metadata checks;
- archive and nested-ZIP validation;
- domain and label-boundary inventories;
- domain-holdout subset construction;
- YOLO frozen subset baselines;
- prediction export, calibration, risk-coverage, image-level coverage, label-boundary overlap, and failure-taxonomy tables;
- the G4 evidence matrix and run manifest.

## Current Frozen Baseline

The included R08 baseline uses YOLOv8n pretrained weights with:

- 160 training images per training domain;
- 80 validation images per target domain;
- 4 CPU epochs;
- image size 320;
- batch size 8;
- seven domain-holdout runs plus an ordinary mixed-domain reference.

Key derived files:

- `outputs/g3_frozen_subset_baseline_summary.md`
- `data_processed/yolo_g3_frozen_subset_ordinary_result.csv`
- `data_processed/yolo_g3_frozen_subset_lodo_results.csv`
- `outputs/g3_frozen_subset_prediction_calibration_batch_summary.md`
- `outputs/g3_frozen_subset_error_taxonomy_summary.md`
- `outputs/g3_frozen_subset_lodo_all_image_level_coverage_summary.md`
- `outputs/g3_frozen_subset_lodo_all_calibration_diagnostics_summary.md`
- `outputs/g3_frozen_subset_lodo_all_label_boundary_overlap_summary.md`
- `configs/g4_evidence_matrix.yaml`
- `configs/g4_run_manifest.yaml`
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

Repository creation and push remain blocked until the user creates the GitHub repository or authorizes push from the local environment.
