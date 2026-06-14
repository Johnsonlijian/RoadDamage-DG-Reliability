"""Public-safe R59 acceptance-gate summary.

This script reads derived, non-sensitive source tables included in the public
repository. It does not require raw RDD images, trained weights, active
manuscripts, cover letters, or internal round logs.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data_processed" / "r59_acceptance_gate" / "source_tables"
OUT = ROOT / "outputs" / "r59"


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else float("nan")


def kstar(values_by_k: dict[int, list[float]], threshold: float = 0.20) -> tuple[str, str]:
    mean_k = None
    all_seed_k = None
    for k in sorted(values_by_k):
        vals = values_by_k[k]
        if mean_k is None and mean(vals) >= threshold:
            mean_k = k
        if all_seed_k is None and min(vals) >= threshold:
            all_seed_k = k
    return (
        str(mean_k) if mean_k is not None else ">320",
        str(all_seed_k) if all_seed_k is not None else ">320",
    )


def load_dose() -> dict[str, dict[int, list[float]]]:
    dose: dict[str, dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))
    with (SRC / "r43_dose_curves.csv").open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            dose[row["domain"]][int(row["k"])].append(float(row["mAP50"]))
    return dose


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    dose = load_dose()
    lines = [
        "# R59 Acceptance-Gate Public Summary",
        "",
        "Source: `data_processed/r59_acceptance_gate/source_tables/r43_dose_curves.csv`.",
        "Criterion: mAP50 >= 0.20, reported as an audit criterion rather than a deployment threshold.",
        "",
        "| Domain | K=0 mean | K=320 mean | K* mean | K* same-K all-seed clearance |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for domain in sorted(dose):
        mean_k, all_seed_k = kstar(dose[domain])
        lines.append(
            f"| {domain} | {mean(dose[domain][0]):.3f} | {mean(dose[domain][320]):.3f} | {mean_k} | {all_seed_k} |"
        )
    lines.extend(
        [
            "",
            "Boundary: these are derived summary results from the R59/AutCon acceptance-gate package.",
            "Raw RDD images, trained weights, active manuscripts, cover letters, and internal round logs are not redistributed.",
            "",
        ]
    )
    (OUT / "r59_acceptance_gate_summary.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(OUT / "r59_acceptance_gate_summary.md")


if __name__ == "__main__":
    main()
