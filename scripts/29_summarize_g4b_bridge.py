from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


SEEDS = [20260512, 20260513, 20260514]
Y8N_PREFIXES = {
    20260512: "g3_frozen_subset",
    20260513: "g4a_r08_repeat_yolov8n_seed20260513",
    20260514: "g4a_r08_repeat_yolov8n_seed20260514",
}
Y8S_PREFIX = "g4b_bridge_yolov8s_seed{seed}"


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def fmt(value: object, digits: int = 4) -> str:
    try:
        val = float(value)
    except (TypeError, ValueError):
        return str(value)
    if pd.isna(val):
        return "NA"
    return f"{val:.{digits}f}"


def markdown_table(df: pd.DataFrame, columns: list[str], digits: int = 4) -> list[str]:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in df[columns].iterrows():
        lines.append("| " + " | ".join(fmt(row[col], digits) for col in columns) + " |")
    return lines


def y8n_paths(root: Path, seed: int) -> tuple[Path, Path]:
    if seed == 20260512:
        return (
            root / "data_processed" / "yolo_g3_frozen_subset_ordinary_result.csv",
            root / "data_processed" / "yolo_g3_frozen_subset_lodo_results.csv",
        )
    prefix = Y8N_PREFIXES[seed]
    return (
        root / "data_processed" / "g4" / f"{prefix}_ordinary_result.csv",
        root / "data_processed" / "g4" / f"{prefix}_lodo_results.csv",
    )


def y8s_paths(root: Path, seed: int) -> tuple[Path, Path]:
    prefix = Y8S_PREFIX.format(seed=seed)
    return (
        root / "data_processed" / "g4" / f"{prefix}_ordinary_result.csv",
        root / "data_processed" / "g4" / f"{prefix}_lodo_results.csv",
    )


def calibration_row(root: Path, seed: int, model_label: str, prefix: str, split: str) -> dict[str, object] | None:
    path = root / "data_processed" / "calibration" / f"{prefix}_{split}_calibration_bins.csv"
    if not path.exists():
        return None
    df = read_csv(path)
    n = pd.to_numeric(df["n_predictions"], errors="coerce").fillna(0)
    total = float(n.sum())
    ece = float(pd.to_numeric(df["ece_contribution"], errors="coerce").fillna(0).sum())
    high = df[pd.to_numeric(df["conf_low"], errors="coerce") >= 0.1].copy()
    high_n = pd.to_numeric(high["n_predictions"], errors="coerce").fillna(0)
    high_total = float(high_n.sum())
    if high_total:
        high_mean_conf = float(
            (pd.to_numeric(high["mean_confidence"], errors="coerce").fillna(0) * high_n).sum()
            / high_total
        )
        high_tp = float((pd.to_numeric(high["empirical_precision"], errors="coerce").fillna(0) * high_n).sum())
        high_precision = high_tp / high_total
        high_gap = abs(high_mean_conf - high_precision)
    else:
        high_mean_conf = float("nan")
        high_precision = float("nan")
        high_gap = float("nan")
    return {
        "seed": seed,
        "model_label": model_label,
        "split": split,
        "calibration_csv": str(path.relative_to(root)),
        "n_predictions": int(total),
        "ece_proxy": ece,
        "high_conf_n_predictions": int(high_total),
        "high_conf_mean_confidence": high_mean_conf,
        "high_conf_empirical_precision": high_precision,
        "high_conf_gap": high_gap,
    }


def image_threshold_rows(
    root: Path,
    seed: int,
    model_label: str,
    prefix: str,
    split: str,
    thresholds: set[float],
) -> list[dict[str, object]]:
    path = root / "data_processed" / "calibration" / f"{prefix}_{split}_image_level_coverage.csv"
    if not path.exists():
        return []
    df = read_csv(path)
    df["threshold_key"] = pd.to_numeric(df["threshold"], errors="coerce").round(6)
    out: list[dict[str, object]] = []
    for threshold in sorted(thresholds):
        matches = df[df["threshold_key"] == round(threshold, 6)]
        if matches.empty:
            continue
        row = matches.iloc[0].to_dict()
        row.update(
            {
                "seed": seed,
                "model_label": model_label,
                "split": split,
                "source_csv": str(path.relative_to(root)),
            }
        )
        row.pop("threshold_key", None)
        out.append(row)
    return out


def collect_metric_rows(root: Path) -> tuple[pd.DataFrame, pd.DataFrame, list[int], list[str]]:
    setting_rows: list[dict[str, object]] = []
    domain_rows: list[dict[str, object]] = []
    completed_seeds: list[int] = []
    missing: list[str] = []

    for seed in SEEDS:
        specs = [
            ("YOLOv8n 320px 4ep", *y8n_paths(root, seed)),
            ("YOLOv8s 640px 8ep", *y8s_paths(root, seed)),
        ]
        seed_has_y8s = False
        for model_label, ordinary_path, lodo_path in specs:
            if not ordinary_path.exists() or not lodo_path.exists():
                missing.extend(
                    str(path.relative_to(root))
                    for path in [ordinary_path, lodo_path]
                    if not path.exists()
                )
                continue
            if model_label.startswith("YOLOv8s"):
                seed_has_y8s = True
            ordinary = read_csv(ordinary_path).iloc[0]
            lodo = read_csv(lodo_path)
            setting_rows.append(
                {
                    "seed": seed,
                    "model_label": model_label,
                    "setting": "ordinary",
                    "n_runs": 1,
                    "precision_B": ordinary["precision_B"],
                    "recall_B": ordinary["recall_B"],
                    "mAP50_B": ordinary["mAP50_B"],
                    "mAP50_95_B": ordinary["mAP50_95_B"],
                }
            )
            setting_rows.append(
                {
                    "seed": seed,
                    "model_label": model_label,
                    "setting": "LODO mean",
                    "n_runs": len(lodo),
                    "precision_B": pd.to_numeric(lodo["precision_B"], errors="coerce").mean(),
                    "recall_B": pd.to_numeric(lodo["recall_B"], errors="coerce").mean(),
                    "mAP50_B": pd.to_numeric(lodo["mAP50_B"], errors="coerce").mean(),
                    "mAP50_95_B": pd.to_numeric(lodo["mAP50_95_B"], errors="coerce").mean(),
                }
            )
            for _, row in lodo.iterrows():
                domain_rows.append(
                    {
                        "seed": seed,
                        "model_label": model_label,
                        "heldout_domain": row["heldout_domain"],
                        "precision_B": row["precision_B"],
                        "recall_B": row["recall_B"],
                        "mAP50_B": row["mAP50_B"],
                        "mAP50_95_B": row["mAP50_95_B"],
                    }
                )
        if seed_has_y8s:
            completed_seeds.append(seed)
    return pd.DataFrame(setting_rows), pd.DataFrame(domain_rows), completed_seeds, missing


def summarize_setting(setting_runs: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for (model_label, setting), group in setting_runs.groupby(["model_label", "setting"], dropna=False):
        row: dict[str, object] = {
            "model_label": model_label,
            "setting": setting,
            "n_seed_runs": len(group),
            "n_detector_runs_total": int(pd.to_numeric(group["n_runs"], errors="coerce").sum()),
        }
        for metric in ["precision_B", "recall_B", "mAP50_B", "mAP50_95_B"]:
            values = pd.to_numeric(group[metric], errors="coerce")
            row[f"{metric}_mean"] = values.mean()
            row[f"{metric}_std"] = values.std(ddof=1) if len(values.dropna()) > 1 else 0.0
            row[f"{metric}_min"] = values.min()
            row[f"{metric}_max"] = values.max()
        rows.append(row)
    return pd.DataFrame(rows)


def compare_domains(domain_runs: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    n_domain = domain_runs[domain_runs["model_label"] == "YOLOv8n 320px 4ep"].rename(
        columns={
            "precision_B": "precision_B_yolov8n",
            "recall_B": "recall_B_yolov8n",
            "mAP50_B": "mAP50_B_yolov8n",
            "mAP50_95_B": "mAP50_95_B_yolov8n",
        }
    )
    s_domain = domain_runs[domain_runs["model_label"] == "YOLOv8s 640px 8ep"].rename(
        columns={
            "precision_B": "precision_B_yolov8s",
            "recall_B": "recall_B_yolov8s",
            "mAP50_B": "mAP50_B_yolov8s",
            "mAP50_95_B": "mAP50_95_B_yolov8s",
        }
    )
    comparison = n_domain.merge(s_domain, on=["seed", "heldout_domain"], suffixes=("", "_drop"))
    comparison = comparison[
        [
            "seed",
            "heldout_domain",
            "precision_B_yolov8n",
            "precision_B_yolov8s",
            "recall_B_yolov8n",
            "recall_B_yolov8s",
            "mAP50_B_yolov8n",
            "mAP50_B_yolov8s",
            "mAP50_95_B_yolov8n",
            "mAP50_95_B_yolov8s",
        ]
    ].copy()
    for metric in ["precision_B", "recall_B", "mAP50_B", "mAP50_95_B"]:
        comparison[f"{metric}_delta_yolov8s_minus_yolov8n"] = (
            pd.to_numeric(comparison[f"{metric}_yolov8s"], errors="coerce")
            - pd.to_numeric(comparison[f"{metric}_yolov8n"], errors="coerce")
        )
    comparison = comparison.sort_values(["heldout_domain", "seed"])

    rows: list[dict[str, object]] = []
    for domain, group in comparison.groupby("heldout_domain"):
        row: dict[str, object] = {"heldout_domain": domain, "n_seed_pairs": len(group)}
        for col in [
            "mAP50_B_yolov8n",
            "mAP50_B_yolov8s",
            "mAP50_B_delta_yolov8s_minus_yolov8n",
            "recall_B_yolov8n",
            "recall_B_yolov8s",
        ]:
            values = pd.to_numeric(group[col], errors="coerce")
            row[f"{col}_mean"] = values.mean()
            row[f"{col}_std"] = values.std(ddof=1) if len(values.dropna()) > 1 else 0.0
        rows.append(row)
    domain_summary = pd.DataFrame(rows).sort_values("mAP50_B_yolov8s_mean")
    return comparison, domain_summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize the completed G4b YOLOv8s detector-capacity bridge.")
    parser.add_argument("--out-dir", default="outputs/g4")
    parser.add_argument("--data-out-dir", default="data_processed/g4")
    args = parser.parse_args()

    root = project_root()
    out_dir = root / args.out_dir
    data_out_dir = root / args.data_out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    data_out_dir.mkdir(parents=True, exist_ok=True)

    setting_runs, domain_runs, completed_seeds, missing = collect_metric_rows(root)
    if setting_runs.empty or domain_runs.empty:
        raise SystemExit("No completed G4b bridge result pairs were found.")

    setting_summary = summarize_setting(setting_runs)
    domain_comparison, domain_summary = compare_domains(domain_runs)

    thresholds = {0.05, 0.10, 0.20, 0.50}
    calibration_rows = []
    image_rows = []
    for seed in SEEDS:
        for model_label, prefix in [
            ("YOLOv8n 320px 4ep", Y8N_PREFIXES[seed]),
            ("YOLOv8s 640px 8ep", Y8S_PREFIX.format(seed=seed)),
        ]:
            for split in ["ordinary", "lodo_all"]:
                cal = calibration_row(root, seed, model_label, prefix, split)
                if cal:
                    calibration_rows.append(cal)
                image_rows.extend(image_threshold_rows(root, seed, model_label, prefix, split, thresholds))
    calibration = pd.DataFrame(calibration_rows)
    image = pd.DataFrame(image_rows)

    setting_runs.to_csv(data_out_dir / "g4b_bridge_setting_runs.csv", index=False)
    setting_summary.to_csv(data_out_dir / "g4b_bridge_setting_summary.csv", index=False)
    domain_runs.to_csv(data_out_dir / "g4b_bridge_domain_long.csv", index=False)
    domain_comparison.to_csv(data_out_dir / "g4b_bridge_domain_comparison.csv", index=False)
    domain_summary.to_csv(data_out_dir / "g4b_bridge_domain_summary.csv", index=False)
    if not calibration.empty:
        calibration.to_csv(data_out_dir / "g4b_bridge_calibration_summary.csv", index=False)
    if not image.empty:
        image.to_csv(data_out_dir / "g4b_bridge_image_level_thresholds.csv", index=False)

    y8n_ord = setting_summary[
        (setting_summary["model_label"] == "YOLOv8n 320px 4ep") & (setting_summary["setting"] == "ordinary")
    ].iloc[0]
    y8s_ord = setting_summary[
        (setting_summary["model_label"] == "YOLOv8s 640px 8ep") & (setting_summary["setting"] == "ordinary")
    ].iloc[0]
    y8n_lodo = setting_summary[
        (setting_summary["model_label"] == "YOLOv8n 320px 4ep") & (setting_summary["setting"] == "LODO mean")
    ].iloc[0]
    y8s_lodo = setting_summary[
        (setting_summary["model_label"] == "YOLOv8s 640px 8ep") & (setting_summary["setting"] == "LODO mean")
    ].iloc[0]
    hardest = domain_summary.iloc[0] if not domain_summary.empty else None

    lines = [
        "# G4b YOLOv8s Detector-Capacity Bridge Summary",
        "",
        "Boundary: this bridge changes detector size, image size, epoch count, and GPU execution together. It tests whether the audit protocol remains informative with a stronger bounded baseline; it is not an architecture ranking or a full-scale benchmark.",
        "",
        f"Completed YOLOv8s bridge seeds: {', '.join(str(seed) for seed in completed_seeds) if completed_seeds else 'none'}.",
        "",
        "## Headline Metrics",
        "",
        f"- Ordinary mAP50 changes from {fmt(y8n_ord['mAP50_B_mean'])} +/- {fmt(y8n_ord['mAP50_B_std'])} with YOLOv8n 320px/4ep to {fmt(y8s_ord['mAP50_B_mean'])} +/- {fmt(y8s_ord['mAP50_B_std'])} with YOLOv8s 640px/8ep across completed seed pairs.",
        f"- Mean LODO mAP50 changes from {fmt(y8n_lodo['mAP50_B_mean'])} +/- {fmt(y8n_lodo['mAP50_B_std'])} to {fmt(y8s_lodo['mAP50_B_mean'])} +/- {fmt(y8s_lodo['mAP50_B_std'])}.",
    ]
    if hardest is not None:
        lines.append(
            f"- The lowest YOLOv8s held-out-domain mean mAP50 is {hardest['heldout_domain']} ({fmt(hardest['mAP50_B_yolov8s_mean'])} +/- {fmt(hardest['mAP50_B_yolov8s_std'])})."
        )
    lines.extend(["", "## Setting Summary", ""])
    lines.extend(
        markdown_table(
            setting_summary.sort_values(["model_label", "setting"]),
            [
                "model_label",
                "setting",
                "n_seed_runs",
                "n_detector_runs_total",
                "precision_B_mean",
                "recall_B_mean",
                "mAP50_B_mean",
                "mAP50_B_std",
                "mAP50_95_B_mean",
            ],
        )
    )
    lines.extend(["", "## Domain Bridge Summary", ""])
    if not domain_summary.empty:
        lines.extend(
            markdown_table(
                domain_summary,
                [
                    "heldout_domain",
                    "n_seed_pairs",
                    "mAP50_B_yolov8n_mean",
                    "mAP50_B_yolov8s_mean",
                    "mAP50_B_delta_yolov8s_minus_yolov8n_mean",
                    "recall_B_yolov8n_mean",
                    "recall_B_yolov8s_mean",
                ],
            )
        )
    if not calibration.empty:
        lines.extend(["", "## Calibration Bridge", ""])
        lines.extend(
            markdown_table(
                calibration.sort_values(["model_label", "seed", "split"]),
                [
                    "seed",
                    "model_label",
                    "split",
                    "n_predictions",
                    "ece_proxy",
                    "high_conf_n_predictions",
                    "high_conf_mean_confidence",
                    "high_conf_empirical_precision",
                    "high_conf_gap",
                ],
            )
        )
    if not image.empty:
        lines.extend(["", "## Image-Level Threshold Bridge", ""])
        image_view = image[
            [
                "seed",
                "model_label",
                "split",
                "threshold",
                "selected_images",
                "image_review_coverage",
                "selected_image_tp_rate",
                "gt_image_miss_proxy",
            ]
        ].copy()
        lines.extend(markdown_table(image_view.sort_values(["model_label", "seed", "split", "threshold"]), list(image_view.columns)))
    if missing:
        lines.extend(["", "## Missing Expected Files", ""])
        for path in missing:
            lines.append(f"- `{path}`")
    lines.extend(
        [
            "",
            "## Output Files",
            "",
            "- `data_processed/g4/g4b_bridge_setting_runs.csv`",
            "- `data_processed/g4/g4b_bridge_setting_summary.csv`",
            "- `data_processed/g4/g4b_bridge_domain_long.csv`",
            "- `data_processed/g4/g4b_bridge_domain_comparison.csv`",
            "- `data_processed/g4/g4b_bridge_domain_summary.csv`",
            "- `data_processed/g4/g4b_bridge_calibration_summary.csv`",
            "- `data_processed/g4/g4b_bridge_image_level_thresholds.csv`",
        ]
    )

    summary_path = out_dir / "g4b_bridge_summary.md"
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {summary_path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
