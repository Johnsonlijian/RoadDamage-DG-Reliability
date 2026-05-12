from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path


DEFAULT_IMAGE_SUMMARY = Path("data_processed/rdd2022_image_xml_summary.csv")
DEFAULT_BOXES = Path("data_processed/rdd2022_boxes.csv")
DEFAULT_LABEL_MAP = Path("data_raw/RDD2022_metadata/label_map.pbtxt")
DEFAULT_SUMMARY = Path("outputs/rdd2022_extracted_inventory_audit.md")
DEFAULT_LABEL_COUNTS = Path("data_processed/rdd2022_label_counts.csv")
DEFAULT_DOMAIN_LABEL_COUNTS = Path("data_processed/rdd2022_domain_label_counts.csv")


def parse_label_map(path: Path) -> set[str]:
    if not path.exists():
        return set()
    text = path.read_text(encoding="utf-8", errors="ignore")
    return {name for _, name in re.findall(r"id:\s*(\d+)\s+name:\s*'([^']+)'", text)}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_counts_csv(counts: Counter[str], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["label", "count"])
        writer.writeheader()
        for label, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
            writer.writerow({"label": label, "count": count})


def write_domain_label_csv(counts: dict[tuple[str, str], int], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["domain", "label", "count"])
        writer.writeheader()
        for (domain, label), count in sorted(counts.items()):
            writer.writerow({"domain": domain, "label": label, "count": count})


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize extracted RDD2022 XML and label inventory.")
    parser.add_argument("--image-summary", default=str(DEFAULT_IMAGE_SUMMARY))
    parser.add_argument("--boxes", default=str(DEFAULT_BOXES))
    parser.add_argument("--label-map", default=str(DEFAULT_LABEL_MAP))
    parser.add_argument("--summary", default=str(DEFAULT_SUMMARY))
    parser.add_argument("--label-counts", default=str(DEFAULT_LABEL_COUNTS))
    parser.add_argument("--domain-label-counts", default=str(DEFAULT_DOMAIN_LABEL_COUNTS))
    args = parser.parse_args()

    image_rows = read_csv(Path(args.image_summary))
    box_rows = read_csv(Path(args.boxes))
    primary_labels = parse_label_map(Path(args.label_map))
    domain_images = Counter(row["domain"] for row in image_rows)
    domain_boxes = Counter(row["domain"] for row in box_rows)
    label_counts = Counter(row["label"] for row in box_rows)
    domain_label_counts: dict[tuple[str, str], int] = defaultdict(int)
    primary_count = 0
    non_primary_count = 0
    for row in box_rows:
        label = row["label"]
        domain = row["domain"]
        domain_label_counts[(domain, label)] += 1
        if label in primary_labels:
            primary_count += 1
        else:
            non_primary_count += 1

    write_counts_csv(label_counts, Path(args.label_counts))
    write_domain_label_csv(domain_label_counts, Path(args.domain_label_counts))

    lines = [
        "# RDD2022 Extracted Inventory Audit",
        "",
        "## Totals",
        "",
        f"- XML image rows: {len(image_rows)}",
        f"- Box rows: {len(box_rows)}",
        f"- Primary label-map classes: {', '.join(sorted(primary_labels)) if primary_labels else '[not found]'}",
        f"- Primary-class boxes: {primary_count}",
        f"- Non-primary observed boxes: {non_primary_count}",
        "",
        "## Train XML Images By Domain",
        "",
    ]
    for domain, count in sorted(domain_images.items()):
        lines.append(f"- {domain}: {count}")
    lines.extend(["", "## Boxes By Domain", ""])
    for domain, count in sorted(domain_boxes.items()):
        lines.append(f"- {domain}: {count}")
    lines.extend(["", "## Boxes By Label", ""])
    for label, count in sorted(label_counts.items(), key=lambda item: (-item[1], item[0])):
        marker = "primary" if label in primary_labels else "non-primary-observed"
        lines.append(f"- {label}: {count} ({marker})")
    lines.extend(
        [
            "",
            "## Interpretation Boundary",
            "",
            "Use the label-map classes as the primary supervised detection task unless the additional observed labels are verified against official RDD documentation. Non-primary observed labels must be reported as ignored, merged, or modeled only after an explicit task definition.",
        ]
    )
    Path(args.summary).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote extracted inventory audit to {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
