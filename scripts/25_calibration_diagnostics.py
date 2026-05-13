from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def as_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def prediction_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row.get("outcome") in {"TP", "FP"}]


def group_key(row: dict[str, str], fields: list[str]) -> str:
    if not fields:
        return "all"
    return "|".join(row.get(field, "") or "unknown" for field in fields)


def calibration_summary(rows: list[dict[str, str]], bins: int, high_conf: float) -> dict[str, str]:
    total = len(rows)
    if total == 0:
        return {
            "n_predictions": "0",
            "tp": "0",
            "fp": "0",
            "precision": "0.000000",
            "ece": "0.000000",
            "max_bin_gap": "0.000000",
            "high_conf_threshold": f"{high_conf:.6f}",
            "high_conf_predictions": "0",
            "high_conf_precision": "0.000000",
            "high_conf_mean_confidence": "0.000000",
            "high_conf_abs_gap": "0.000000",
        }

    tp = sum(1 for row in rows if row.get("outcome") == "TP")
    fp = total - tp
    ece = 0.0
    max_gap = 0.0
    for idx in range(bins):
        lo = idx / bins
        hi = (idx + 1) / bins
        if idx == bins - 1:
            members = [row for row in rows if lo <= as_float(row.get("confidence", "")) <= hi]
        else:
            members = [row for row in rows if lo <= as_float(row.get("confidence", "")) < hi]
        n = len(members)
        if not n:
            continue
        bin_tp = sum(1 for row in members if row.get("outcome") == "TP")
        mean_conf = sum(as_float(row.get("confidence", "")) for row in members) / n
        precision = bin_tp / n
        gap = abs(mean_conf - precision)
        ece += (n / total) * gap
        max_gap = max(max_gap, gap)

    high = [row for row in rows if as_float(row.get("confidence", "")) >= high_conf]
    high_n = len(high)
    high_tp = sum(1 for row in high if row.get("outcome") == "TP")
    high_precision = high_tp / high_n if high_n else 0.0
    high_mean_conf = sum(as_float(row.get("confidence", "")) for row in high) / high_n if high_n else 0.0
    return {
        "n_predictions": str(total),
        "tp": str(tp),
        "fp": str(fp),
        "precision": f"{tp / total:.6f}",
        "ece": f"{ece:.6f}",
        "max_bin_gap": f"{max_gap:.6f}",
        "high_conf_threshold": f"{high_conf:.6f}",
        "high_conf_predictions": str(high_n),
        "high_conf_precision": f"{high_precision:.6f}",
        "high_conf_mean_confidence": f"{high_mean_conf:.6f}",
        "high_conf_abs_gap": f"{abs(high_mean_conf - high_precision):.6f}" if high_n else "0.000000",
    }


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_summary(rows: list[dict[str, str]], output: Path, args: argparse.Namespace) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# Calibration Diagnostics Summary",
        "",
        f"Generated: {generated}, local time",
        "",
        "## Configuration",
        "",
        f"- Prediction table: `{args.predictions}`",
        f"- Group fields: `{', '.join(args.group_by) if args.group_by else 'all'}`",
        f"- Bins: `{args.bins}`",
        f"- High-confidence threshold: `{args.high_conf}`",
        "",
        "## Diagnostics",
        "",
        "| Group | N | Precision | ECE proxy | Max bin gap | High-conf N | High-conf precision | High-conf mean conf | High-conf gap |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {group} | {n_predictions} | {precision} | {ece} | {max_bin_gap} | {high_conf_predictions} | {high_conf_precision} | {high_conf_mean_confidence} | {high_conf_abs_gap} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "These are prediction-level calibration diagnostics for object-detection exports. They support reliability auditing, but they do not validate an operational reject option or deployment threshold.",
        ]
    )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize pooled, grouped, and high-confidence calibration gaps.")
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--group-by", nargs="*", default=["domain"])
    parser.add_argument("--bins", type=int, default=10)
    parser.add_argument("--high-conf", type=float, default=0.1)
    parser.add_argument("--csv", required=True)
    parser.add_argument("--summary", required=True)
    args = parser.parse_args()

    rows = prediction_rows(read_rows(Path(args.predictions)))
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    grouped["all"] = list(rows)
    for row in rows:
        grouped[group_key(row, args.group_by)].append(row)

    out_rows: list[dict[str, str]] = []
    for group in sorted(grouped, key=lambda value: (value != "all", value)):
        out_rows.append({"group": group, **calibration_summary(grouped[group], args.bins, args.high_conf)})
    write_csv(out_rows, Path(args.csv))
    write_summary(out_rows, Path(args.summary), args)
    print(f"Wrote {args.csv}")
    print(f"Wrote {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
