from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def filter_rows(rows: list[dict[str, str]], require_split: str | None) -> list[dict[str, str]]:
    usable_rows = [row for row in rows if row.get("kind", "image") == "image"]
    if require_split:
        usable_rows = [row for row in usable_rows if (row.get("split", "") or "") == require_split]
    return usable_rows


def write_leave_one_domain(rows: list[dict[str, str]], output: Path, require_split: str | None) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    usable_rows = filter_rows(rows, require_split)
    domains = sorted({row.get("domain", "unknown") or "unknown" for row in usable_rows})
    fields = ["fold", "held_out_domain", "image_path", "role"]
    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for domain in domains:
            fold = f"holdout_{domain}"
            for row in usable_rows:
                row_domain = row.get("domain", "unknown") or "unknown"
                writer.writerow(
                    {
                        "fold": fold,
                        "held_out_domain": domain,
                        "image_path": row.get("image_path", "") or row.get("path", ""),
                        "role": "test" if row_domain == domain else "train_pool",
                    }
                )
    return len(usable_rows)


def write_summary(rows: list[dict[str, str]], output: Path, require_split: str | None) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    usable_rows = filter_rows(rows, require_split)
    domains = sorted({row.get("domain", "unknown") or "unknown" for row in usable_rows})
    lines = [
        "# Leave-One-Domain Split Summary",
        "",
        f"- Images: {len(usable_rows)}",
        f"- Domains: {len(domains)}",
        f"- Required split: {require_split or 'any'}",
        "",
        "| Held-out domain | Train-pool images | Test images |",
        "| --- | ---: | ---: |",
    ]
    for domain in domains:
        test = sum(1 for row in usable_rows if (row.get("domain", "unknown") or "unknown") == domain)
        train = len(usable_rows) - test
        lines.append(f"| {domain} | {train} | {test} |")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build leave-one-domain split table from inventory.")
    parser.add_argument("--inventory", required=True, help="domain_inventory.csv path.")
    parser.add_argument("--splits", required=True, help="Output split CSV path.")
    parser.add_argument("--summary", required=True, help="Output summary Markdown path.")
    parser.add_argument("--require-split", default=None, help="Optional split filter, e.g. train.")
    args = parser.parse_args()

    rows = read_rows(Path(args.inventory))
    n_images = write_leave_one_domain(rows, Path(args.splits), args.require_split)
    write_summary(rows, Path(args.summary), args.require_split)
    print(f"Wrote split table with {n_images} images")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
