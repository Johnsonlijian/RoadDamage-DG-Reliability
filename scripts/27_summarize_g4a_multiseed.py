from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


SEED_PREFIXES = {
    20260512: "g3_frozen_subset",
    20260513: "g4a_r08_repeat_yolov8n_seed20260513",
    20260514: "g4a_r08_repeat_yolov8n_seed20260514",
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path)


def metric_summary(df: pd.DataFrame, group_cols: list[str], metrics: list[str]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for keys, group in df.groupby(group_cols, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        row = dict(zip(group_cols, keys))
        row["n_runs"] = len(group)
        for metric in metrics:
            values = pd.to_numeric(group[metric], errors="coerce")
            row[f"{metric}_mean"] = values.mean()
            row[f"{metric}_std"] = values.std(ddof=1) if len(values.dropna()) > 1 else 0.0
            row[f"{metric}_min"] = values.min()
            row[f"{metric}_max"] = values.max()
        rows.append(row)
    return pd.DataFrame(rows)


def calibration_row(root: Path, seed: int, prefix: str, split: str) -> dict[str, object]:
    path = root / "data_processed" / "calibration" / f"{prefix}_{split}_calibration_bins.csv"
    df = read_csv(path)
    n = pd.to_numeric(df["n_predictions"], errors="coerce").fillna(0)
    total = float(n.sum())
    ece = float(pd.to_numeric(df["ece_contribution"], errors="coerce").fillna(0).sum())
    high = df[pd.to_numeric(df["conf_low"], errors="coerce") >= 0.1].copy()
    high_n = pd.to_numeric(high["n_predictions"], errors="coerce").fillna(0)
    high_total = float(high_n.sum())
    if high_total:
        high_mean_conf = float((pd.to_numeric(high["mean_confidence"], errors="coerce").fillna(0) * high_n).sum() / high_total)
        high_tp = float((pd.to_numeric(high["empirical_precision"], errors="coerce").fillna(0) * high_n).sum())
        high_precision = high_tp / high_total
        high_gap = abs(high_mean_conf - high_precision)
    else:
        high_mean_conf = float("nan")
        high_precision = float("nan")
        high_gap = float("nan")
    return {
        "seed": seed,
        "split": split,
        "calibration_csv": str(path.relative_to(root)),
        "n_predictions": int(total),
        "ece_proxy": ece,
        "high_conf_n_predictions": int(high_total),
        "high_conf_mean_confidence": high_mean_conf,
        "high_conf_empirical_precision": high_precision,
        "high_conf_gap": high_gap,
    }


def threshold_rows(
    root: Path,
    seed: int,
    prefix: str,
    split: str,
    thresholds: set[float],
    kind: str,
) -> list[dict[str, object]]:
    if kind == "risk":
        path = root / "data_processed" / "calibration" / f"{prefix}_{split}_risk_coverage.csv"
    elif kind == "image":
        path = root / "data_processed" / "calibration" / f"{prefix}_{split}_image_level_coverage.csv"
    else:
        raise ValueError(kind)
    df = read_csv(path)
    out: list[dict[str, object]] = []
    df["threshold_key"] = pd.to_numeric(df["threshold"], errors="coerce").round(6)
    for threshold in sorted(thresholds):
        matches = df[df["threshold_key"] == round(threshold, 6)]
        if matches.empty:
            continue
        row = matches.iloc[0].to_dict()
        row.update(
            {
                "seed": seed,
                "split": split,
                "kind": kind,
                "source_csv": str(path.relative_to(root)),
            }
        )
        row.pop("threshold_key", None)
        out.append(row)
    return out


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


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize completed G4a multi-seed evidence.")
    parser.add_argument("--out-dir", default="outputs/g4")
    parser.add_argument("--data-out-dir", default="data_processed/g4")
    args = parser.parse_args()

    root = project_root()
    out_dir = root / args.out_dir
    data_out_dir = root / args.data_out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    data_out_dir.mkdir(parents=True, exist_ok=True)

    ordinary_rows: list[pd.DataFrame] = []
    lodo_rows: list[pd.DataFrame] = []
    calibration_rows: list[dict[str, object]] = []
    risk_rows: list[dict[str, object]] = []
    image_rows: list[dict[str, object]] = []
    thresholds = {0.05, 0.10, 0.20, 0.50}

    for seed, prefix in SEED_PREFIXES.items():
        if seed == 20260512:
            ordinary_csv = root / "data_processed" / "yolo_g3_frozen_subset_ordinary_result.csv"
            lodo_csv = root / "data_processed" / "yolo_g3_frozen_subset_lodo_results.csv"
        else:
            ordinary_csv = root / "data_processed" / "g4" / f"{prefix}_ordinary_result.csv"
            lodo_csv = root / "data_processed" / "g4" / f"{prefix}_lodo_results.csv"

        ordinary = read_csv(ordinary_csv)
        ordinary.insert(0, "seed", seed)
        ordinary.insert(1, "evidence_layer", "G4a" if seed != 20260512 else "R08-as-G4a-seed")
        ordinary.insert(2, "source_csv", str(ordinary_csv.relative_to(root)))
        ordinary_rows.append(ordinary)

        lodo = read_csv(lodo_csv)
        lodo.insert(0, "seed", seed)
        lodo.insert(1, "evidence_layer", "G4a" if seed != 20260512 else "R08-as-G4a-seed")
        lodo.insert(2, "source_csv", str(lodo_csv.relative_to(root)))
        lodo_rows.append(lodo)

        for split in ["ordinary", "lodo_all"]:
            calibration_rows.append(calibration_row(root, seed, prefix, split))
            risk_rows.extend(threshold_rows(root, seed, prefix, split, thresholds, "risk"))
            image_rows.extend(threshold_rows(root, seed, prefix, split, thresholds, "image"))

    ordinary_all = pd.concat(ordinary_rows, ignore_index=True)
    lodo_all = pd.concat(lodo_rows, ignore_index=True)
    runs_all = pd.concat(
        [
            ordinary_all.assign(setting="ordinary", heldout_domain="mixed"),
            lodo_all.assign(setting="lodo"),
        ],
        ignore_index=True,
        sort=False,
    )

    metrics = ["precision_B", "recall_B", "mAP50_B", "mAP50_95_B"]
    ordinary_summary = metric_summary(ordinary_all, ["model", "epochs", "imgsz"], metrics)
    lodo_by_domain = metric_summary(lodo_all, ["model", "epochs", "imgsz", "heldout_domain"], metrics)
    lodo_overall = metric_summary(lodo_all.assign(pool="all_lodo_domains"), ["model", "epochs", "imgsz", "pool"], metrics)
    calibration = pd.DataFrame(calibration_rows)
    risk = pd.DataFrame(risk_rows)
    image = pd.DataFrame(image_rows)

    runs_all.to_csv(data_out_dir / "g4a_multiseed_runs.csv", index=False)
    ordinary_summary.to_csv(data_out_dir / "g4a_multiseed_ordinary_summary.csv", index=False)
    lodo_by_domain.to_csv(data_out_dir / "g4a_multiseed_lodo_by_domain_summary.csv", index=False)
    lodo_overall.to_csv(data_out_dir / "g4a_multiseed_lodo_overall_summary.csv", index=False)
    calibration.to_csv(data_out_dir / "g4a_multiseed_calibration_summary.csv", index=False)
    risk.to_csv(data_out_dir / "g4a_multiseed_risk_coverage_thresholds.csv", index=False)
    image.to_csv(data_out_dir / "g4a_multiseed_image_level_thresholds.csv", index=False)

    ordinary_gap = float(ordinary_summary.iloc[0]["mAP50_B_mean"] - lodo_overall.iloc[0]["mAP50_B_mean"])
    hardest = lodo_by_domain.sort_values("mAP50_B_mean").iloc[0]
    most_variable = lodo_by_domain.sort_values("mAP50_B_std", ascending=False).iloc[0]

    lines = [
        "# G4a Multi-Seed YOLOv8n Summary",
        "",
        "Boundary: this summarizes the completed bounded subset evidence layer for YOLOv8n only. It does not establish full-scale detector performance, deployment readiness, or a calibrated referral policy.",
        "",
        "Included seeds: 20260512 (original R08 CPU baseline treated as the first seed-level run), 20260513, and 20260514. Each seed contains one ordinary mixed-domain run and seven leave-one-domain-out runs.",
        "",
        "## Headline Metrics",
        "",
        f"- Ordinary mixed-domain mean mAP50: {fmt(ordinary_summary.iloc[0]['mAP50_B_mean'])} +/- {fmt(ordinary_summary.iloc[0]['mAP50_B_std'])} across 3 seeds.",
        f"- Pooled LODO-domain mean mAP50: {fmt(lodo_overall.iloc[0]['mAP50_B_mean'])} +/- {fmt(lodo_overall.iloc[0]['mAP50_B_std'])} across 21 held-out-domain runs.",
        f"- Ordinary-minus-LODO mAP50 gap: {fmt(ordinary_gap)}.",
        f"- Lowest mean held-out mAP50 domain: {hardest['heldout_domain']} ({fmt(hardest['mAP50_B_mean'])} +/- {fmt(hardest['mAP50_B_std'])}).",
        f"- Largest across-seed held-out mAP50 spread: {most_variable['heldout_domain']} (std {fmt(most_variable['mAP50_B_std'])}).",
        "",
        "## Ordinary Summary",
        "",
    ]
    lines.extend(
        markdown_table(
            ordinary_summary,
            [
                "model",
                "epochs",
                "imgsz",
                "n_runs",
                "precision_B_mean",
                "recall_B_mean",
                "mAP50_B_mean",
                "mAP50_B_std",
                "mAP50_95_B_mean",
            ],
        )
    )
    lines.extend(["", "## LODO Overall Summary", ""])
    lines.extend(
        markdown_table(
            lodo_overall,
            [
                "model",
                "epochs",
                "imgsz",
                "n_runs",
                "precision_B_mean",
                "recall_B_mean",
                "mAP50_B_mean",
                "mAP50_B_std",
                "mAP50_95_B_mean",
            ],
        )
    )
    lines.extend(["", "## LODO By Held-Out Domain", ""])
    lines.extend(
        markdown_table(
            lodo_by_domain.sort_values("mAP50_B_mean"),
            [
                "heldout_domain",
                "n_runs",
                "precision_B_mean",
                "recall_B_mean",
                "mAP50_B_mean",
                "mAP50_B_std",
                "mAP50_95_B_mean",
            ],
        )
    )
    lines.extend(["", "## Calibration And Threshold Artifacts", ""])
    lines.append(
        "Per-seed calibration, prediction-row risk-coverage, and image-level coverage tables were regenerated for ordinary and pooled LODO exports. Manuscript text should report these as audit diagnostics, not as calibrated deployment thresholds."
    )
    lines.extend(["", "### Calibration Summary", ""])
    lines.extend(
        markdown_table(
            calibration,
            [
                "seed",
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
    lines.extend(["", "### Image-Level Coverage At Selected Thresholds", ""])
    image_view = image[
        [
            "seed",
            "split",
            "threshold",
            "selected_images",
            "image_review_coverage",
            "selected_image_tp_rate",
            "gt_image_miss_proxy",
        ]
    ].copy()
    lines.extend(markdown_table(image_view, list(image_view.columns)))
    lines.extend(["", "## Output Files", ""])
    for path in [
        "data_processed/g4/g4a_multiseed_runs.csv",
        "data_processed/g4/g4a_multiseed_ordinary_summary.csv",
        "data_processed/g4/g4a_multiseed_lodo_by_domain_summary.csv",
        "data_processed/g4/g4a_multiseed_lodo_overall_summary.csv",
        "data_processed/g4/g4a_multiseed_calibration_summary.csv",
        "data_processed/g4/g4a_multiseed_risk_coverage_thresholds.csv",
        "data_processed/g4/g4a_multiseed_image_level_thresholds.csv",
    ]:
        lines.append(f"- `{path}`")

    summary_path = out_dir / "g4a_multiseed_summary.md"
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {summary_path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
