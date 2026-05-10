#!/usr/bin/env python3
"""Visualize ablation.tex with grouped relative bars and absolute-value annotations."""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np

BENCHMARKS = ["Egoschema", "EgoLifeQA", "EgoR1Bench"]
# Only plot the first two metrics as requested.
PLOT_METRICS = [
    (0, "alpha_c", r"$\overline{\alpha^c}$", "Option-question Accuracy"),
    (1, "alpha_e_E", r"$\overline{\alpha^e_E}$", "Closest Option from Encoding"),
]

TOTAL_METRICS = 3
EXPECTED_VALUE_COUNT = len(BENCHMARKS) * TOTAL_METRICS
BENCHMARK_CENTER_GAP = 1.2
TITLE_FONT_SIZE = 18
LEGEND_FONT_SIZE = 23

# Relative rows are grouped as: first 3, then 1, then 2, then 2, then 1.
GROUP_SIZES = [3, 1, 2, 2, 1]
GROUP_NAMES = [
    "Core Components",
    "w/o Context",
    "k Variants",
    "μ Variants",
    "Text Encoder",
]
GROUP_CMAPS = ["Blues", "Purples", "Greens", "Oranges", "Greys"]


def clean_method_name(raw: str) -> str:
    """Remove LaTeX marks while keeping readable method names."""
    text = raw.strip()
    text = text.replace(r"$\mu$", "μ")
    text = re.sub(r"~?\\cite\{[^{}]*\}", "", text)
    text = re.sub(r"\$\^\{[^{}]*\}\$", "", text)
    text = re.sub(r"\$[^$]*\$", "", text)
    text = re.sub(r"\\textbf\{([^{}]*)\}", r"\1", text)
    text = text.replace("{", "").replace("}", "")
    text = re.sub(r"\\hline", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    # Keep μ as Greek symbol in legend labels.
    text = re.sub(r"\bmu\b", "μ", text)
    return text


def extract_cell_value(cell: str) -> float:
    """Extract a numeric value from a LaTeX cell."""
    clean = re.sub(r"\\cellcolor\{[^{}]*\}", "", cell)
    clean = re.sub(r"\\[a-zA-Z]+\{[^{}]*\}", "", clean)
    clean = clean.replace("$", " ").strip()

    match = re.search(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?", clean)
    if not match:
        raise ValueError(f"No numeric value in cell: {cell}")
    return float(match.group(0))


def parse_ablation_table(tex_path: Path) -> Tuple[np.ndarray, List[str], np.ndarray]:
    """Return baseline matrix [3,3], ablation names, and relative matrix [N,3,3]."""
    names: List[str] = []
    rows: List[List[float]] = []

    lines = tex_path.read_text(encoding="utf-8").splitlines()
    in_tabular = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(r"\begin{tabular}"):
            in_tabular = True
            continue
        if stripped.startswith(r"\end{tabular}"):
            in_tabular = False
            continue
        if not in_tabular:
            continue

        no_comment = line.split("%", 1)[0].strip()
        if not no_comment or "&" not in no_comment or r"\\" not in no_comment:
            continue

        row_body = re.sub(r"\\\\.*$", "", no_comment).strip()
        cells = [part.strip() for part in row_body.split("&")]
        if len(cells) != 1 + EXPECTED_VALUE_COUNT:
            continue

        name = clean_method_name(cells[0])
        if not name or name in {"Benchmark", "Metric", "Unit"}:
            continue

        values: List[float] = []
        ok = True
        for cell in cells[1:]:
            try:
                values.append(extract_cell_value(cell))
            except ValueError:
                ok = False
                break

        # Skip helper rows like "mu=8, k=6" that have no numeric data.
        if not ok or len(values) != EXPECTED_VALUE_COUNT:
            continue

        names.append(name)
        rows.append(values)

    if not rows:
        raise RuntimeError(f"No data rows parsed from {tex_path}")

    data = np.asarray(rows, dtype=float).reshape(len(rows), len(BENCHMARKS), TOTAL_METRICS)

    baseline_idx = None
    for i, name in enumerate(names):
        if "EgoVidMem" in name:
            baseline_idx = i
            break
    if baseline_idx is None:
        raise RuntimeError("Cannot find baseline row 'EgoVidMem' in ablation.tex")

    baseline = data[baseline_idx]
    ablation_names = names[baseline_idx + 1 :]
    ablation_rel = data[baseline_idx + 1 :]

    if len(ablation_names) != sum(GROUP_SIZES):
        raise RuntimeError(
            f"Expected {sum(GROUP_SIZES)} ablation rows, got {len(ablation_names)}."
        )

    return baseline, ablation_names, ablation_rel


def build_offsets(
    n_methods: int,
    within_step: float = 1.25,
    between_multiplier: float = 1.2,
    target_span: float = 0.90,
) -> Tuple[np.ndarray, float, np.ndarray]:
    """Build method offsets with inter-group distance = 1.2x intra-group distance."""
    positions: List[float] = []
    group_ids: List[int] = []
    cursor = 0.0
    between_extra = within_step * max(0.0, between_multiplier - 1.0)

    idx = 0
    for gid, size in enumerate(GROUP_SIZES):
        for _ in range(size):
            if idx >= n_methods:
                break
            positions.append(cursor)
            group_ids.append(gid)
            cursor += within_step
            idx += 1
        if gid < len(GROUP_SIZES) - 1:
            cursor += between_extra

    pos = np.asarray(positions, dtype=float)
    pos = pos - np.mean(pos)

    raw_span = float(np.max(pos) - np.min(pos)) if len(pos) > 1 else 1.0
    scale = target_span / raw_span
    offsets = pos * scale
    bar_width = within_step * scale * 0.90

    return offsets, bar_width, np.asarray(group_ids, dtype=int)


def build_colors(group_ids: np.ndarray) -> List[Tuple[float, float, float, float]]:
    """Assign one colormap family to each ablation group."""
    colors: List[Tuple[float, float, float, float]] = []
    for gid in group_ids:
        count = int(np.sum(group_ids == gid))
        rank = int(np.sum(group_ids[: len(colors)] == gid))
        if count <= 1:
            t = 0.62
        else:
            t = 0.42 + 0.46 * (rank / (count - 1))
        cmap = plt.get_cmap(GROUP_CMAPS[gid])
        colors.append(cmap(t))
    return colors


def text_color_for_bar(rgba: Tuple[float, float, float, float]) -> str:
    """Use white text on dark bars and black text on light bars."""
    r, g, b = rgba[:3]
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return "#ffffff" if luminance < 0.5 else "#111111"


def format_sig(value: float, sig: int = 3, omit_leading_zero: bool = True) -> str:
    """Format with significant digits, optional no-leading-zero for decimals."""
    if value == 0:
        return "0.00"

    exponent = int(math.floor(math.log10(abs(value))))
    decimals = sig - 1 - exponent

    if decimals > 0:
        text = f"{value:.{decimals}f}"
    else:
        text = f"{round(value, -decimals):.0f}"

    if omit_leading_zero and 0 < value < 1 and text.startswith("0"):
        text = text[1:]
    if omit_leading_zero and -1 < value < 0 and text.startswith("-0"):
        text = "-" + text[2:]
    return text


def format_rel(value: float) -> str:
    """Relative value text with explicit sign for nonzero values."""
    if abs(value) < 1e-12:
        return "0.00"
    body = format_sig(abs(value), sig=3, omit_leading_zero=True)
    return ("+" if value > 0 else "-") + body


def plot_metric(
    baseline: np.ndarray,
    ablation_names: List[str],
    ablation_rel: np.ndarray,
    metric_idx: int,
    metric_key: str,
    metric_symbol: str,
    metric_name: str,
    out_dir: Path,
) -> Path:
    """Plot one metric using absolute bars with relative arrows to baseline."""
    n_methods = len(ablation_names)
    offsets, bar_width, group_ids = build_offsets(n_methods)
    colors = build_colors(group_ids)

    base_vals = baseline[:, metric_idx]
    rel_vals = ablation_rel[:, :, metric_idx]
    abs_vals = base_vals[None, :] + rel_vals

    x_centers = np.arange(len(BENCHMARKS), dtype=float) * BENCHMARK_CENTER_GAP

    min_abs = float(np.min(abs_vals))
    max_abs = float(np.max(abs_vals))
    max_base = float(np.max(base_vals))
    top_ref = max(max_abs, max_base)
    span = max(1.0, top_ref - min_abs)
    lower = max(0.0, min_abs - span * 0.22)
    upper = top_ref + span * 0.2
    abs_label_offset = span * 0.045

    fig, ax = plt.subplots(figsize=(16, 6.8))

    for i, name in enumerate(ablation_names):
        xs = x_centers + offsets[i]
        ys = abs_vals[i]
        bars = ax.bar(xs, ys, width=bar_width, color=colors[i], edgecolor="white", linewidth=0.5, label=name)

        for j, bar in enumerate(bars):
            abs_y = float(ys[j])
            base_y = float(base_vals[j])
            delta = float(rel_vals[i, j])
            x = bar.get_x() + bar.get_width() / 2

            # Arrow from full-version baseline to the ablation absolute value.
            if abs(delta) > 1e-6:
                ax.annotate(
                    "",
                    xy=(x, abs_y),
                    xytext=(x, base_y),
                    arrowprops=dict(arrowstyle="<->", lw=0.85, color="#444444", shrinkA=0, shrinkB=0),
                    zorder=4,
                )

            y_mid = (abs_y + base_y) / 2.0 if abs(delta) > 1e-6 else base_y - span * 0.03
            ax.text(
                x,
                y_mid,
                format_rel(delta),
                ha="center",
                va="center",
                fontsize=8.6,
                rotation=90,
                color="#303030",
                zorder=5,
            )

            # Absolute value label: slightly below the bar top edge.
            y_abs = max(abs_y - abs_label_offset, abs_y * 0.55)
            abs_text_color = text_color_for_bar(bar.get_facecolor())

            ax.text(
                x,
                y_abs,
                format_sig(abs_vals[i, j], sig=3, omit_leading_zero=True),
                ha="center",
                va="top",
                fontsize=18,
                rotation=90,
                color=abs_text_color,
                fontweight="bold",
                zorder=6,
            )

    # Full-version reference line for each benchmark.
    cluster_left = float(np.min(offsets) - bar_width * 0.5)
    cluster_right = float(np.max(offsets) + bar_width * 0.5)
    for b_idx, c in enumerate(x_centers):
        y_base = float(base_vals[b_idx])
        ax.hlines(
            y_base,
            c + cluster_left,
            c + cluster_right,
            colors="#111111",
            linewidth=1.5,
            zorder=3,
        )

    ax.text(
        x_centers[0] + cluster_left,
        upper - span * 0.04,
        "Full version baseline",
        fontsize=11,
        color="#111111",
        ha="left",
        va="top",
    )

    # Show full-version absolute numbers per benchmark near baseline lines.
    for b_idx, bench in enumerate(BENCHMARKS):
        ax.text(
            x_centers[b_idx],
            float(base_vals[b_idx]) + span * 0.02,
            f"Full={format_sig(base_vals[b_idx], sig=3, omit_leading_zero=True)}",
            ha="center",
            va="bottom",
            fontsize=16,
            color="#111111",
            fontweight="bold",
        )

    ax.set_xticks(x_centers)
    ax.set_xticklabels(BENCHMARKS, fontsize=18, fontweight="bold")
    # ax.set_ylabel("Absolute value", fontsize=13)
    # ax.set_title(
    #     f"Ablation on {metric_symbol} {metric_name} (bars=absolute, arrows=relative change)",
    #     fontsize=TITLE_FONT_SIZE,
    # )
    ax.set_ylim(lower, upper)
    ax.grid(axis="y", linestyle="--", alpha=0.25)

    # Add group separators inside each benchmark cluster for readability.
    boundary_indices = np.cumsum(GROUP_SIZES)[:-1]
    for c in x_centers:
        for idx in boundary_indices:
            left = offsets[idx - 1]
            right = offsets[idx]
            sep_x = c + (left + right) / 2.0
            ax.vlines(sep_x, lower, upper, colors="#bbbbbb", linestyles=":", linewidth=0.7, alpha=0.5)

    # Put all 9 ablation methods in a 3x3 legend at the upper-right area.
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(
        handles,
        labels,
        loc="upper right",
        bbox_to_anchor=(0.995, 0.995),
        ncol=3,
        frameon=True,
        framealpha=0.92,
        edgecolor="#dddddd",
        fontsize=LEGEND_FONT_SIZE,
        columnspacing=1.1,
        handletextpad=0.5,
        borderpad=0.5,
        labelspacing=0.5,
    )

    out_path = out_dir / f"ablation_{metric_key}.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot ablation bars from ablation.tex")
    parser.add_argument("--tex", type=Path, default=Path("ablation.tex"), help="Path to ablation.tex")
    parser.add_argument("--outdir", type=Path, default=Path("."), help="Output directory")
    args = parser.parse_args()

    tex_path = args.tex.resolve()
    out_dir = args.outdir.resolve()

    if not tex_path.exists():
        raise FileNotFoundError(f"Cannot find tex file: {tex_path}")

    out_dir.mkdir(parents=True, exist_ok=True)
    baseline, ablation_names, ablation_rel = parse_ablation_table(tex_path)

    saved: List[Path] = []
    for metric_idx, metric_key, metric_symbol, metric_name in PLOT_METRICS:
        saved.append(
            plot_metric(
                baseline=baseline,
                ablation_names=ablation_names,
                ablation_rel=ablation_rel,
                metric_idx=metric_idx,
                metric_key=metric_key,
                metric_symbol=metric_symbol,
                metric_name=metric_name,
                out_dir=out_dir,
            )
        )

    print(f"Baseline row parsed: {format_sig(baseline[0, 0])} / {format_sig(baseline[0, 1])} / {format_sig(baseline[0, 2])}")
    print(f"Ablation methods: {len(ablation_names)}")
    for path in saved:
        print(path)


if __name__ == "__main__":
    main()
