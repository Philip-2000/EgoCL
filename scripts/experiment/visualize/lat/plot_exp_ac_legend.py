#!/usr/bin/env python3
"""Draw a standalone legend for exp_ac bar charts."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from plot_exp_ac_bars import build_method_colors, parse_exp_ac_table

FIG_SIZE = (18, 3)
TEXT_FONT_SIZE = 18
SWATCH_WIDTH = 0.10
SWATCH_HEIGHT = 0.14
TEXT_GAP = 0.012

COLUMN_X = [0.03, 0.27, 0.51, 0.75]
ROW_Y = [0.84, 0.62, 0.40, 0.18]


def split_columns(methods: List[str]) -> List[List[str]]:
    """Arrange methods into 4 columns: 4 + 4 + 4 + 1."""
    return [
        methods[:4],
        methods[4:8],
        methods[8:12],
        methods[12:13],
    ]


def draw_entry(
    ax: plt.Axes,
    x: float,
    y: float,
    method: str,
    color: Tuple[float, float, float, float],
) -> None:
    """Draw one color swatch and one method label."""
    ax.add_patch(
        Rectangle(
            (x, y - SWATCH_HEIGHT / 2),
            SWATCH_WIDTH,
            SWATCH_HEIGHT,
            facecolor=color,
            edgecolor="none",
        )
    )
    ax.text(
        x + SWATCH_WIDTH + TEXT_GAP,
        y,
        method,
        va="center",
        ha="left",
        fontsize=TEXT_FONT_SIZE,
    )


def draw_legend(methods: List[str], colors: List[Tuple[float, float, float, float]], out_path: Path) -> None:
    """Draw legend-only figure with the requested column layout."""
    method_to_color: Dict[str, Tuple[float, float, float, float]] = {
        method: color for method, color in zip(methods, colors)
    }

    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    columns = split_columns(methods)

    for col_idx in range(3):
        if col_idx >= len(columns):
            break
        x = COLUMN_X[col_idx]
        for row_idx, method in enumerate(columns[col_idx]):
            if row_idx >= len(ROW_Y):
                break
            y = ROW_Y[row_idx]
            draw_entry(ax, x, y, method, method_to_color[method])

    if len(columns) >= 4 and columns[3]:
        # Keep the last method alone in the final column (full-column style).
        method = columns[3][0]
        draw_entry(ax, COLUMN_X[3], 0.5, method, method_to_color[method])

    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot standalone legend for exp_ac charts")
    parser.add_argument("--tex", type=Path, default=Path("sup_ac.tex"), help="Path to sup_ac.tex")
    parser.add_argument("--out", type=Path, default=Path("exp_ac_legend.png"), help="Output legend image")
    args = parser.parse_args()

    tex_path = args.tex.resolve()
    out_path = args.out.resolve()

    if not tex_path.exists():
        raise FileNotFoundError(f"Cannot find tex file: {tex_path}")

    out_path.parent.mkdir(parents=True, exist_ok=True)

    methods, _, split_idx = parse_exp_ac_table(tex_path)
    colors = build_method_colors(len(methods), split_idx)

    draw_legend(methods, colors, out_path)
    print(f"Legend methods: {len(methods)}")
    print(out_path)


if __name__ == "__main__":
    main()
