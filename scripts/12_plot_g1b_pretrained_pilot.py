from __future__ import annotations

import argparse
import csv
import html
from pathlib import Path


METRICS = [
    ("recall_B", "Recall", "#2f6f9f"),
    ("mAP50_B", "mAP50", "#5b8f3a"),
    ("mAP50_95_B", "mAP50-95", "#b7652b"),
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def as_float(row: dict[str, str], key: str) -> float:
    try:
        return float(row.get(key, "") or 0.0)
    except ValueError:
        return 0.0


def unique_value(rows: list[dict[str, str]], key: str, fallback: str) -> str:
    values = sorted({(row.get(key, "") or "").strip() for row in rows if row.get(key, "")})
    if not values:
        return fallback
    if len(values) == 1:
        return values[0]
    return f"{values[0]}-{values[-1]}"


def run_boundary(rows: list[dict[str, str]]) -> str:
    model = unique_value(rows, "model", "YOLOv8n pretrained")
    epochs = unique_value(rows, "epochs", "unknown")
    imgsz = unique_value(rows, "imgsz", "unknown")
    train = unique_value(rows, "train_images", "unknown")
    val = unique_value(rows, "val_images", "unknown")
    return (
        f"{model}, {epochs} CPU epochs, image size {imgsz}, "
        f"{train} train images and {val} held-out validation images per domain."
    )


def write_svg(rows: list[dict[str, str]], output: Path, title: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    width = 1120
    left = 190
    top = 108
    row_h = 54
    panel_gap = 34
    panel_w = 250
    height = top + row_h * max(1, len(rows)) + 86
    max_by_metric = {
        key: max([as_float(row, key) for row in rows] or [0.0]) for key, _, _ in METRICS
    }
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="32" y="38" font-family="Arial" font-size="22" font-weight="700">{html.escape(title)}</text>',
        f'<text x="32" y="66" font-family="Arial" font-size="14" fill="#555">{html.escape(run_boundary(rows))} Pilot only.</text>',
    ]
    for j, (_, label, _) in enumerate(METRICS):
        x = left + j * (panel_w + panel_gap)
        lines.append(
            f'<text x="{x}" y="96" font-family="Arial" font-size="14" font-weight="700" fill="#222">{html.escape(label)}</text>'
        )
        lines.append(f'<line x1="{x}" x2="{x + panel_w}" y1="104" y2="104" stroke="#ddd"/>')
    for i, row in enumerate(rows):
        y = top + i * row_h
        domain = row.get("heldout_domain", "unknown")
        lines.append(
            f'<text x="32" y="{y + 26}" font-family="Arial" font-size="14" fill="#222">{html.escape(domain)}</text>'
        )
        for j, (key, _, color) in enumerate(METRICS):
            x = left + j * (panel_w + panel_gap)
            value = as_float(row, key)
            max_value = max_by_metric[key] or 1.0
            bar_w = max(1, int((panel_w - 64) * value / max_value)) if value > 0 else 0
            lines.append(f'<rect x="{x}" y="{y + 9}" width="{panel_w - 64}" height="22" fill="#f1f3f5"/>')
            if bar_w:
                lines.append(f'<rect x="{x}" y="{y + 9}" width="{bar_w}" height="22" fill="{color}"/>')
            lines.append(
                f'<text x="{x + panel_w - 54}" y="{y + 25}" font-family="Arial" font-size="13" fill="#222">{value:.4f}</text>'
            )
    lines.extend(
        [
            f'<text x="32" y="{height - 34}" font-family="Arial" font-size="13" fill="#666">Interpretation boundary: this figure supports go/no-go decisions only; it is not final model performance.</text>',
            "</svg>",
        ]
    )
    output.write_text("\n".join(lines), encoding="utf-8")


def write_markdown(rows: list[dict[str, str]], output: Path, title: str) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {title} Figure Inputs",
        "",
        f"Run boundary: {run_boundary(rows)}",
        "",
        "| Held-out domain | Recall | mAP50 | mAP50-95 |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {domain} | {recall:.4f} | {map50:.4f} | {map5095:.4f} |".format(
                domain=row.get("heldout_domain", "unknown"),
                recall=as_float(row, "recall_B"),
                map50=as_float(row, "mAP50_B"),
                map5095=as_float(row, "mAP50_95_B"),
            )
        )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Plot the G1B pretrained pilot matrix as a simple SVG.")
    parser.add_argument("--matrix", default="outputs/g1b_pretrained_pilot_matrix.csv")
    parser.add_argument("--svg", default="manuscript/figures/fig_g1b_pretrained_pilot_matrix.svg")
    parser.add_argument("--summary", default="manuscript/figures/fig_g1b_pretrained_pilot_inputs.md")
    parser.add_argument("--title", default="G1B pretrained LODO pilot")
    args = parser.parse_args()

    rows = read_rows(Path(args.matrix))
    write_svg(rows, Path(args.svg), args.title)
    write_markdown(rows, Path(args.summary), args.title)
    print(f"Wrote {args.svg} and {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
