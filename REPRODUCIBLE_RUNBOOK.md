# Reproducible Runbook

Status: R08 frozen subset, completed G4 release-candidate runbook, and v16 manuscript-facing derived-table/figure export.

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

## V16 Manuscript-Facing Derived Outputs

The following directories provide the public, non-sensitive traceability layer for the v16 manuscript text:

- `data_processed/paper_tables/`: derived CSV tables used for manuscript numbers, including domain inventories, ordinary-vs-LODO summaries, budget-sweep summaries, domain/class diagnostics, and threshold-frontier tables.
- `figures/paper_figures/`: generated PNG/SVG manuscript figures.

These files do not include raw RDD2022 images, raw archives, full prediction exports, active manuscript drafts, cover letters, reviewer-response drafts, or internal `rounds/` and `logs/` material.
