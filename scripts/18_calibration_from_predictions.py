from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


DEFAULT_THRESHOLDS = [0.0, 0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.2, 0.3, 0.5]


@dataclass
class Prediction:
    confidence: float
    is_tp: bool
    domain: str
    cls: str


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def as_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def prediction_rows(rows: list[dict[str, str]]) -> list[Prediction]:
    preds: list[Prediction] = []
    for row in rows:
        if row.get("outcome") not in {"TP", "FP"}:
            continue
        preds.append(
            Prediction(
                confidence=as_float(row.get("confidence", "")),
                is_tp=row.get("outcome") == "TP",
                domain=row.get("domain", "unknown"),
                cls=row.get("pred_class") or row.get("gt_class") or "unknown",
            )
        )
    return preds


def count_gt(rows: list[dict[str, str]]) -> int:
    return sum(1 for row in rows if row.get("outcome") in {"TP", "FN"})


def calibration_bins(preds: list[Prediction], bins: int) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    total = len(preds) or 1
    for idx in range(bins):
        lo = idx / bins
        hi = (idx + 1) / bins
        if idx == bins - 1:
            members = [pred for pred in preds if lo <= pred.confidence <= hi]
        else:
            members = [pred for pred in preds if lo <= pred.confidence < hi]
        n = len(members)
        tp = sum(1 for pred in members if pred.is_tp)
        fp = n - tp
        mean_conf = sum(pred.confidence for pred in members) / n if n else 0.0
        precision = tp / n if n else 0.0
        abs_gap = abs(mean_conf - precision) if n else 0.0
        out.append(
            {
                "bin": str(idx),
                "conf_low": f"{lo:.3f}",
                "conf_high": f"{hi:.3f}",
                "n_predictions": str(n),
                "tp": str(tp),
                "fp": str(fp),
                "mean_confidence": f"{mean_conf:.6f}",
                "empirical_precision": f"{precision:.6f}",
                "abs_calibration_gap": f"{abs_gap:.6f}",
                "ece_contribution": f"{(n / total) * abs_gap:.6f}",
            }
        )
    return out


def risk_coverage(preds: list[Prediction], total_gt: int, thresholds: list[float]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    total_preds = len(preds) or 1
    total_gt = total_gt or 1
    for threshold in thresholds:
        accepted = [pred for pred in preds if pred.confidence >= threshold]
        n = len(accepted)
        tp = sum(1 for pred in accepted if pred.is_tp)
        fp = n - tp
        precision = tp / n if n else 0.0
        residual_error = fp / n if n else 0.0
        recall = tp / total_gt
        out.append(
            {
                "threshold": f"{threshold:.6f}",
                "accepted_predictions": str(n),
                "referred_or_rejected_predictions": str(len(preds) - n),
                "prediction_coverage": f"{n / total_preds:.6f}",
                "tp": str(tp),
                "fp": str(fp),
                "precision": f"{precision:.6f}",
                "residual_error_rate": f"{residual_error:.6f}",
                "gt_recall_after_acceptance": f"{recall:.6f}",
            }
        )
    return out


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_summary(
    bins: list[dict[str, str]],
    risk: list[dict[str, str]],
    output: Path,
    args: argparse.Namespace,
    n_pred: int,
    n_gt: int,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")
    ece = sum(as_float(row["ece_contribution"]) for row in bins)
    lines = [
        "# Calibration And Risk-Coverage Summary",
        "",
        f"Generated: {generated}, local time",
        "",
        "## Configuration",
        "",
        f"- Prediction table: `{args.predictions}`",
        f"- Bins: `{args.bins}`",
        f"- Prediction rows: `{n_pred}`",
        f"- Ground-truth objects counted through TP+FN rows: `{n_gt}`",
        "",
        "## Prediction-Level Calibration",
        "",
        f"- Expected calibration error proxy: `{ece:.6f}`",
        "",
        "| Bin | Confidence range | N | Mean confidence | Empirical precision | Abs gap |",
        "|---:|---|---:|---:|---:|---:|",
    ]
    for row in bins:
        lines.append(
            "| {bin} | [{lo}, {hi}] | {n} | {mean} | {precision} | {gap} |".format(
                bin=row["bin"],
                lo=row["conf_low"],
                hi=row["conf_high"],
                n=row["n_predictions"],
                mean=row["mean_confidence"],
                precision=row["empirical_precision"],
                gap=row["abs_calibration_gap"],
            )
        )
    lines.extend(
        [
            "",
            "## Risk-Coverage",
            "",
            "| Threshold | Coverage | Accepted | Precision | Residual error | GT recall |",
            "|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in risk:
        lines.append(
            "| {thr} | {coverage} | {accepted} | {precision} | {error} | {recall} |".format(
                thr=row["threshold"],
                coverage=row["prediction_coverage"],
                accepted=row["accepted_predictions"],
                precision=row["precision"],
                error=row["residual_error_rate"],
                recall=row["gt_recall_after_acceptance"],
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This is a prediction-level calibration proxy for object detections. It supports method development and failure analysis, but paper claims require fixed G3 baselines and consistent thresholds.",
        ]
    )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build calibration and risk-coverage tables from prediction rows.")
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--bins", type=int, default=10)
    parser.add_argument("--thresholds", nargs="*", type=float, default=DEFAULT_THRESHOLDS)
    parser.add_argument("--calibration-csv", required=True)
    parser.add_argument("--risk-csv", required=True)
    parser.add_argument("--summary", required=True)
    args = parser.parse_args()

    raw_rows = read_rows(Path(args.predictions))
    preds = prediction_rows(raw_rows)
    total_gt = count_gt(raw_rows)
    bin_rows = calibration_bins(preds, args.bins)
    risk_rows = risk_coverage(preds, total_gt, args.thresholds)
    write_csv(bin_rows, Path(args.calibration_csv))
    write_csv(risk_rows, Path(args.risk_csv))
    write_summary(bin_rows, risk_rows, Path(args.summary), args, len(preds), total_gt)
    print(f"Wrote {args.calibration_csv}")
    print(f"Wrote {args.risk_csv}")
    print(f"Wrote {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
