# G4 Compute Feasibility Memo

Date checked: 2026-05-13, Asia/Shanghai

Status update: superseded by `gates/G4_Execution_Report_2026-05-14.md` after the user authorized GPU computation. The earlier blocker described below was resolved by using CUDA-enabled PyTorch in `.venv-rdd` and acquiring `yolov8s.pt`.

## Local Environment

- GPU visible through `nvidia-smi`: NVIDIA GeForce RTX 3070, 8192 MiB, driver 560.94.
- Current RoadDamage-DG Python environment: `.venv-rdd`.
- PyTorch in `.venv-rdd` at the time of execution: `2.11.0+cu126`.
- `torch.cuda.is_available()` at the time of execution: `True`.
- Local YOLO weights used: `yolov8n.pt`, `yolov8s.pt`.

## Consequence

The original feasibility concern is closed. G4a and G4b were executed with GPU support after authorization. The active execution record is `gates/G4_Execution_Report_2026-05-14.md`.

## Remaining G4a Work

Closed. Seeds `20260513` and `20260514` completed, with prediction export and post-processing.

## Dry-Run Command

Status after R12 Iteration 4: passed on 2026-05-13. The dry run generated `outputs/g4/g4_evidence_layer_run_manifest.md` and confirmed the planned commands for seeds `20260513` and `20260514`. It did not start training and does not count as evidence.

```powershell
python scripts\24_run_g4_evidence_layer.py `
  --suite g4a_r08_repeat `
  --models yolov8n.pt `
  --seeds 20260513 20260514 `
  --train-per-domain 160 `
  --val-per-domain 80 `
  --epochs 4 `
  --imgsz 320 `
  --batch 8 `
  --device cpu `
  --workers 0 `
  --copy-mode hardlink `
  --postprocess `
  --dry-run
```

## Actual Run Command

Run only when the machine can be occupied for a long CPU job:

```powershell
python scripts\24_run_g4_evidence_layer.py `
  --suite g4a_r08_repeat `
  --models yolov8n.pt `
  --seeds 20260513 20260514 `
  --train-per-domain 160 `
  --val-per-domain 80 `
  --epochs 4 `
  --imgsz 320 `
  --batch 8 `
  --device cpu `
  --workers 0 `
  --copy-mode hardlink `
  --postprocess
```

## G4b Bridge Command Template

Use only after `yolov8s.pt` or `yolov8m.pt` exists and CUDA or acceptable CPU wall time has been confirmed:

```powershell
python scripts\24_run_g4_evidence_layer.py `
  --suite g4b_bridge `
  --models yolov8s.pt `
  --seeds 20260512 `
  --train-per-domain 160 `
  --val-per-domain 80 `
  --epochs 8 `
  --imgsz 640 `
  --batch 8 `
  --device cuda `
  --workers 0 `
  --copy-mode hardlink `
  --postprocess
```

## Submission Decision

After G4 completion, the manuscript may be upgraded to a bounded G4-evidence protocol paper. It still cannot claim deployment readiness, state-of-the-art detector performance, full-scale benchmark performance, or validated road-agency workload policy.
