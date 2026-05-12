from __future__ import annotations

import argparse
import csv
import html
from pathlib import Path


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def as_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def write_matrix_svg(
    ordinary: dict[str, str],
    lodo_rows: list[dict[str, str]],
    output: Path,
    title: str,
    subtitle: str,
    detail: str,
    source_note: str,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "label": "Ordinary mixed-domain",
            "mAP50_B": ordinary.get("mAP50_B", "0"),
            "mAP50_95_B": ordinary.get("mAP50_95_B", "0"),
            "recall_B": ordinary.get("recall_B", "0"),
            "kind": "ordinary",
        }
    ]
    for row in lodo_rows:
        rows.append(
            {
                "label": "LODO " + row.get("heldout_domain", "unknown"),
                "mAP50_B": row.get("mAP50_B", "0"),
                "mAP50_95_B": row.get("mAP50_95_B", "0"),
                "recall_B": row.get("recall_B", "0"),
                "kind": "lodo",
            }
        )
    metrics = [
        ("mAP50_B", "mAP50", "#4f7f76"),
        ("mAP50_95_B", "mAP50-95", "#9b6a3d"),
        ("recall_B", "Recall", "#7d5f9f"),
    ]
    width = 1180
    left = 230
    top = 126
    row_h = 48
    panel_w = 250
    panel_gap = 32
    height = top + len(rows) * row_h + 88
    max_by_metric = {
        key: max([as_float(row[key]) for row in rows] or [1.0]) or 1.0 for key, _, _ in metrics
    }
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="32" y="38" font-family="Arial" font-size="22" font-weight="700">{html.escape(title)}</text>',
        f'<text x="32" y="66" font-family="Arial" font-size="14" fill="#555">{html.escape(subtitle)}</text>',
        f'<text x="32" y="88" font-family="Arial" font-size="13" fill="#777">{html.escape(detail)}</text>',
    ]
    for j, (_, label, _) in enumerate(metrics):
        x = left + j * (panel_w + panel_gap)
        lines.append(
            f'<text x="{x}" y="114" font-family="Arial" font-size="14" font-weight="700" fill="#222">{html.escape(label)}</text>'
        )
        lines.append(f'<line x1="{x}" x2="{x + panel_w}" y1="122" y2="122" stroke="#ddd"/>')
    for i, row in enumerate(rows):
        y = top + i * row_h
        label = row["label"]
        fill = "#111" if row["kind"] == "ordinary" else "#333"
        lines.append(f'<text x="32" y="{y + 25}" font-family="Arial" font-size="13" fill="{fill}">{html.escape(label)}</text>')
        for j, (key, _, color) in enumerate(metrics):
            x = left + j * (panel_w + panel_gap)
            value = as_float(row[key])
            bar_w = max(1, int((panel_w - 62) * value / max_by_metric[key])) if value > 0 else 0
            bg = "#eef2f1" if row["kind"] == "ordinary" else "#f4f4f4"
            lines.append(f'<rect x="{x}" y="{y + 8}" width="{panel_w - 62}" height="22" fill="{bg}"/>')
            if bar_w:
                lines.append(f'<rect x="{x}" y="{y + 8}" width="{bar_w}" height="22" fill="{color}"/>')
            lines.append(f'<text x="{x + panel_w - 54}" y="{y + 24}" font-family="Arial" font-size="13" fill="#222">{value:.4f}</text>')
    lines.extend(
        [
            f'<text x="32" y="{height - 36}" font-family="Arial" font-size="13" fill="#666">{html.escape(source_note)}</text>',
            "</svg>",
        ]
    )
    output.write_text("\n".join(lines), encoding="utf-8")


def write_risk_svg(
    ordinary_rows: list[dict[str, str]],
    norway_rows: list[dict[str, str]],
    output: Path,
    title: str,
    subtitle: str,
    ordinary_label: str,
    lodo_label: str,
    footer: str,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    width = 1180
    height = 520
    left = 82
    top = 86
    plot_w = 440
    plot_h = 300
    gap = 86
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="32" y="38" font-family="Arial" font-size="22" font-weight="700">{html.escape(title)}</text>',
        f'<text x="32" y="66" font-family="Arial" font-size="14" fill="#555">{html.escape(subtitle)}</text>',
    ]

    def add_panel(x0: int, y0: int, rows: list[dict[str, str]], title: str) -> None:
        lines.append(f'<text x="{x0}" y="{y0 - 18}" font-family="Arial" font-size="15" font-weight="700">{html.escape(title)}</text>')
        lines.append(f'<rect x="{x0}" y="{y0}" width="{plot_w}" height="{plot_h}" fill="#fafafa" stroke="#ddd"/>')
        for k in range(6):
            gx = x0 + k * plot_w / 5
            gy = y0 + k * plot_h / 5
            lines.append(f'<line x1="{gx:.1f}" x2="{gx:.1f}" y1="{y0}" y2="{y0 + plot_h}" stroke="#eee"/>')
            lines.append(f'<line x1="{x0}" x2="{x0 + plot_w}" y1="{gy:.1f}" y2="{gy:.1f}" stroke="#eee"/>')
        lines.append(f'<text x="{x0}" y="{y0 + plot_h + 34}" font-family="Arial" font-size="12" fill="#555">Prediction coverage</text>')
        lines.append(f'<text x="{x0 - 48}" y="{y0 + 12}" font-family="Arial" font-size="12" fill="#555">Value</text>')
        series = [
            ("precision", "#4f7f76", "Precision"),
            ("gt_recall_after_acceptance", "#9b6a3d", "GT recall"),
        ]
        for key, color, label in series:
            points = []
            for row in rows:
                cov = as_float(row.get("prediction_coverage", "0"))
                val = as_float(row.get(key, "0"))
                px = x0 + cov * plot_w
                py = y0 + plot_h - val * plot_h
                points.append((px, py))
            if len(points) > 1:
                path = " ".join(("M" if idx == 0 else "L") + f" {px:.1f} {py:.1f}" for idx, (px, py) in enumerate(points))
                lines.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="3"/>')
            for px, py in points:
                lines.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3" fill="{color}"/>')
            legend_y = y0 + plot_h + 58 + (0 if key == "precision" else 20)
            lines.append(f'<rect x="{x0 + 250}" y="{legend_y - 10}" width="12" height="12" fill="{color}"/>')
            lines.append(f'<text x="{x0 + 268}" y="{legend_y}" font-family="Arial" font-size="12" fill="#333">{html.escape(label)}</text>')

    add_panel(left, top, ordinary_rows, ordinary_label)
    add_panel(left + plot_w + gap, top, norway_rows, lodo_label)
    lines.extend(
        [
            f'<text x="32" y="474" font-family="Arial" font-size="13" fill="#666">{html.escape(footer)}</text>',
            "</svg>",
        ]
    )
    output.write_text("\n".join(lines), encoding="utf-8")


def write_inputs_summary(
    ordinary: dict[str, str],
    lodo_rows: list[dict[str, str]],
    ordinary_risk: list[dict[str, str]],
    norway_risk: list[dict[str, str]],
    output: Path,
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# G3 Figure Inputs",
        "",
        "## Ordinary vs LODO Matrix",
        "",
        "| Split | mAP50 | mAP50-95 | Recall |",
        "|---|---:|---:|---:|",
        "| Ordinary mixed-domain | {map50:.4f} | {map5095:.4f} | {recall:.4f} |".format(
            map50=as_float(ordinary.get("mAP50_B", "")),
            map5095=as_float(ordinary.get("mAP50_95_B", "")),
            recall=as_float(ordinary.get("recall_B", "")),
        ),
    ]
    for row in lodo_rows:
        lines.append(
            "| LODO {domain} | {map50:.4f} | {map5095:.4f} | {recall:.4f} |".format(
                domain=row.get("heldout_domain", "unknown"),
                map50=as_float(row.get("mAP50_B", "")),
                map5095=as_float(row.get("mAP50_95_B", "")),
                recall=as_float(row.get("recall_B", "")),
            )
        )
    lines.extend(
        [
            "",
            "## Risk-Coverage Sources",
            "",
            f"- Ordinary rows: {len(ordinary_risk)}",
            f"- Norway held-out rows: {len(norway_risk)}",
        ]
    )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Plot G3 timing pilot matrix and risk-coverage figures.")
    parser.add_argument("--ordinary", default="data_processed/yolo_g3_timing_ordinary_result.csv")
    parser.add_argument("--lodo", default="data_processed/yolo_g3_timing_lodo_results.csv")
    parser.add_argument("--ordinary-risk", default="data_processed/calibration/g3_timing_ordinary_risk_coverage.csv")
    parser.add_argument("--norway-risk", default="data_processed/calibration/g3_timing_lodo_heldout_Norway_risk_coverage.csv")
    parser.add_argument("--matrix-svg", default="manuscript/figures/fig04_g3_ordinary_vs_lodo_timing.svg")
    parser.add_argument("--risk-svg", default="manuscript/figures/fig05_g3_risk_coverage_timing.svg")
    parser.add_argument("--summary", default="manuscript/figures/fig04_fig05_g3_timing_inputs.md")
    parser.add_argument("--matrix-title", default="G3 timing pilot: ordinary vs held-out-domain transfer")
    parser.add_argument(
        "--matrix-subtitle",
        default="YOLOv8n pretrained, 2 CPU epochs, 320 px. Subset-scale timing evidence, not final paper performance.",
    )
    parser.add_argument(
        "--matrix-detail",
        default="Ordinary: 160 train and 68 validation images/domain. LODO: 160 train images/domain from six source domains, 68 validation images from held-out domain.",
    )
    parser.add_argument(
        "--matrix-source-note",
        default="Source: data_processed/yolo_g3_timing_ordinary_result.csv and data_processed/yolo_g3_timing_lodo_results.csv.",
    )
    parser.add_argument("--risk-title", default="G3 timing pilot: confidence threshold tradeoffs")
    parser.add_argument(
        "--risk-subtitle",
        default="Prediction-level risk-coverage curves from exported TP/FP/FN tables. Pilot-only evidence.",
    )
    parser.add_argument("--risk-ordinary-label", default="Ordinary mixed-domain timing")
    parser.add_argument("--risk-lodo-label", default="LODO held-out Norway timing")
    parser.add_argument(
        "--risk-footer",
        default="Raising confidence thresholds improves accepted-prediction precision but reduces coverage and ground-truth recall. This supports an audit/tradeoff framing, not an operational threshold claim.",
    )
    args = parser.parse_args()

    ordinary_rows = read_rows(Path(args.ordinary))
    if not ordinary_rows:
        raise ValueError(f"No ordinary rows in {args.ordinary}")
    ordinary = ordinary_rows[0]
    lodo = read_rows(Path(args.lodo))
    ordinary_risk = read_rows(Path(args.ordinary_risk))
    norway_risk = read_rows(Path(args.norway_risk))
    write_matrix_svg(
        ordinary,
        lodo,
        Path(args.matrix_svg),
        args.matrix_title,
        args.matrix_subtitle,
        args.matrix_detail,
        args.matrix_source_note,
    )
    write_risk_svg(
        ordinary_risk,
        norway_risk,
        Path(args.risk_svg),
        args.risk_title,
        args.risk_subtitle,
        args.risk_ordinary_label,
        args.risk_lodo_label,
        args.risk_footer,
    )
    write_inputs_summary(ordinary, lodo, ordinary_risk, norway_risk, Path(args.summary))
    print(f"Wrote {args.matrix_svg}")
    print(f"Wrote {args.risk_svg}")
    print(f"Wrote {args.summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
