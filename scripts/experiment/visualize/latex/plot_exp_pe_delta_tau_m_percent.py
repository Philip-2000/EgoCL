#!/usr/bin/env python3
"""Plot only delta_tau_m from exp_pe.tex as percentage bars with 100% reference bars."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import List, Tuple

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np

BENCHMARKS = ["Egoschema", "EgoLifeQA", "EgoR1Bench"]
METRIC_IDX = 2
METRIC_KEY = "delta_tau_m"
METRIC_SYMBOL = r"$\overline{\delta^m_\tau}$"
METRIC_NAME = "Memorize Time Rate"

EXPECTED_VALUE_COUNT = 12
TITLE_FONT_SIZE = 17
LEGEND_FONT_SIZE = 14


def clean_method_name(raw: str) -> str:
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

    score_matrix = np.asarray(rows, dtype=float).reshape(len(rows), len(BENCHMARKS), 4)
    return methods, score_matrix


def build_method_colors(methods: List[str]) -> List[Tuple[float, float, float, float]]:
    if not methods:
        return []

    # Stronger contrast among pink bars for non-EgoVidMem methods.
    pink_palette = ["#fde8f0", "#f6bccf", "#ea8bab", "#d96592"]
    colors: List[Tuple[float, float, float, float]] = []
    pink_rank = 0

    for method in methods:
        if "EgoVidMem" in method:
            colors.append(mcolors.to_rgba("#f6e6a6"))
            continue
        color = pink_palette[min(pink_rank, len(pink_palette) - 1)]
        colors.append(mcolors.to_rgba(color))
        pink_rank += 1

    return colors


def format_percent(value: float) -> str:
    """value is in ratio; convert to percent string using one decimal place."""
    pct = value * 100.0
    return f"{pct:.1f}%"


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot delta_tau_m as percentage bars with 100% reference")
    parser.add_argument("--tex", type=Path, default=Path("exp_pe.tex"), help="Path to exp_pe.tex")
    parser.add_argument("--out", type=Path, default=Path("exp_pe_delta_tau_m_percent.png"), help="Output image path")
    args = parser.parse_args()

    tex_path = args.tex.resolve()
    out_path = args.out.resolve()

    if not tex_path.exists():
        raise FileNotFoundError(f"Cannot find tex file: {tex_path}")

    methods, score_matrix = parse_exp_pe_table(tex_path)

    # Remove Ego-R1 (second method in the original table) as requested.
    keep_indices = [i for i, method in enumerate(methods) if "Ego-R1" not in method]
    methods = [methods[i] for i in keep_indices]
    score_matrix = score_matrix[keep_indices, :, :]

    x = np.arange(len(BENCHMARKS), dtype=float)
    n_methods = len(methods)
    group_width = 0.84
    base_step = group_width / n_methods
    center_step = base_step * 1.10
    cluster_span = center_step * n_methods
    bar_width = base_step * 0.86
    colors = build_method_colors(methods)

    metric_values = score_matrix[:, :, METRIC_IDX]

    fig, ax = plt.subplots(figsize=(14, 6.5))

    bg_shift = bar_width * 0.12
    bar_actual_width = bar_width * 0.92

    for i, method in enumerate(methods):
        offset = -cluster_span / 2 + (i + 0.5) * center_step
        xpos = x + offset
        vals = metric_values[i, :]

        for j, val in enumerate(vals):
            if not np.isfinite(val):
                continue
            ax.bar(
                xpos[j] + bg_shift,
                100.0,
                width=bar_actual_width,
                color="#dceeff",
                edgecolor="#b9d8f5",
                linewidth=0.8,
                zorder=1,
            )

        clipped = np.where(np.isfinite(vals), np.minimum(vals * 100.0, 110.0), np.nan)
        bars = ax.bar(
            xpos,
            clipped,
            width=bar_actual_width,
            color=colors[i],
            edgecolor="none",
            zorder=2,
            label=method,
        )

        for j, bar in enumerate(bars):
            val = vals[j]
            if np.isfinite(val):
                shown_h = min(val * 100.0, 110.0)
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    shown_h + 1.2,
                    format_percent(val),
                    ha="center",
                    va="bottom",
                    fontsize=11,
                    fontweight="bold",
                    rotation=0,
                )
            else:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    3.0,
                    "N/A",
                    ha="center",
                    va="bottom",
                    fontsize=9,
                    color="#666666",
                )

    ax.set_xticks(x)
    ax.set_xticklabels(BENCHMARKS)
    ax.set_ylim(0, 115)
    ax.set_yticks([0, 20, 40, 60, 80, 100, 110])
    ax.set_ylabel("Percentage (%)")
    ax.set_title(f"{METRIC_SYMBOL} {METRIC_NAME} (100% background, clipped at 110%)", fontsize=TITLE_FONT_SIZE)
    ax.grid(axis="y", linestyle="--", alpha=0.35, zorder=0)

    handles, labels = ax.get_legend_handles_labels()
    handles.append(Patch(facecolor="#dceeff", edgecolor="#b9d8f5", label="100% reference"))
    labels.append("100% reference")
    ax.legend(handles, labels, loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False, fontsize=LEGEND_FONT_SIZE)

    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Parsed methods: {len(methods)}")
    print(out_path)


if __name__ == "__main__":
    main()
