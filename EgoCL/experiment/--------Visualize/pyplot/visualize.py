from __future__ import annotations

import math
from typing import Dict, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Normalize
from matplotlib.ticker import FuncFormatter

from ..data.loader import seconds_to_hms


def _gaussian_kernel(size: int, sigma: float) -> np.ndarray:
    assert size % 2 == 1, "Kernel size must be odd"
    ax = np.arange(-(size // 2), size // 2 + 1)
    kernel_1d = np.exp(-(ax ** 2) / (2 * sigma ** 2))
    kernel_1d /= kernel_1d.sum()
    kernel_2d = np.outer(kernel_1d, kernel_1d)
    kernel_2d /= kernel_2d.sum()
    return kernel_2d


def _conv2d(arr: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    """Simple 2D convolution with zero padding. Avoids SciPy dependency.
    Suitable for small kernels (<= 15x15).
    """
    kh, kw = kernel.shape
    pad_h, pad_w = kh // 2, kw // 2
    padded = np.pad(arr, ((pad_h, pad_h), (pad_w, pad_w)), mode="constant")
    out = np.zeros_like(arr, dtype=float)
    # Flip kernel for convolution
    k = kernel[::-1, ::-1]
    H, W = arr.shape
    for i in range(H):
        sl = padded[i : i + kh, :]
        # Sliding window across width
        for j in range(W):
            window = sl[:, j : j + kw]
            out[i, j] = float((window * k).sum())
    return out


def _make_heatmap(square: Dict, bins: int = 100, sigma: float = 1.5) -> Tuple[np.ndarray, np.ndarray]:
    """Bin scatter to grid and smooth; return (avg_grid, mask_nan)."""
    xs = np.asarray(square["x_sec"], dtype=float)
    ys = np.asarray(square["y_sec"], dtype=float)
    vs = np.asarray(square["value"], dtype=float)
    duration = float(max(xs.max(initial=0.0), ys.max(initial=0.0), 1.0))
    x = xs / max(duration, 1.0)
    y = ys / max(duration, 1.0)

    # Bin indices
    xi = np.clip((x * bins).astype(int), 0, bins - 1)
    yi = np.clip((y * bins).astype(int), 0, bins - 1)

    num = np.zeros((bins, bins), dtype=float)
    den = np.zeros((bins, bins), dtype=float)
    for i, j, w in zip(yi, xi, vs):  # note: row-major -> y first
        num[i, j] += w
        den[i, j] += 1.0

    # Smooth numerator and denominator then divide
    ksize = int(max(3, 2 * int(2 * sigma) + 1))
    kernel = _gaussian_kernel(ksize, sigma)
    num_s = _conv2d(num, kernel)
    den_s = _conv2d(den, kernel)
    with np.errstate(divide="ignore", invalid="ignore"):
        avg = np.where(den_s > 0, num_s / den_s, np.nan)

    # Mask upper-left triangle (y > x) so we only display lower-right region
    coords = (np.arange(bins) + 0.5) / bins
    xv, yv = np.meshgrid(coords, coords, indexing="xy")
    mask = (yv > xv)
    avg[mask] = np.nan
    return avg, mask


def _binned_bar(xs: np.ndarray, ys: np.ndarray, vs: np.ndarray, n_bins: int = 12):
    # Normalized distance to diagonal within valid region (>=0)
    duration = float(max(xs.max(initial=0.0), ys.max(initial=0.0), 1.0))
    x = xs / max(duration, 1.0)
    y = ys / max(duration, 1.0)
    # Distance within lower-right triangle relative to y=x (use x - y in [0,1])
    d = np.maximum(0.0, x - y)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    idx = np.clip(np.digitize(d, edges) - 1, 0, n_bins - 1)

    sums = np.zeros(n_bins)
    cnts = np.zeros(n_bins)
    for k, val in zip(idx, vs):
        sums[k] += val
        cnts[k] += 1
    with np.errstate(divide="ignore", invalid="ignore"):
        means = np.where(cnts > 0, sums / cnts, np.nan)

    # Order bars from highest mean value (top) to lowest (bottom)
    order = np.argsort(means)[::-1]
    return edges, means[order], order


def plot_square_to_png(
    square: Dict,
    out_path: str,
    duration_seconds: int,
    bins: int = 120,
    sigma: float = 1.5,
    bar_bins: int = 12,
    cmap: str = "viridis",
) -> None:
    """Render heatmap and right-side horizontal bar chart to a PNG.

    - Colorbar is placed in the blank upper-left triangular area (as an inset).
    - X axis bottom; Y axis on the right with ticks.
    - Bar chart ordered from largest distance (top) to smallest (bottom). Percent labels on the right.
    """
    avg, mask = _make_heatmap(square, bins=bins, sigma=sigma)

    xs = np.asarray(square["x_sec"], dtype=float)
    ys = np.asarray(square["y_sec"], dtype=float)
    vs = np.asarray(square["value"], dtype=float)

    edges, bar_means_desc, order = _binned_bar(xs, ys, vs, n_bins=bar_bins)

    # Figure layout: main heatmap + right bar chart
    fig = plt.figure(figsize=(10, 6), constrained_layout=False)
    gs = fig.add_gridspec(ncols=20, nrows=20, wspace=2.0, hspace=0.0)
    ax_main = fig.add_subplot(gs[:, :14])  # big square-ish area
    ax_bar = fig.add_subplot(gs[:, 16:19])

    # Heatmap
    cmap_obj = plt.get_cmap(cmap).copy()
    cmap_obj.set_bad(color="white")
    im = ax_main.imshow(
        avg,
        origin="lower",
        interpolation="nearest",
        cmap=cmap_obj,
        norm=Normalize(vmin=0.0, vmax=1.0),
        extent=[0, duration_seconds, 0, duration_seconds],
        aspect="equal",
    )

    # Axes formatting: x bottom, y right with HH:MM:SS
    ax_main.xaxis.set_ticks_position("bottom")
    ax_main.yaxis.set_ticks_position("right")
    ax_main.yaxis.tick_right()
    ax_main.yaxis.set_label_position("right")
    ax_main.set_xlabel("X Time (HH:MM:SS)")
    ax_main.set_ylabel("Y Time (HH:MM:SS)")

    def _fmt(x, _pos=None):
        return seconds_to_hms(int(x))

    ax_main.xaxis.set_major_formatter(FuncFormatter(_fmt))
    ax_main.yaxis.set_major_formatter(FuncFormatter(_fmt))

    # Rotate x-axis tick labels to tilt down-right for readability
    for label in ax_main.get_xticklabels():
        label.set_rotation(20)
        label.set_horizontalalignment("right")

    # Colorbar in upper-left blank triangular region (inset)
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes

    cax = inset_axes(ax_main, width="3%", height="45%", loc="upper left", borderpad=1.0)
    cb = fig.colorbar(im, cax=cax)
    cb.set_label("Value")

    # Right-side horizontal bar chart
    # Categories are distance bins from large->small
    y_pos = np.arange(bar_bins)
    ax_bar.barh(y_pos, bar_means_desc, color="#4C78A8")
    ax_bar.set_ylim(-0.5, bar_bins - 0.5)
    ax_bar.invert_yaxis()  # largest distance on top
    ax_bar.set_xlabel("Average")
    ax_bar.xaxis.set_ticks_position("bottom")
    ax_bar.set_yticks([])  # no category labels

    # Percent labels on the right of bars
    for y, v in zip(y_pos, bar_means_desc):
        if not np.isnan(v):
            ax_bar.text(v + 0.01, y, f"{int(round(v * 100)):d}%", va="center")

    # Overlay gray crosses for individual data points
    ax_main.scatter(
        xs, ys, c='gray', marker='x', s=5, alpha=0.4, label='Data Points'
    )
    ax_main.legend(loc='upper right', fontsize='small')

    # Tight-ish layout while respecting custom gridspec spacing
    fig.suptitle("Experimental Data Visualization (Heatmap + Horizontal Bars)")
    fig.subplots_adjust(left=0.07, right=0.92, top=0.9, bottom=0.12, wspace=0.25)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
