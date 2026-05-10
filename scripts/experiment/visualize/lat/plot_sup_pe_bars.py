#!/usr/bin/env python3
"""Draw grouped bar charts from sup_pe.tex."""

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
    ("delta_c", r"$\overline{\delta^c}$", "Choice Delay", "s"),
    ("delta_e", r"$\overline{\delta^e}$", "Encoding Delay", "s"),
    ("delta_m_tau", r"$\overline{\delta^m_\tau}$", "Memorize Tau", "--"),
    ("delta_c_tau", r"$\overline{\delta^c_\tau}$", "Choice Delay Rate", "--"),
    ("delta_e_tau", r"$\overline{\delta^e_\tau}$", "Encoding Delay Rate", "--"),
    ("eta_MV", r"$\overline{\eta^{\mathcal{M}}_{\mathcal{V}}}$", "Compression Rate", "--"),
]

XTICK_FONT_SIZE = 18
YTICK_FONT_SIZE = 16


def clean_method_name(raw: str) -> str:
    """Remove LaTeX marks and keep readable method names."""
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


def strip_latex_comment(line: str) -> str:
    """Strip comments that start with an unescaped percent sign."""
    match = re.search(r"(?<!\\)%", line)
    if match:
        return line[: match.start()].strip()
    return line.strip()


def extract_cell_value(cell: str) -> float:
    """Extract numeric value from one LaTeX table cell; return NaN for missing '--'."""
    clean = re.sub(r"\\cellcolor\{[^{}]*\}", "", cell)
    clean = re.sub(r"\\[a-zA-Z]+\{[^{}]*\}", "", clean)
    clean = re.sub(r"(?<=\d),(?=\d)", ".", clean)
    clean = clean.replace("$", " ").strip()

    if re.fullmatch(r"-+", clean):
        return float("nan")

    match = re.search(r"[-+]?(?:\d*\.\d+|\d+)", clean)
    if not match:
        raise ValueError(f"No numeric value in cell: {cell}")
    return float(match.group(0))


def parse_sup_pe_table(tex_path: Path) -> Tuple[List[str], np.ndarray, int]:
    """Parse method rows into names, score matrix [N, 3, 6], and split index."""
    methods: List[str] = []
    first_part: dict[str, List[float]] = {}
    second_part: dict[str, List[float]] = {}
    split_idx: int | None = None

    lines = tex_path.read_text(encoding="utf-8").splitlines()
    in_tabular = False
    section = 1
    pending_prefix = ""
    row_buffer = ""

    def consume_row(raw_row: str, section_idx: int) -> None:
        row_body = re.sub(r"\\\\.*$", "", raw_row).strip()
        if not row_body:
            return

        cells = [part.strip() for part in row_body.split("&")]
        # sup_pe.tex rows are: method, size, then 9 values (3 benchmarks x 3 metrics).
        if len(cells) != 11:
            return

        method = clean_method_name(cells[0])
        if not method or method in {"Benchmark", "Metric", "Unit"}:
            return

        values: List[float] = []
        ok = True
        for cell in cells[2:]:
            try:
                values.append(extract_cell_value(cell))
            except ValueError:
                ok = False
                break

        if not ok or len(values) != 9:
            return

        if section_idx == 1:
            if method not in first_part:
                methods.append(method)
            first_part[method] = values
        else:
            second_part[method] = values

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

        no_comment = strip_latex_comment(line)
        if not no_comment:
            continue

        if "delta^c_\\tau" in no_comment:
            section = 2

        if row_buffer:
            row_buffer += " " + no_comment
            if r"\\" in no_comment:
                consume_row(row_buffer, section)
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
                consume_row(row_buffer, section)
                row_buffer = ""
            continue

        if section == 1 and split_idx is None and methods and no_comment.startswith(r"\hline"):
            split_idx = len(methods)
            continue

        if no_comment.startswith(r"\hline"):
            continue

        pending_prefix = no_comment

    merged_methods: List[str] = []
    merged_rows: List[List[float]] = []
    for method in methods:
        if method not in first_part or method not in second_part:
            continue

        first_values = first_part[method]
        second_values = second_part[method]

        merged: List[float] = []
        for bench_idx in range(len(BENCHMARKS)):
            base = bench_idx * 3
            delta_c, delta_e, delta_m_tau = first_values[base : base + 3]
            delta_c_tau, delta_e_tau, eta_MV = second_values[base : base + 3]
            merged.extend([delta_c, delta_e, delta_m_tau, delta_c_tau, delta_e_tau, eta_MV])

        merged_methods.append(method)
        merged_rows.append(merged)

    if not merged_rows:
        raise RuntimeError(f"No data rows parsed from {tex_path}")

    score_matrix = np.asarray(merged_rows, dtype=float).reshape(len(merged_rows), len(BENCHMARKS), len(METRICS))
    if split_idx is None:
        split_idx = min(8, len(merged_methods))
    else:
        split_idx = min(split_idx, len(merged_methods))

    return merged_methods, score_matrix, split_idx


def build_method_colors(n_methods: int, split_idx: int) -> List[Tuple[float, float, float, float]]:
    """Create colors for: first group blue, middle group strong pink, last one light yellow."""
    split_idx = max(0, min(split_idx, n_methods))
    middle_count = max(0, n_methods - split_idx - 1)
    colors: List[Tuple[float, float, float, float]] = []

    if split_idx > 0:
        blue_scale = np.linspace(0.45, 0.9, split_idx)
        colors.extend([plt.cm.Blues(v) for v in blue_scale])

    if middle_count > 0:
        pink_map = mcolors.LinearSegmentedColormap.from_list("strongpink", ["#ffd1e1", "#ff6f9f", "#d81b60"])
        pink_scale = np.linspace(0.45, 1.0, middle_count)
        colors.extend([pink_map(v) for v in pink_scale])

    if len(colors) < n_methods:
        colors.append(mcolors.to_rgba("#f6e6a6"))

    return colors


def format_value(value: float) -> str:
    """Format labels on bars with three significant digits."""
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
    split_idx: int,
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
    all_colors = build_method_colors(n_methods, split_idx)

    # Remove methods with no valid value for this metric so they take no bar space.
    active_indices = [idx for idx in range(n_methods) if np.isfinite(score_matrix[idx, :, metric_idx]).any()]
    if not active_indices:
        raise RuntimeError(f"No valid values for metric {metric_key}")

    active_methods = [methods[idx] for idx in active_indices]
    active_colors = [all_colors[idx] for idx in active_indices]
    active_scores = score_matrix[active_indices, :, metric_idx]
    bar_width = group_width / len(active_methods)

    fig, ax = plt.subplots(figsize=(14, 6))

    label_fontsize = 13
    label_rotation = 90

    for i, (method, color, y) in enumerate(zip(active_methods, active_colors, active_scores)):
        offset = -group_width / 2 + (i + 0.5) * bar_width
        bars = ax.bar(x + offset, y, width=bar_width * 0.95, label=method, color=color, edgecolor="none")

        for bar, value in zip(bars, y):
            if not np.isfinite(value):
                continue
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                value,
                format_value(value),
                ha="center",
                va="bottom",
                fontsize=label_fontsize,
                fontweight="bold",
                rotation=label_rotation,
            )

    ax.set_xticks(x)
    ax.set_xticklabels(BENCHMARKS, fontsize=XTICK_FONT_SIZE, fontweight="bold")
    ax.tick_params(axis="y", labelsize=YTICK_FONT_SIZE)
    ax.grid(axis="y", linestyle="--", alpha=0.35)

    metric_values = active_scores
    finite_values = metric_values[np.isfinite(metric_values)]
    if finite_values.size > 0:
        max_value = float(np.max(finite_values))
        upper_margin = max_value * 0.2 if max_value > 1 else 0.2
        ax.set_ylim(0, max_value + upper_margin)

    out_path = out_dir / f"exp_pe_{metric_key}.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot grouped bars from sup_pe.tex")
    parser.add_argument("--tex", type=Path, default=Path("sup_pe.tex"), help="Path to sup_pe.tex")
    parser.add_argument("--outdir", type=Path, default=Path("."), help="Output directory for figures")
    args = parser.parse_args()

    tex_path = args.tex.resolve()
    out_dir = args.outdir.resolve()

    if not tex_path.exists():
        raise FileNotFoundError(f"Cannot find tex file: {tex_path}")

    out_dir.mkdir(parents=True, exist_ok=True)
    methods, score_matrix, split_idx = parse_sup_pe_table(tex_path)

    saved_paths: List[Path] = []
    for idx, (metric_key, metric_symbol, metric_name, unit) in enumerate(METRICS):
        saved_paths.append(
            plot_metric(methods, score_matrix, split_idx, idx, metric_key, metric_symbol, metric_name, unit, out_dir)
        )

    print(f"Parsed methods: {len(methods)}")
    print(f"Split index (above hline): {split_idx}")
    for path in saved_paths:
        print(path)


if __name__ == "__main__":
    main()
