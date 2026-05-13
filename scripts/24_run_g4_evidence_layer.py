from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


DOMAINS = [
    "China_Drone",
    "China_MotorBike",
    "Czech_Republic",
    "India",
    "Japan",
    "Norway",
    "United_States",
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def safe_stem(model: str) -> str:
    stem = Path(model).stem
    return "".join(ch if ch.isalnum() or ch in {"_", "-"} else "_" for ch in stem)


def run(command: list[str], root: Path, dry_run: bool) -> None:
    print("Running:", " ".join(command), flush=True)
    if dry_run:
        return
    completed = subprocess.run(command, cwd=root, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def write_manifest(root: Path, rows: list[dict[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# G4 Evidence Layer Run Manifest",
        "",
        f"Generated: {generated}, local time",
        "",
        "This manifest records planned or executed G4 run commands. It is not a results table.",
        "",
        "| Label | Model | Seed | Ordinary CSV | LODO CSV | Prediction summary |",
        "| --- | --- | ---: | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {label} | `{model}` | {seed} | `{ordinary_csv}` | `{lodo_csv}` | `{prediction_summary}` |".format(
                **row
            )
        )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {output.relative_to(root)}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run or plan the RoadDamage-DG G4 evidence layer.")
    parser.add_argument("--suite", default="g4_minimum")
    parser.add_argument("--models", nargs="+", default=["yolov8n.pt"])
    parser.add_argument("--seeds", nargs="+", type=int, default=[20260512, 20260513, 20260514])
    parser.add_argument("--train-per-domain", type=int, default=160)
    parser.add_argument("--val-per-domain", type=int, default=80)
    parser.add_argument("--epochs", type=int, default=4)
    parser.add_argument("--imgsz", type=int, default=320)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--copy-mode", choices=["copy", "hardlink", "symlink"], default="hardlink")
    parser.add_argument("--conf", type=float, default=0.001)
    parser.add_argument("--iou-threshold", type=float, default=0.5)
    parser.add_argument("--bins", type=int, default=10)
    parser.add_argument("--domains", nargs="*", default=DOMAINS)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--overwrite-runs", action="store_true")
    parser.add_argument("--collect-only", action="store_true")
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--skip-train", action="store_true")
    parser.add_argument("--postprocess", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--manifest", default="outputs/g4/g4_evidence_layer_run_manifest.md")
    args = parser.parse_args()

    root = project_root()
    py = sys.executable
    manifest_rows: list[dict[str, str]] = []

    for model in args.models:
        model_label = safe_stem(model)
        for seed in args.seeds:
            label = f"{args.suite}_{model_label}_seed{seed}"
            ordinary_root = f"data_processed/g4/{label}_ordinary"
            lodo_root = f"data_processed/g4/{label}_lodo"
            ordinary_project = f"outputs/g4/{label}_ordinary_train"
            lodo_project = f"outputs/g4/{label}_lodo_train"
            ordinary_csv = f"data_processed/g4/{label}_ordinary_result.csv"
            lodo_csv = f"data_processed/g4/{label}_lodo_results.csv"
            ordinary_summary = f"outputs/g4/{label}_ordinary_summary.md"
            lodo_summary = f"outputs/g4/{label}_lodo_summary.md"
            prediction_summary = f"outputs/g4/{label}_prediction_calibration_batch_summary.md"

            if not args.skip_build:
                build_ordinary = [
                    py,
                    "scripts/15_make_yolo_ordinary_subset.py",
                    "--root",
                    "data_raw/RDD2022_extracted",
                    "--out",
                    ordinary_root,
                    "--max-train-per-domain",
                    str(args.train_per_domain),
                    "--max-val-per-domain",
                    str(args.val_per_domain),
                    "--seed",
                    str(seed),
                    "--copy-mode",
                    args.copy_mode,
                ]
                if args.overwrite:
                    build_ordinary.append("--overwrite")
                run(build_ordinary, root, args.dry_run)

                build_lodo = [
                    py,
                    "scripts/11_make_lodo_subset_matrix.py",
                    "--root",
                    "data_raw/RDD2022_extracted",
                    "--out-root",
                    lodo_root,
                    "--max-train-per-domain",
                    str(args.train_per_domain),
                    "--max-val",
                    str(args.val_per_domain),
                    "--seed",
                    str(seed),
                    "--copy-mode",
                    args.copy_mode,
                    "--domains",
                    *args.domains,
                ]
                if args.overwrite:
                    build_lodo.append("--overwrite")
                run(build_lodo, root, args.dry_run)

            if not args.skip_train:
                ordinary_train = [
                    py,
                    "scripts/16_run_yolo_once.py",
                    "--data",
                    str(Path(ordinary_root) / "dataset.yaml"),
                    "--model",
                    model,
                    "--project",
                    ordinary_project,
                    "--name",
                    f"ordinary_{model_label}_seed{seed}_{args.epochs}ep_{args.imgsz}px",
                    "--epochs",
                    str(args.epochs),
                    "--imgsz",
                    str(args.imgsz),
                    "--batch",
                    str(args.batch),
                    "--workers",
                    str(args.workers),
                    "--device",
                    args.device,
                    "--csv",
                    ordinary_csv,
                    "--summary",
                    ordinary_summary,
                    "--title",
                    f"G4 Ordinary Summary ({model_label}, seed {seed})",
                    "--boundary",
                    "G4 bounded subset evidence; not deployment or SOTA detector-performance evidence.",
                ]
                if args.collect_only:
                    ordinary_train.append("--collect-only")
                if args.overwrite_runs:
                    ordinary_train.append("--overwrite-run")
                run(ordinary_train, root, args.dry_run)

                lodo_train = [
                    py,
                    "scripts/13_run_g2_pretrained_smoke_matrix.py",
                    "--subset-root",
                    lodo_root,
                    "--model",
                    model,
                    "--project",
                    lodo_project,
                    "--run-suffix",
                    f"{model_label}_seed{seed}_{args.epochs}ep_{args.imgsz}px",
                    "--epochs",
                    str(args.epochs),
                    "--imgsz",
                    str(args.imgsz),
                    "--batch",
                    str(args.batch),
                    "--workers",
                    str(args.workers),
                    "--device",
                    args.device,
                    "--csv",
                    lodo_csv,
                    "--summary",
                    lodo_summary,
                    "--domains",
                    *args.domains,
                ]
                if args.collect_only:
                    lodo_train.append("--collect-only")
                if args.overwrite_runs:
                    lodo_train.append("--overwrite-runs")
                run(lodo_train, root, args.dry_run)

            if args.postprocess:
                run(
                    [
                        py,
                        "scripts/20_run_g3_prediction_calibration.py",
                        "--ordinary-csv",
                        ordinary_csv,
                        "--lodo-csv",
                        lodo_csv,
                        "--label-prefix",
                        label,
                        "--combined-lodo-predictions",
                        f"data_processed/predictions/{label}_lodo_all_predictions.csv",
                        "--summary",
                        prediction_summary,
                        "--imgsz",
                        str(args.imgsz),
                        "--conf",
                        str(args.conf),
                        "--iou-threshold",
                        str(args.iou_threshold),
                        "--device",
                        args.device,
                        "--bins",
                        str(args.bins),
                    ],
                    root,
                    args.dry_run,
                )
                for split_label, pred_path in [
                    (f"{label}_ordinary", f"data_processed/predictions/{label}_ordinary_predictions.csv"),
                    (f"{label}_lodo_all", f"data_processed/predictions/{label}_lodo_all_predictions.csv"),
                ]:
                    run(
                        [
                            py,
                            "scripts/23_image_level_coverage.py",
                            "--predictions",
                            pred_path,
                            "--csv",
                            f"data_processed/calibration/{split_label}_image_level_coverage.csv",
                            "--summary",
                            f"outputs/g4/{split_label}_image_level_coverage_summary.md",
                            "--title",
                            f"G4 Image-Level Coverage ({split_label})",
                        ],
                        root,
                        args.dry_run,
                    )

            manifest_rows.append(
                {
                    "label": label,
                    "model": model,
                    "seed": str(seed),
                    "ordinary_csv": ordinary_csv,
                    "lodo_csv": lodo_csv,
                    "prediction_summary": prediction_summary if args.postprocess else "[not requested]",
                }
            )

    write_manifest(root, manifest_rows, root / args.manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
