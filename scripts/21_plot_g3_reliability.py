from __future__ import annotations

import argparse
import csv
import html
from pathlib import Path


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def as_float(row: dict[str, str], key: str) -> float:
    try:
        return float(row.get(key, "") or 0.0)
    except ValueError:
        return 0.0


def scale_points(rows: list[dict[str, str]], x0: int, y0: int, w: int, h: int, y_max: float) -> list[tuple[float, float]]:
    points = []
    for row in rows:
        x = x0 + w * as_float(row, "prediction_coverage")
        y = y0 + h - h * min(as_float(row, "precision"), y_max) / y_max
        points.append((x, y))
    return points


def polyline(points: list[tuple[float, float]], color: str) -> str:
    encoded = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{encoded}" fill="none" stroke="{color}" stroke-width="3"/>'


def write_svg(
    ordinary: list[dict[str, str]],
    lodo: list[dict[str, str]],
    output: Path,
    title: str,
    subtitle: str,
    ordinary_label: str,
    lodo_label: str,
    footer: str,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    width = 980
    height = 560
    x0 = 96
    y0 = 104
    w = 760
    h = 340
    y_max = max(
        [as_float(row, "precision") for row in ordinary + lodo] + [0.25]
    )
    y_max = max(0.25, min(1.0, y_max * 1.15))
    ordinary_points = scale_points(ordinary, x0, y0, w, h, y_max)
    lodo_points = scale_points(lodo, x0, y0, w, h, y_max)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="32" y="42" font-family="Arial" font-size="22" font-weight="700">{html.escape(title)}</text>',
        f'<text x="32" y="70" font-family="Arial" font-size="14" fill="#555">{html.escape(subtitle)}</text>',
        f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="#fafafa" stroke="#d0d0d0"/>',
    ]
    for tick in range(0, 6):
        x = x0 + w * tick / 5
        lines.append(f'<line x1="{x:.1f}" y1="{y0}" x2="{x:.1f}" y2="{y0 + h}" stroke="#e8e8e8"/>')
        lines.append(
            f'<text x="{x - 10:.1f}" y="{y0 + h + 24}" font-family="Arial" font-size="12" fill="#555">{tick / 5:.1f}</text>'
        )
    for tick in range(0, 6):
        value = y_max * tick / 5
        y = y0 + h - h * tick / 5
        lines.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x0 + w}" y2="{y:.1f}" stroke="#e8e8e8"/>')
        lines.append(
            f'<text x="{x0 - 58}" y="{y + 4:.1f}" font-family="Arial" font-size="12" fill="#555">{value:.2f}</text>'
        )
    lines.append(polyline(ordinary_points, "#2f6f9f"))
    lines.append(polyline(lodo_points, "#b7652b"))
    for points, color in [(ordinary_points, "#2f6f9f"), (lodo_points, "#b7652b")]:
        for x, y in points:
            lines.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}"/>')
    lines.extend(
        [
            f'<text x="{x0 + w / 2 - 58:.1f}" y="{height - 60}" font-family="Arial" font-size="14" fill="#222">Prediction coverage</text>',
            f'<text x="24" y="{y0 + h / 2:.1f}" transform="rotate(-90 24,{y0 + h / 2:.1f})" font-family="Arial" font-size="14" fill="#222">Precision</text>',
            '<rect x="690" y="92" width="18" height="10" fill="#2f6f9f"/>',
            f'<text x="714" y="102" font-family="Arial" font-size="13" fill="#222">{html.escape(ordinary_label)}</text>',
            '<rect x="690" y="116" width="18" height="10" fill="#b7652b"/>',
            f'<text x="714" y="126" font-family="Arial" font-size="13" fill="#222">{html.escape(lodo_label)}</text>',
            f'<text x="32" y="506" font-family="Arial" font-size="13" fill="#666">{html.escape(footer)}</text>',
            "</svg>",
        ]
    )
    output.write_text("\n".join(lines), encoding="utf-8")


def write_markdown(ordinary: list[dict[str, str]], lodo: list[dict[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    by_threshold: dict[str, dict[str, str]] = {}
    for row in ordinary:
        by_threshold.setdefault(row["threshold"], {})["ordinary_precision"] = row["precision"]
        by_threshold.setdefault(row["threshold"], {})["ordinary_coverage"] = row["prediction_coverage"]
    for row in lodo:
        by_threshold.setdefault(row["threshold"], {})["lodo_precision"] = row["precision"]
        by_threshold.setdefault(row["threshold"], {})["lodo_coverage"] = row["prediction_coverage"]
    lines = [
        "# G3 Reliability Figure Inputs",
        "",
        "| Threshold | Ordinary coverage | Ordinary precision | LODO coverage | LODO precision |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for threshold in sorted(by_threshold, key=lambda value: float(value)):
        row = by_threshold[threshold]
        lines.append(
            "| {thr} | {oc} | {op} | {lc} | {lp} |".format(
                thr=threshold,
                oc=row.get("ordinary_coverage", ""),
                op=row.get("ordinary_precision", ""),
                lc=row.get("lodo_coverage", ""),
                lp=row.get("lodo_precision", ""),
            )
        )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Plot G3 ordinary-vs-LODO risk-coverage curves.")
    parser.add_argument("--ordinary-risk", default="data_processed/calibration/g3_timing_ordinary_risk_coverage.csv")
    parser.add_argument("--lodo-risk", default="data_processed/calibration/g3_timing_lodo_all_risk_coverage.csv")
    parser.add_argument("--svg", default="manuscript/figures/fig_g3_timing_risk_coverage.svg")
    parser.add_argument("--summary", default="manuscript/figures/fig_g3_timing_risk_coverage_inputs.md")
    parser.add_argument("--title", default="G3 timing pilot: risk-coverage curves")
    parser.add_argument(
        "--subtitle",
        default="Prediction-level precision versus retained prediction coverage. Timing-pilot evidence only.",
    )
    parser.add_argument("--ordinary-label", default="Ordinary timing pilot")
    parser.add_argument("--lodo-label", default="LODO timing pilot, pooled")
    parser.add_argument(
        "--footer",
        default="Boundary: thresholds are analysis probes; final thresholds require fixed G3 scale and target-journal reporting decisions.",
    )
    args = parser.parse_args()

    ordinary = read_rows(Path(args.ordinary_risk))
    lodo = read_rows(Path(args.lodo_risk))
    write_svg(
        ordinary,
        lodo,
        Path(args.svg),
        args.title,
        args.subtitle,
        args.ordinary_label,
        args.lodo_label,
        args.footer,
    )
    write_markdown(ordinary, lodo, Path(args.summary))
    print(f"Wrote {args.svg} and {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
