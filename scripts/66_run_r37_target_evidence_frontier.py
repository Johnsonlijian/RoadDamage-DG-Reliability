from __future__ import annotations

import argparse
import csv
import os
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
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

THRESHOLDS = [0.0, 0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.2, 0.3, 0.5]


ROOT = Path(__file__).resolve().parents[1]
R36_RESULTS = ROOT / "data_processed" / "r36_target_domain_evidence" / "r36_yolov8s_targetk20_results.csv"
OUT_DIR = ROOT / "data_processed" / "r37_target_evidence_frontier"
PRED_DIR = OUT_DIR / "predictions"
CAL_DIR = OUT_DIR / "calibration"
FIG_DIR = ROOT / "figures" / "paper_figures"
RUN_STATE_DIR = ROOT / "outputs" / "r37" / "run_state"
SUMMARY_MD = ROOT / "outputs" / "r37" / "r37_target_evidence_frontier_summary.md"


@dataclass(frozen=True)
class RunSpec:
    domain: str
    variant: str
    weights: Path
    dataset_yaml: Path
    label: str


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def as_float(value: object, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def run_cmd(cmd: list[str], cwd: Path, skip_existing: bool, expected: Path) -> None:
    if skip_existing and expected.exists() and expected.stat().st_size > 0:
        print(f"[skip] {expected}")
        return
    env = os.environ.copy()
    env.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))
    print("[run]", " ".join(cmd))
    subprocess.run(cmd, cwd=str(cwd), env=env, check=True)


def specs_for_k20() -> list[RunSpec]:
    rows = [row for row in read_csv(R36_RESULTS) if row.get("target_k") == "20" and row.get("domain") in DOMAINS]
    specs: list[RunSpec] = []
    for row in rows:
        domain = row["domain"]
        dataset_yaml = ROOT / row["dataset_root"] / "dataset.yaml"
        source_weight = ROOT / row["source_weight"]
        results_csv = ROOT / row["results_csv"]
        ft_weight = results_csv.parent / "weights" / "best.pt"
        specs.append(
            RunSpec(
                domain=domain,
                variant="source_only",
                weights=source_weight,
                dataset_yaml=dataset_yaml,
                label=f"r37_{domain}_source_only_k20eval",
            )
        )
        specs.append(
            RunSpec(
                domain=domain,
                variant="target_evidence_k20",
                weights=ft_weight,
                dataset_yaml=dataset_yaml,
                label=f"r37_{domain}_target_evidence_k20",
            )
        )
    return specs


def export_and_calibrate(spec: RunSpec, args: argparse.Namespace) -> tuple[Path, Path, Path]:
    pred_csv = PRED_DIR / f"{spec.label}_predictions.csv"
    pred_summary = ROOT / "outputs" / "r37" / f"{spec.label}_prediction_export_summary.md"
    cal_csv = CAL_DIR / f"{spec.label}_calibration_bins.csv"
    risk_csv = CAL_DIR / f"{spec.label}_risk_coverage.csv"
    cal_summary = ROOT / "outputs" / "r37" / f"{spec.label}_calibration_summary.md"

    export_cmd = [
        sys.executable,
        "scripts/17_export_yolo_predictions.py",
        "--weights",
        str(spec.weights),
        "--data",
        str(spec.dataset_yaml),
        "--split",
        "val",
        "--imgsz",
        str(args.imgsz),
        "--conf",
        str(args.conf),
        "--iou-threshold",
        str(args.iou_threshold),
        "--device",
        str(args.device),
        "--csv",
        str(pred_csv),
        "--summary",
        str(pred_summary),
    ]
    run_cmd(export_cmd, ROOT, args.skip_existing, pred_csv)

    cal_cmd = [
        sys.executable,
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
    ]
    for threshold in THRESHOLDS:
        cal_cmd.extend(["--thresholds", str(threshold)])
    # argparse with nargs consumes only the last repeated group, so build a simpler command.
    cal_cmd = [
        sys.executable,
        "scripts/18_calibration_from_predictions.py",
        "--predictions",
        str(pred_csv),
        "--bins",
        str(args.bins),
        "--thresholds",
        *[str(threshold) for threshold in THRESHOLDS],
        "--calibration-csv",
        str(cal_csv),
        "--risk-csv",
        str(risk_csv),
        "--summary",
        str(cal_summary),
    ]
    run_cmd(cal_cmd, ROOT, args.skip_existing, risk_csv)
    return pred_csv, cal_csv, risk_csv


def pooled_prediction_rows(prediction_files: list[tuple[RunSpec, Path]]) -> dict[str, list[dict[str, str]]]:
    pooled: dict[str, list[dict[str, str]]] = defaultdict(list)
    fieldnames: list[str] | None = None
    for spec, path in prediction_files:
        rows = read_csv(path)
        if rows and fieldnames is None:
            fieldnames = list(rows[0].keys()) + ["r37_variant", "r37_heldout_domain"]
        for row in rows:
            row = dict(row)
            row["r37_variant"] = spec.variant
            row["r37_heldout_domain"] = spec.domain
            pooled[spec.variant].append(row)
    for variant, rows in pooled.items():
        out = PRED_DIR / f"r37_pooled_{variant}_k20eval_predictions.csv"
        write_csv(out, rows, fieldnames=fieldnames)
    return pooled


def calibrate_pooled(variant: str, args: argparse.Namespace) -> tuple[Path, Path]:
    pred_csv = PRED_DIR / f"r37_pooled_{variant}_k20eval_predictions.csv"
    cal_csv = CAL_DIR / f"r37_pooled_{variant}_k20eval_calibration_bins.csv"
    risk_csv = CAL_DIR / f"r37_pooled_{variant}_k20eval_risk_coverage.csv"
    summary = ROOT / "outputs" / "r37" / f"r37_pooled_{variant}_k20eval_calibration_summary.md"
    cmd = [
        sys.executable,
        "scripts/18_calibration_from_predictions.py",
        "--predictions",
        str(pred_csv),
        "--bins",
        str(args.bins),
        "--thresholds",
        *[str(threshold) for threshold in THRESHOLDS],
        "--calibration-csv",
        str(cal_csv),
        "--risk-csv",
        str(risk_csv),
        "--summary",
        str(summary),
    ]
    run_cmd(cmd, ROOT, args.skip_existing, risk_csv)
    return cal_csv, risk_csv


def prediction_counts(rows: list[dict[str, str]]) -> dict[str, float]:
    preds = [row for row in rows if row.get("outcome") in {"TP", "FP"}]
    gt = [row for row in rows if row.get("outcome") in {"TP", "FN"}]
    tp = sum(1 for row in rows if row.get("outcome") == "TP")
    fp = sum(1 for row in rows if row.get("outcome") == "FP")
    fn = sum(1 for row in rows if row.get("outcome") == "FN")
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    return {
        "prediction_rows": float(len(preds)),
        "gt_objects": float(len(gt)),
        "tp": float(tp),
        "fp": float(fp),
        "fn": float(fn),
        "stream_precision": precision,
        "stream_recall": recall,
    }


def ece_from_bins(path: Path) -> tuple[float, float, int]:
    rows = read_csv(path)
    ece = sum(as_float(row.get("ece_contribution")) for row in rows)
    high = [row for row in rows if as_float(row.get("conf_low")) >= 0.5]
    high_n = sum(int(as_float(row.get("n_predictions"))) for row in high)
    if high_n:
        weighted_gap = sum(
            int(as_float(row.get("n_predictions"))) * as_float(row.get("abs_calibration_gap")) for row in high
        ) / high_n
    else:
        weighted_gap = 0.0
    return ece, weighted_gap, high_n


def frontier_summary(path: Path) -> dict[str, float | str]:
    rows = read_csv(path)
    best = max(rows, key=lambda row: as_float(row.get("precision"))) if rows else {}
    floor_rows = [row for row in rows if as_float(row.get("precision")) >= 0.10]
    floor = min(floor_rows, key=lambda row: as_float(row.get("threshold"))) if floor_rows else {}
    return {
        "peak_precision": as_float(best.get("precision")) if best else 0.0,
        "threshold_at_peak_precision": best.get("threshold", "") if best else "",
        "coverage_at_peak_precision": as_float(best.get("prediction_coverage")) if best else 0.0,
        "reaches_0_10_precision_floor": "yes" if floor else "no",
        "min_threshold_for_0_10_precision": floor.get("threshold", "") if floor else "",
        "coverage_at_0_10_precision": as_float(floor.get("prediction_coverage")) if floor else 0.0,
        "precision_at_threshold_0_20": next(
            (as_float(row.get("precision")) for row in rows if abs(as_float(row.get("threshold")) - 0.2) < 1e-9),
            0.0,
        ),
        "coverage_at_threshold_0_20": next(
            (as_float(row.get("prediction_coverage")) for row in rows if abs(as_float(row.get("threshold")) - 0.2) < 1e-9),
            0.0,
        ),
    }


def summarize_outputs(
    prediction_files: list[tuple[RunSpec, Path]],
    cal_files: dict[tuple[str, str], Path],
    risk_files: dict[tuple[str, str], Path],
    pooled: dict[str, list[dict[str, str]]],
    pooled_cal: dict[str, Path],
    pooled_risk: dict[str, Path],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for spec, pred_file in prediction_files:
        metrics = prediction_counts(read_csv(pred_file))
        ece, high_gap, high_n = ece_from_bins(cal_files[(spec.domain, spec.variant)])
        frontier = frontier_summary(risk_files[(spec.domain, spec.variant)])
        rows.append(
            {
                "scope": "domain",
                "domain": spec.domain,
                "variant": spec.variant,
                **metrics,
                "ece_proxy": ece,
                "high_conf_gap": high_gap,
                "high_conf_predictions": high_n,
                **frontier,
            }
        )
    for variant, rows_in_variant in pooled.items():
        metrics = prediction_counts(rows_in_variant)
        ece, high_gap, high_n = ece_from_bins(pooled_cal[variant])
        frontier = frontier_summary(pooled_risk[variant])
        rows.append(
            {
                "scope": "pooled",
                "domain": "all_7_domains",
                "variant": variant,
                **metrics,
                "ece_proxy": ece,
                "high_conf_gap": high_gap,
                "high_conf_predictions": high_n,
                **frontier,
            }
        )
    return rows


def make_plot(summary_rows: list[dict[str, object]], pooled_risk: dict[str, Path]) -> tuple[Path, Path]:
    import matplotlib.pyplot as plt

    FIG_DIR.mkdir(parents=True, exist_ok=True)
    png_path = FIG_DIR / "fig16_r37_target_evidence_confidence_frontier.png"
    svg_path = FIG_DIR / "fig16_r37_target_evidence_confidence_frontier.svg"

    pooled_source = read_csv(pooled_risk["source_only"])
    pooled_target = read_csv(pooled_risk["target_evidence_k20"])
    pooled_rows = {row["variant"]: row for row in summary_rows if row["scope"] == "pooled"}

    fig, axes = plt.subplots(1, 2, figsize=(13.5, 5.2), dpi=220)
    ax = axes[0]
    for rows, label, color, marker in [
        (pooled_source, "Source-only on K=20 target-eval split", "#4C78A8", "o"),
        (pooled_target, "After K=20 target evidence", "#F58518", "s"),
    ]:
        coverage = [as_float(row["prediction_coverage"]) for row in rows]
        precision = [as_float(row["precision"]) for row in rows]
        ax.plot(coverage, precision, marker=marker, linewidth=2.2, color=color, label=label)
    ax.axhline(0.10, color="#8A8A8A", linestyle="--", linewidth=1.2)
    ax.text(0.02, 0.105, "0.10 precision floor", color="#5C5C5C", fontsize=9)
    ax.set_xlabel("Prediction-row coverage retained")
    ax.set_ylabel("Accepted-prediction precision")
    ax.set_title("A. Pooled confidence frontier")
    ax.grid(True, linestyle=":", linewidth=0.8, alpha=0.6)
    ax.legend(frameon=False, fontsize=8.5)

    ax = axes[1]
    categories = ["Source-only", "K=20 target evidence"]
    variants = ["source_only", "target_evidence_k20"]
    x = list(range(len(categories)))
    width = 0.36
    precision_at_020 = [float(pooled_rows[variant]["precision_at_threshold_0_20"]) for variant in variants]
    coverage_at_020 = [float(pooled_rows[variant]["coverage_at_threshold_0_20"]) for variant in variants]
    ax.bar([i - width / 2 for i in x], precision_at_020, width, label="Precision at threshold 0.20", color="#4C78A8")
    ax.bar([i + width / 2 for i in x], coverage_at_020, width, label="Prediction coverage at threshold 0.20", color="#F58518")
    ax.axhline(0.10, color="#8A8A8A", linestyle="--", linewidth=1.2)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=9)
    ax.set_ylabel("Pooled value")
    ax.set_title("B. Fixed-threshold screening tradeoff")
    ax.grid(True, axis="y", linestyle=":", linewidth=0.8, alpha=0.6)
    ax.legend(frameon=False, fontsize=8.5)

    fig.suptitle(
        "R37 target-domain evidence frontier: local labels improve recall but screening coverage remains narrow",
        fontsize=11.5,
        fontweight="bold",
    )
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(png_path, bbox_inches="tight")
    fig.savefig(svg_path, bbox_inches="tight")
    plt.close(fig)
    return png_path, svg_path


def fmt(value: object, digits: int = 4) -> str:
    if isinstance(value, str):
        return value
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def public_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def write_reports(summary_rows: list[dict[str, object]], figure_paths: tuple[Path, Path]) -> None:
    RUN_STATE_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_MD.parent.mkdir(parents=True, exist_ok=True)
    summary_csv = OUT_DIR / "r37_target_evidence_frontier_summary.csv"
    fieldnames = [
        "scope",
        "domain",
        "variant",
        "prediction_rows",
        "gt_objects",
        "tp",
        "fp",
        "fn",
        "stream_precision",
        "stream_recall",
        "ece_proxy",
        "high_conf_gap",
        "high_conf_predictions",
        "peak_precision",
        "threshold_at_peak_precision",
        "coverage_at_peak_precision",
        "reaches_0_10_precision_floor",
        "min_threshold_for_0_10_precision",
        "coverage_at_0_10_precision",
        "precision_at_threshold_0_20",
        "coverage_at_threshold_0_20",
    ]
    write_csv(summary_csv, summary_rows, fieldnames=fieldnames)

    pooled_source = next(row for row in summary_rows if row["scope"] == "pooled" and row["variant"] == "source_only")
    pooled_target = next(row for row in summary_rows if row["scope"] == "pooled" and row["variant"] == "target_evidence_k20")

    lines = [
        "# R37 Target-Evidence Confidence-Frontier Audit",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}, local time",
        "",
        "## Scope",
        "",
        "R37 recomputes prediction exports, calibration bins, and confidence frontiers on the R36 K=20 target-evaluation splits. Each held-out domain is evaluated twice on the same split: once with the original source-only YOLOv8s LODO checkpoint and once after fine-tuning that checkpoint with 20 labelled target-domain images. The 20 target images are not included in the evaluation split.",
        "",
        "## Pooled Results",
        "",
        "| Variant | Prediction rows | GT objects | Stream precision | Stream recall | ECE proxy | High-conf gap | Peak precision | Threshold at peak | Coverage at peak | Reaches 0.10 precision floor |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in [pooled_source, pooled_target]:
        lines.append(
            "| {variant} | {preds:.0f} | {gt:.0f} | {precision} | {recall} | {ece} | {gap} | {peak} | {thr} | {cov} | {floor} |".format(
                variant=row["variant"],
                preds=float(row["prediction_rows"]),
                gt=float(row["gt_objects"]),
                precision=fmt(row["stream_precision"]),
                recall=fmt(row["stream_recall"]),
                ece=fmt(row["ece_proxy"]),
                gap=fmt(row["high_conf_gap"]),
                peak=fmt(row["peak_precision"]),
                thr=row["threshold_at_peak_precision"],
                cov=fmt(row["coverage_at_peak_precision"]),
                floor=row["reaches_0_10_precision_floor"],
            )
        )
    lines.extend(
        [
            "",
            "## Domain-Level Peak Precision",
            "",
            "| Domain | Source-only peak precision | K=20 target-evidence peak precision | Source reaches 0.10 floor | Target-evidence reaches 0.10 floor |",
            "|---|---:|---:|---|---|",
        ]
    )
    for domain in DOMAINS:
        source = next(row for row in summary_rows if row["scope"] == "domain" and row["domain"] == domain and row["variant"] == "source_only")
        target = next(row for row in summary_rows if row["scope"] == "domain" and row["domain"] == domain and row["variant"] == "target_evidence_k20")
        lines.append(
            f"| {domain} | {fmt(source['peak_precision'])} | {fmt(target['peak_precision'])} | {source['reaches_0_10_precision_floor']} | {target['reaches_0_10_precision_floor']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "- R37 is a single-seed diagnostic pass designed to test whether the R36 local-evidence mAP gains also improve confidence-frontier interpretation.",
            "- Prediction-row precision is not AP and should not be reported as a deployment operating point.",
            "- If target evidence improves mAP but not the frontier, the manuscript should interpret local fine-tuning as necessary evidence collection rather than as a deployment solution.",
            "",
            "## Files",
            "",
            f"- Summary CSV: `{public_path(summary_csv)}`",
            f"- Figure PNG: `{public_path(figure_paths[0])}`",
            f"- Figure SVG: `{public_path(figure_paths[1])}`",
        ]
    )
    text = "\n".join(lines) + "\n"
    SUMMARY_MD.write_text(text, encoding="utf-8")
    (RUN_STATE_DIR / "R37_AUDIT_REPORT.md").write_text(text, encoding="utf-8")
    (RUN_STATE_DIR / "round_state.md").write_text(
        "\n".join(
            [
                "# R37 Round State",
                "",
                "- Status: completed",
                "- Increment: post-R36 prediction-export calibration and confidence-frontier audit.",
                f"- Summary: `{public_path(SUMMARY_MD)}`",
                f"- Figure: `{public_path(figure_paths[0])}`",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run R37 confidence-frontier audit after R36 target-domain evidence.")
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--conf", type=float, default=0.001)
    parser.add_argument("--iou-threshold", type=float, default=0.5)
    parser.add_argument("--device", default="0")
    parser.add_argument("--bins", type=int, default=10)
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()

    specs = specs_for_k20()
    prediction_files: list[tuple[RunSpec, Path]] = []
    cal_files: dict[tuple[str, str], Path] = {}
    risk_files: dict[tuple[str, str], Path] = {}
    for spec in specs:
        pred_csv, cal_csv, risk_csv = export_and_calibrate(spec, args)
        prediction_files.append((spec, pred_csv))
        cal_files[(spec.domain, spec.variant)] = cal_csv
        risk_files[(spec.domain, spec.variant)] = risk_csv

    pooled = pooled_prediction_rows(prediction_files)
    pooled_cal: dict[str, Path] = {}
    pooled_risk: dict[str, Path] = {}
    for variant in ["source_only", "target_evidence_k20"]:
        cal_csv, risk_csv = calibrate_pooled(variant, args)
        pooled_cal[variant] = cal_csv
        pooled_risk[variant] = risk_csv

    summary_rows = summarize_outputs(prediction_files, cal_files, risk_files, pooled, pooled_cal, pooled_risk)
    figure_paths = make_plot(summary_rows, pooled_risk)
    write_reports(summary_rows, figure_paths)
    print(f"Wrote {OUT_DIR / 'r37_target_evidence_frontier_summary.csv'}")
    print(f"Wrote {SUMMARY_MD}")
    print(f"Wrote {figure_paths[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
