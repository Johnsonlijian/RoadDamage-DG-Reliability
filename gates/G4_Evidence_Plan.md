# G4 Evidence Plan

Date: 2026-05-13

Status: required before high-selectivity submission.

## Decision

R08 is retained as a useful audit demonstration, but it is not sufficient for EAAI-level submission. The next evidence layer must test whether the audit conclusions survive basic sources of variation: random split/training seed, detector capacity, confidence calibration, image-level review workload, and label-boundary interpretation.

## Minimum Evidence Layer

| Component | Minimum action | Pass criterion | If not passed |
| --- | --- | --- | --- |
| G4a repeated R08 | Repeat the frozen R08 subset with YOLOv8n for seeds 20260512, 20260513, and 20260514. Each seed has one ordinary run and seven LODO runs. | Domain/class/threshold patterns can be described with mean and spread, not one run. | Do not claim stable hard domains/classes. |
| G4b stronger detector bridge | Run at least one stronger detector matrix, preferably YOLOv8s or YOLOv8m. | The protocol yields interpretable diagnostics beyond YOLOv8n. | Do not claim model-agnostic protocol value; downgrade target or keep as pilot. |
| G4c calibration diagnostics | Report pooled, domain-wise, and high-confidence calibration gaps from prediction exports. | Confidence-threshold claims are backed by reliability bins. | Keep threshold results as exploratory only. |
| G4d image-level workload proxy | Report image review coverage, selected-image TP rate, and GT-positive image recall proxy at fixed thresholds. | Prediction-row coverage is not the only workload language. | Do not use engineering workload language. |
| G4e label-boundary sensitivity | Count false positives overlapping non-primary XML labels; optionally add merge-policy training later. | The 10,705 extra boxes are connected to error interpretation. | Treat label-boundary audit as descriptive only. |
| G4f artifact release candidate | Prepare public release contents and runbook excluding raw data and manuscript drafts. | Submission can cite a fixed tag/archive. | Do not submit as a reproducibility-protocol paper. |

## Run Scope

The minimum first pass preserves the frozen R08 subset scale:

- 160 training images per source domain.
- 80 validation images per target domain.
- Seven country/capture LODO domains.
- Ordinary mixed-domain reference.
- Explicit seeds.

This design does not turn the paper into a full detector benchmark. It only asks whether the audit protocol remains interpretable under minimal stability checks.

## Stronger Detector Bridge

Preferred bridge:

1. YOLOv8s at 640 px, at least one seed, ordinary plus seven LODO.
2. YOLOv8m at 640 px if GPU/CUDA setup is available and wall time is acceptable.

If the local environment remains CPU-only, the bridge is still required before submission but may be queued as the next computational job. The manuscript must not treat G4b as completed until result files exist.

## Submission Boundary

Even after G4, the manuscript may claim only a bounded audit protocol unless a later G5 layer adds larger/full-scale detector training, additional detector families, and operational validation. G4 can support a rational EAAI development route; it cannot support deployment readiness.
