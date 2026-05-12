from __future__ import annotations

import argparse
import csv
import html
import json
from collections import Counter
from pathlib import Path


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def count_labels(rows: list[dict[str, str]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for row in rows:
        raw = row.get("label_counts_json", "{}")
        try:
            values = json.loads(raw)
        except json.JSONDecodeError:
            values = {}
        for label, value in values.items():
            counts[str(label)] += int(value)
    return counts


def count_domains(rows: list[dict[str, str]]) -> Counter[str]:
    usable_rows = [row for row in rows if row.get("kind", "image") == "image"]
    return Counter(row.get("domain", "unknown") or "unknown" for row in usable_rows)


def bar_svg(counts: Counter[str], title: str, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    width = 960
    row_h = 34
    margin_l = 210
    margin_r = 40
    top = 70
    height = top + max(1, len(items)) * row_h + 50
    max_value = max([v for _, v in items] or [1])
    bar_w = width - margin_l - margin_r
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="32" y="38" font-family="Arial" font-size="22" font-weight="700">{html.escape(title)}</text>',
    ]
    if not items:
        lines.append(
            '<text x="32" y="92" font-family="Arial" font-size="16" fill="#666">Pending: no parsed labels in this inventory.</text>'
        )
    for i, (name, value) in enumerate(items):
        y = top + i * row_h
        w = 1 if max_value == 0 else int(bar_w * value / max_value)
        lines.append(
            f'<text x="32" y="{y + 20}" font-family="Arial" font-size="15" fill="#222">{html.escape(name)}</text>'
        )
        lines.append(f'<rect x="{margin_l}" y="{y}" width="{w}" height="22" fill="#3366aa"/>')
        lines.append(
            f'<text x="{margin_l + w + 8}" y="{y + 17}" font-family="Arial" font-size="14" fill="#222">{value}</text>'
        )
    lines.append("</svg>")
    output.write_text("\n".join(lines), encoding="utf-8")


def write_markdown(domain_counts: Counter[str], label_counts: Counter[str], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Inventory Figure Inputs", ""]
    lines.extend(["## Domains", ""])
    for key, value in sorted(domain_counts.items()):
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Labels", ""])
    for key, value in sorted(label_counts.items()):
        lines.append(f"- {key}: {value}")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build simple SVG inventory figures from domain inventory CSV.")
    parser.add_argument("--inventory", required=True, help="domain_inventory.csv path.")
    parser.add_argument("--outdir", required=True, help="Output figure directory.")
    args = parser.parse_args()

    rows = read_rows(Path(args.inventory))
    domain_counts = count_domains(rows)
    label_counts = count_labels(rows)
    outdir = Path(args.outdir)
    bar_svg(domain_counts, "Images by domain", outdir / "fig02a_images_by_domain.svg")
    bar_svg(label_counts, "Damage annotations by class", outdir / "fig02b_annotations_by_class.svg")
    write_markdown(domain_counts, label_counts, outdir / "fig02_inventory_inputs.md")
    print(f"Wrote inventory figures to {outdir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
