from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def style() -> None:
    plt.rcParams.update(
        {
            "font.family": "Arial",
            "font.size": 9,
            "axes.titlesize": 11,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "svg.fonttype": "none",
        }
    )


def save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, format="svg", bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {path.relative_to(project_root())}")


def make_g4a_lodo_figure(root: Path, fig_dir: Path) -> None:
    domain = pd.read_csv(root / "data_processed/g4/g4a_multiseed_lodo_by_domain_summary.csv")
    ordinary = pd.read_csv(root / "data_processed/g4/g4a_multiseed_ordinary_summary.csv").iloc[0]
    domain = domain.sort_values("mAP50_B_mean", ascending=True)

    fig, ax = plt.subplots(figsize=(6.6, 3.6))
    y = range(len(domain))
    ax.barh(y, domain["mAP50_B_mean"], xerr=domain["mAP50_B_std"], color="#4e79a7", alpha=0.9)
    ax.axvline(float(ordinary["mAP50_B_mean"]), color="#d62728", linewidth=1.2, linestyle="--", label="ordinary mean")
    ax.set_yticks(list(y), domain["heldout_domain"])
    ax.set_xlabel("mAP50")
    ax.set_title("G4a YOLOv8n three-seed LODO audit surface")
    ax.grid(axis="x", color="#dddddd", linewidth=0.6)
    ax.legend(loc="lower right", frameon=False)
    ax.text(
        0.99,
        0.02,
        "Bars: mean across seeds; whiskers: seed std",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        color="#555555",
        fontsize=8,
    )
    save(fig, fig_dir / "fig09_g4a_multiseed_lodo_map50.svg")


def make_g4a_image_coverage_figure(root: Path, fig_dir: Path) -> None:
    image = pd.read_csv(root / "data_processed/g4/g4a_multiseed_image_level_thresholds.csv")
    keep = image[image["threshold"].isin([0.05, 0.1, 0.2, 0.5])].copy()
    grouped = (
        keep.groupby(["split", "threshold"], as_index=False)
        .agg(
            image_review_coverage_mean=("image_review_coverage", "mean"),
            image_review_coverage_std=("image_review_coverage", "std"),
            gt_image_miss_proxy_mean=("gt_image_miss_proxy", "mean"),
            gt_image_miss_proxy_std=("gt_image_miss_proxy", "std"),
            selected_image_tp_rate_mean=("selected_image_tp_rate", "mean"),
        )
        .sort_values(["split", "threshold"])
    )
    grouped.to_csv(root / "data_processed/g4/g4a_multiseed_image_level_threshold_summary.csv", index=False)

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.2), sharex=True)
    colors = {"ordinary": "#4e79a7", "lodo_all": "#f28e2b"}
    labels = {"ordinary": "ordinary", "lodo_all": "pooled LODO"}
    for split, group in grouped.groupby("split"):
        axes[0].errorbar(
            group["threshold"],
            group["image_review_coverage_mean"],
            yerr=group["image_review_coverage_std"].fillna(0),
            marker="o",
            color=colors.get(split, "#333333"),
            label=labels.get(split, split),
            linewidth=1.5,
        )
        axes[1].errorbar(
            group["threshold"],
            group["gt_image_miss_proxy_mean"],
            yerr=group["gt_image_miss_proxy_std"].fillna(0),
            marker="o",
            color=colors.get(split, "#333333"),
            label=labels.get(split, split),
            linewidth=1.5,
        )
    axes[0].set_title("Images sent to review")
    axes[0].set_ylabel("image review coverage")
    axes[1].set_title("Residual missed GT-positive images")
    axes[1].set_ylabel("GT-image miss proxy")
    for ax in axes:
        ax.set_xscale("log")
        ax.set_xlabel("confidence threshold")
        ax.set_xticks([0.05, 0.1, 0.2, 0.5])
        ax.get_xaxis().set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.2f}"))
        ax.grid(axis="both", color="#dddddd", linewidth=0.6)
        ax.set_ylim(0, 1.02)
    axes[0].legend(loc="best", frameon=False)
    fig.suptitle("G4a image-level threshold audit across three YOLOv8n seeds", y=1.02, fontsize=11)
    save(fig, fig_dir / "fig10_g4a_image_level_thresholds.svg")


def make_g4b_bridge_figure(root: Path, fig_dir: Path) -> None:
    summary_path = root / "data_processed/g4/g4b_bridge_setting_summary.csv"
    if summary_path.exists():
        bridge = pd.read_csv(summary_path)
        fig, ax = plt.subplots(figsize=(5.8, 3.2))
        labels = ["YOLOv8n 320px 4ep", "YOLOv8s 640px 8ep"]
        x = [0, 1]
        width = 0.34
        for offset, setting, color in [(-width / 2, "ordinary", "#4e79a7"), (width / 2, "LODO mean", "#f28e2b")]:
            vals = []
            errs = []
            for label in labels:
                row = bridge[(bridge["model_label"] == label) & (bridge["setting"] == setting)].iloc[0]
                vals.append(float(row["mAP50_B_mean"]))
                errs.append(float(row.get("mAP50_B_std", 0.0)))
            ax.bar([v + offset for v in x], vals, yerr=errs, width=width, label=setting, color=color, capsize=3)
        ax.set_xticks(x, labels)
        ax.set_ylabel("mAP50")
        ax.set_title("G4b detector-capacity bridge across completed seeds")
        ax.grid(axis="y", color="#dddddd", linewidth=0.6)
        ax.legend(frameon=False)
        ax.text(
            0.99,
            0.02,
            "Bars: seed mean; whiskers: seed std",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            color="#555555",
            fontsize=8,
        )
        save(fig, fig_dir / "fig11_g4b_yolov8n_vs_yolov8s_bridge.svg")
        return

    y8n_ord = root / "data_processed/yolo_g3_frozen_subset_ordinary_result.csv"
    y8n_lodo = root / "data_processed/yolo_g3_frozen_subset_lodo_results.csv"
    y8s_ord = root / "data_processed/g4/g4b_bridge_yolov8s_seed20260512_ordinary_result.csv"
    y8s_lodo = root / "data_processed/g4/g4b_bridge_yolov8s_seed20260512_lodo_results.csv"
    if not (y8s_ord.exists() and y8s_lodo.exists()):
        return

    rows = []
    for model_label, ordinary_path, lodo_path in [
        ("YOLOv8n 320px 4ep", y8n_ord, y8n_lodo),
        ("YOLOv8s 640px 8ep", y8s_ord, y8s_lodo),
    ]:
        ordinary = pd.read_csv(ordinary_path).iloc[0]
        lodo = pd.read_csv(lodo_path)
        rows.append({"model_label": model_label, "setting": "ordinary", "mAP50": ordinary["mAP50_B"]})
        rows.append({"model_label": model_label, "setting": "LODO mean", "mAP50": lodo["mAP50_B"].mean()})
    bridge = pd.DataFrame(rows)
    bridge.to_csv(root / "data_processed/g4/g4b_bridge_yolov8n_vs_yolov8s_summary.csv", index=False)

    fig, ax = plt.subplots(figsize=(5.8, 3.2))
    x = [0, 1]
    width = 0.34
    for offset, setting, color in [(-width / 2, "ordinary", "#4e79a7"), (width / 2, "LODO mean", "#f28e2b")]:
        vals = [float(bridge[(bridge["model_label"] == label) & (bridge["setting"] == setting)]["mAP50"].iloc[0]) for label in bridge["model_label"].unique()]
        ax.bar([v + offset for v in x], vals, width=width, label=setting, color=color)
    ax.set_xticks(x, list(bridge["model_label"].unique()))
    ax.set_ylabel("mAP50")
    ax.set_title("G4b detector-capacity bridge on the same seed")
    ax.grid(axis="y", color="#dddddd", linewidth=0.6)
    ax.legend(frameon=False)
    save(fig, fig_dir / "fig11_g4b_yolov8n_vs_yolov8s_bridge.svg")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create G4 manuscript SVG figures.")
    parser.add_argument("--fig-dir", default="manuscript/figures")
    args = parser.parse_args()
    root = project_root()
    style()
    fig_dir = root / args.fig_dir
    make_g4a_lodo_figure(root, fig_dir)
    make_g4a_image_coverage_figure(root, fig_dir)
    make_g4b_bridge_figure(root, fig_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
