from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def run(command: list[str], root: Path) -> None:
    print("Running:", " ".join(command), flush=True)
    env = os.environ.copy()
    env.setdefault("YOLO_CONFIG_DIR", str(root / "UltralyticsConfig"))
    env.setdefault("MPLCONFIGDIR", str(root / ".mplconfig"))
    env.setdefault("YOLO_OFFLINE", "true")
    completed = subprocess.run(command, cwd=root, check=False, env=env)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def weights_from_results_csv(root: Path, results_csv: str) -> Path:
    results = root / results_csv
    weights = results.parent / "weights" / "best.pt"
    if not weights.exists():
        raise FileNotFoundError(f"Missing YOLO best weights: {weights}")
    return weights


def append_csv(source: Path, output: Path, add_fields: dict[str, str]) -> None:
    rows = read_csv(source)
    if not rows:
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(add_fields) + list(rows[0])
    exists = output.exists()
    with output.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        for row in rows:
            writer.writerow({**add_fields, **row})


def export_and_calibrate(
    root: Path,
    py: str,
    label: str,
    weights: Path,
    dataset_yaml: str,
    args: argparse.Namespace,
) -> Path:
    safe_label = label.replace(" ", "_")
    pred_csv = root / "data_processed" / "predictions" / f"{safe_label}_predictions.csv"
    pred_summary = root / "outputs" / f"{safe_label}_prediction_export_summary.md"
    cal_csv = root / "data_processed" / "calibration" / f"{safe_label}_calibration_bins.csv"
    risk_csv = root / "data_processed" / "calibration" / f"{safe_label}_risk_coverage.csv"
    cal_summary = root / "outputs" / f"{safe_label}_calibration_summary.md"

    export_cmd = [
        py,
        "scripts/17_export_yolo_predictions.py",
        "--weights",
        str(weights),
        "--data",
        dataset_yaml,
        "--split",
        "val",
        "--imgsz",
        str(args.imgsz),
        "--conf",
        str(args.conf),
        "--iou-threshold",
        str(args.iou_threshold),
        "--device",
        args.device,
        "--csv",
        str(pred_csv),
        "--summary",
        str(pred_summary),
    ]
    if args.max_images:
        export_cmd.extend(["--max-images", str(args.max_images)])
    run(export_cmd, root)

    run(
        [
            py,
            "scripts/18_calibration_from_predictions.py",
            "--predictions",
            str(pred_csv),
            "--bins",
            str(args.bins),
            "--calibration-csv",
            str(cal_csv),
            "--risk-csv",
            str(risk_csv),
            "--summary",
            str(cal_summary),
        ],
        root,
    )
    return pred_csv


def write_summary(root: Path, output: Path, prediction_files: list[tuple[str, Path]], label_prefix: str) -> None:
    lines = [
        "# G3 Prediction And Calibration Batch Summary",
        "",
        f"Boundary: generated from the `{label_prefix}` baseline. This is prediction-level method evidence, not final paper performance.",
        "",
        "| Label | Prediction table | Rows |",
        "| --- | --- | ---: |",
    ]
    for label, path in prediction_files:
        rows = read_csv(path)
        lines.append(f"| {label} | `{path.relative_to(root)}` | {len(rows)} |")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {output.relative_to(root)}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Export G3 timing-pilot predictions and calibration tables.")
    parser.add_argument("--ordinary-csv", default="data_processed/yolo_g3_timing_ordinary_result.csv")
    parser.add_argument("--lodo-csv", default="data_processed/yolo_g3_timing_lodo_results.csv")
    parser.add_argument("--label-prefix", default="g3_timing")
    parser.add_argument("--combined-lodo-predictions", default="data_processed/predictions/g3_timing_lodo_all_predictions.csv")
    parser.add_argument("--summary", default="outputs/g3_prediction_calibration_batch_summary.md")
    parser.add_argument("--imgsz", type=int, default=320)
    parser.add_argument("--conf", type=float, default=0.001)
    parser.add_argument("--iou-threshold", type=float, default=0.5)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--bins", type=int, default=10)
    parser.add_argument("--max-images", type=int, default=0)
    parser.add_argument("--skip-ordinary", action="store_true")
    args = parser.parse_args()

    root = project_root()
    py = sys.executable
    prediction_files: list[tuple[str, Path]] = []

    if not args.skip_ordinary:
        ordinary_rows = read_csv(root / args.ordinary_csv)
        if ordinary_rows:
            ordinary = ordinary_rows[0]
            weights = weights_from_results_csv(root, ordinary["results_csv"])
            pred_csv = export_and_calibrate(
                root,
                py,
                f"{args.label_prefix}_ordinary",
                weights,
                ordinary["data"],
                args,
            )
            prediction_files.append((f"{args.label_prefix}_ordinary", pred_csv))

    combined_lodo = root / args.combined_lodo_predictions
    if combined_lodo.exists():
        combined_lodo.unlink()
    for row in read_csv(root / args.lodo_csv):
        domain = row["heldout_domain"]
        label = f"{args.label_prefix}_lodo_{domain}"
        weights = weights_from_results_csv(root, row["results_csv"])
        pred_csv = export_and_calibrate(root, py, label, weights, row["subset_yaml"], args)
        prediction_files.append((label, pred_csv))
        append_csv(pred_csv, combined_lodo, {"heldout_domain": domain})

    run(
        [
            py,
            "scripts/18_calibration_from_predictions.py",
            "--predictions",
            str(combined_lodo),
            "--bins",
            str(args.bins),
            "--calibration-csv",
            f"data_processed/calibration/{args.label_prefix}_lodo_all_calibration_bins.csv",
            "--risk-csv",
            f"data_processed/calibration/{args.label_prefix}_lodo_all_risk_coverage.csv",
            "--summary",
            f"outputs/{args.label_prefix}_lodo_all_calibration_summary.md",
        ],
        root,
    )
    prediction_files.append((f"{args.label_prefix}_lodo_all", combined_lodo))
    write_summary(root, root / args.summary, prediction_files, args.label_prefix)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
