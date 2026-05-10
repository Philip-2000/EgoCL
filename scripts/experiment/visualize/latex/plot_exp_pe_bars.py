#!/usr/bin/env python3
"""Draw grouped bar charts from exp_pe.tex."""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path
from typing import List, Tuple

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np

BENCHMARKS = ["Egoschema", "EgoLifeQA", "EgoR1Bench"]
METRICS = [
    ("delta", r"$\overline{\delta}$", "Delay", "scaled s"),
    ("delta_tau", r"$\overline{\delta_\tau}$", "Delay Rate", "scaled s"),
    ("delta_tau_m", r"$\overline{\delta^m_\tau}$", "Memorize Time Rate", "--"),
    ("eta_MV", r"$\overline{\eta^{\mathcal{M}}_{\mathcal{V}}}$", "Compression Rate", "--"),
]

EXPECTED_VALUE_COUNT = len(BENCHMARKS) * len(METRICS)
TITLE_FONT_SIZE = 17
LEGEND_FONT_SIZE = 14


def clean_method_name(raw: str) -> str:
    """Remove LaTeX marks, keep readable method names."""
    text = raw.strip()
    text = re.sub(r"~?\\cite\{[^{}]*\}", "", text)
    text = re.sub(r"\$[^$]*\$", "", text)
    text = re.sub(r"\\textbf\{([^{}]*)\}", r"\1", text)
    text = text.replace("{", "").replace("}", "")
    text = re.sub(r"\\hline", "", text)
    text = re.sub(r"\\multicolumn\{[^{}]*\}\{[^{}]*\}\{[^{}]*\}", "", text)
    text = re.sub(r"\\fontsize\{[^{}]*\}\{[^{}]*\}\\selectfont", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_cell_value(cell: str) -> float:
    """Extract numeric value from a LaTeX cell; return NaN for missing markers."""
    clean = re.sub(r"\\cellcolor\{[^{}]*\}", "", cell)
    clean = re.sub(r"\\[a-zA-Z]+\{[^{}]*\}", "", clean)
    clean = clean.replace("$", " ").strip()

    if re.fullmatch(r"-+", clean):
        return float("nan")

    match = re.search(r"[-+]?(?:\d*\.\d+|\d+)", clean)
    if not match:
        raise ValueError(f"No numeric value in cell: {cell}")
    return float(match.group(0))


def parse_exp_pe_table(tex_path: Path) -> Tuple[List[str], np.ndarray]:
    """Parse method rows into names and a score matrix [N, 3, 4]."""
    methods: List[str] = []
    rows: List[List[float]] = []

    lines = tex_path.read_text(encoding="utf-8").splitlines()
    in_tabular = False
    pending_prefix = ""
    row_buffer = ""

    def consume_row(raw_row: str) -> None:
        row_body = re.sub(r"\\\\.*$", "", raw_row).strip()
        if not row_body:
            return

        cells = [part.strip() for part in row_body.split("&")]
        if len(cells) != 1 + EXPECTED_VALUE_COUNT:
            return

        method = clean_method_name(cells[0])
        if not method or method in {"Benchmark", "Metric", "Unit"}:
            return

        values: List[float] = []
        ok = True
        for cell in cells[1:]:
            try:
                values.append(extract_cell_value(cell))
            except ValueError:
                ok = False
                break

        if not ok or len(values) != EXPECTED_VALUE_COUNT:
            return

        methods.append(method)
        rows.append(values)

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
        if not no_comment:
            continue

        if row_buffer:
            row_buffer += " " + no_comment
            if r"\\" in no_comment:
                consume_row(row_buffer)
                row_buffer = ""
                pending_prefix = ""
            continue

        if "&" in no_comment:
            if pending_prefix:
                row_buffer = pending_prefix + " " + no_comment
                pending_prefix = ""
            else:
                row_buffer = no_comment

            if r"\\" in no_comment:
                consume_row(row_buffer)
                row_buffer = ""
            continue

        if no_comment.startswith(r"\hline"):
            continue

        pending_prefix = no_comment

    if not rows:
        raise RuntimeError(f"No data rows parsed from {tex_path}")

    score_matrix = np.asarray(rows, dtype=float).reshape(len(rows), len(BENCHMARKS), len(METRICS))
    return methods, score_matrix


def build_method_colors(methods: List[str]) -> List[Tuple[float, float, float, float]]:
    """Use stronger pink contrast; EgoVidMem is pale yellow; Ego-R1 is averaged color."""
    if not methods:
        return []

    pink_palette = ["#fde8f0", "#f6bccf", "#ea8bab"]
    pink_rgba = [np.array(mcolors.to_rgba(c), dtype=float) for c in pink_palette]
    yellow = mcolors.to_rgba("#f6e6a6")

    colors: List[Tuple[float, float, float, float] | None] = [None] * len(methods)
    pink_rank = 0
    ego_r1_idx = None

    for i, method in enumerate(methods):
        if "EgoVidMem" in method:
            colors[i] = yellow
        elif "Ego-R1" in method:
            ego_r1_idx = i
        else:
            colors[i] = tuple(pink_rgba[min(pink_rank, len(pink_rgba) - 1)])
            pink_rank += 1

    if ego_r1_idx is not None:
        if len(methods) >= 3 and colors[0] is not None and colors[2] is not None:
            avg = (np.array(colors[0], dtype=float) + np.array(colors[2], dtype=float)) / 2.0
            colors[ego_r1_idx] = tuple(avg)
        else:
            colors[ego_r1_idx] = tuple(pink_rgba[1])

    for i, color in enumerate(colors):
        if color is None:
            colors[i] = tuple(pink_rgba[min(pink_rank, len(pink_rgba) - 1)])
            pink_rank += 1

    return [tuple(c) for c in colors]


def format_value(value: float) -> str:
    """Format labels with three significant digits and no leading zero for (0, 1)."""
    if not np.isfinite(value):
        return ""

    if value == 0:
        return "0.00"

    exponent = int(math.floor(math.log10(abs(value))))
    decimals = 2 - exponent

    if decimals > 0:
        formatted = f"{value:.{decimals}f}"
        if 0 < value < 1 and formatted.startswith("0"):
            return formatted[1:]
        return formatted

    rounded = round(value, -decimals)
    return f"{rounded:.0f}"


def plot_metric(
    methods: List[str],
    score_matrix: np.ndarray,
    metric_idx: int,
    metric_key: str,
    metric_symbol: str,
    metric_name: str,
    unit: str,
    out_dir: Path,
) -> Path:
    """Draw one grouped bar chart for one metric."""
    x = np.arange(len(BENCHMARKS), dtype=float)
    n_methods = len(methods)
    group_width = 0.84
    bar_width = group_width / n_methods
    colors = build_method_colors(methods)

    metric_values = score_matrix[:, :, metric_idx]
    finite_values = metric_values[np.isfinite(metric_values)]
    max_value = float(np.max(finite_values)) if finite_values.size > 0 else 1.0
    label_offset = max(max_value * 0.008, 0.008)

    fig, ax = plt.subplots(figsize=(14, 6))

    # Use one unified larger horizontal style for all numeric labels.
    label_fontsize = 14
    label_rotation = 0

    for i, method in enumerate(methods):
        offset = -group_width / 2 + (i + 0.5) * bar_width
        y = score_matrix[i, :, metric_idx]
        bars = ax.bar(x + offset, y, width=bar_width * 0.95, label=method, color=colors[i], edgecolor="none")

        for bar, value in zip(bars, y):
            if not np.isfinite(value):
                continue
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                value + label_offset,
                format_value(value),
                ha="center",
                va="bottom",
                fontsize=label_fontsize,
                fontweight="bold",
                rotation=label_rotation,
            )

    ax.set_xticks(x)
    ax.set_xticklabels(BENCHMARKS)
    ax.set_title(f"{metric_symbol} {metric_name} by Benchmark (Lower is better)", fontsize=TITLE_FONT_SIZE)
    ax.set_ylabel("Value (lower is better)" if unit == "--" else f"Value ({unit}, lower is better)")
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.text(0.01, 0.98, "Lower is better", transform=ax.transAxes, ha="left", va="top", fontsize=9, color="#9a2f62")

    upper_margin = max_value * 0.2 if max_value > 1 else 0.2
    ax.set_ylim(0, max_value + upper_margin)

    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False, fontsize=LEGEND_FONT_SIZE)

    out_path = out_dir / f"exp_pe_{metric_key}.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot grouped bars from exp_pe.tex")
    parser.add_argument("--tex", type=Path, default=Path("exp_pe.tex"), help="Path to exp_pe.tex")
    parser.add_argument("--outdir", type=Path, default=Path("."), help="Output directory for figures")
    args = parser.parse_args()

    tex_path = args.tex.resolve()
    out_dir = args.outdir.resolve()

    if not tex_path.exists():
        raise FileNotFoundError(f"Cannot find tex file: {tex_path}")

    out_dir.mkdir(parents=True, exist_ok=True)
    methods, score_matrix = parse_exp_pe_table(tex_path)

    saved_paths: List[Path] = []
    for idx, (metric_key, metric_symbol, metric_name, unit) in enumerate(METRICS):
        saved_paths.append(plot_metric(methods, score_matrix, idx, metric_key, metric_symbol, metric_name, unit, out_dir))

    print(f"Parsed methods: {len(methods)}")
    for path in saved_paths:
        print(path)


if __name__ == "__main__":
    main()
