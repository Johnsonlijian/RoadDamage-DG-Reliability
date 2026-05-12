from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def safe_div(num: int, den: int) -> float:
    return num / den if den else 0.0


def summarize(rows: list[dict[str, str]], group_keys: list[str]) -> list[dict[str, str]]:
    counts: dict[tuple[str, ...], dict[str, int]] = defaultdict(lambda: {"TP": 0, "FP": 0, "FN": 0})
    for row in rows:
        cls = row.get("pred_class") or row.get("gt_class") or "unknown"
        values = []
        for key in group_keys:
            if key == "class":
                values.append(cls)
            else:
                values.append(row.get(key, "unknown") or "unknown")
        outcome = row.get("outcome", "")
        if outcome in {"TP", "FP", "FN"}:
            counts[tuple(values)][outcome] += 1
    out = []
    for key_values, count in sorted(counts.items()):
        tp = count["TP"]
        fp = count["FP"]
        fn = count["FN"]
        row = {key: value for key, value in zip(group_keys, key_values)}
        row.update(
            {
                "TP": str(tp),
                "FP": str(fp),
                "FN": str(fn),
                "precision": f"{safe_div(tp, tp + fp):.6f}",
                "recall": f"{safe_div(tp, tp + fn):.6f}",
                "support_gt": str(tp + fn),
                "predictions": str(tp + fp),
            }
        )
        out.append(row)
    return out


def write_markdown(
    domain_rows: list[dict[str, str]],
    class_rows: list[dict[str, str]],
    output: Path,
    title: str,
    boundary: str,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {title}",
        "",
        f"Boundary: {boundary}",
        "",
        "## By Held-Out Domain",
        "",
        "| Held-out domain | TP | FP | FN | Precision | Recall |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in domain_rows:
        lines.append(
            "| {domain} | {tp} | {fp} | {fn} | {precision} | {recall} |".format(
                domain=row.get("heldout_domain", "unknown"),
                tp=row["TP"],
                fp=row["FP"],
                fn=row["FN"],
                precision=row["precision"],
                recall=row["recall"],
            )
        )
    lines.extend(
        [
            "",
            "## By Class, Pooled LODO",
            "",
            "| Class | TP | FP | FN | Precision | Recall |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in class_rows:
        lines.append(
            "| {cls} | {tp} | {fp} | {fn} | {precision} | {recall} |".format(
                cls=row.get("class", "unknown"),
                tp=row["TP"],
                fp=row["FP"],
                fn=row["FN"],
                precision=row["precision"],
                recall=row["recall"],
            )
        )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize TP/FP/FN prediction export rows.")
    parser.add_argument("--predictions", default="data_processed/predictions/g3_timing_lodo_all_predictions.csv")
    parser.add_argument("--domain-csv", default="data_processed/g3_timing_lodo_error_by_domain.csv")
    parser.add_argument("--domain-class-csv", default="data_processed/g3_timing_lodo_error_by_domain_class.csv")
    parser.add_argument("--class-csv", default="data_processed/g3_timing_lodo_error_by_class.csv")
    parser.add_argument("--summary", default="outputs/g3_timing_error_taxonomy_summary.md")
    parser.add_argument("--title", default="G3 Timing Error Taxonomy Summary")
    parser.add_argument(
        "--boundary",
        default="timing/subset-scale prediction export. Use for method development and failure-analysis planning, not final paper claims.",
    )
    args = parser.parse_args()

    rows = read_rows(Path(args.predictions))
    by_domain = summarize(rows, ["heldout_domain"])
    by_domain_class = summarize(rows, ["heldout_domain", "class"])
    by_class = summarize(rows, ["class"])
    write_csv(by_domain, Path(args.domain_csv))
    write_csv(by_domain_class, Path(args.domain_class_csv))
    write_csv(by_class, Path(args.class_csv))
    write_markdown(by_domain, by_class, Path(args.summary), args.title, args.boundary)
    print(f"Wrote {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
