from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from ..data.loader import load_dataset, get_square


def _compute_heatmap_payload(square: Dict[str, Any], bins: int = 100) -> Dict[str, Any]:
    xs = np.asarray(square["x_sec"], dtype=float)
    ys = np.asarray(square["y_sec"], dtype=float)
    vs = np.asarray(square["value"], dtype=float)
    duration = float(max(xs.max(initial=0.0), ys.max(initial=0.0), 1.0))
    x = xs / max(duration, 1.0)
    y = ys / max(duration, 1.0)
    xi = np.clip((x * bins).astype(int), 0, bins - 1)
    yi = np.clip((y * bins).astype(int), 0, bins - 1)

    # Average per cell
    num = np.zeros((bins, bins), dtype=float)
    den = np.zeros((bins, bins), dtype=float)
    for i, j, w in zip(yi, xi, vs):
        num[i, j] += w
        den[i, j] += 1
    with np.errstate(divide="ignore", invalid="ignore"):
        avg = np.where(den > 0, num / den, np.nan)

    # Prepare ECharts heatmap data [x_idx, y_idx, value] only for lower-right triangle (y<=x)
    data: List[List[float]] = []
    for i in range(bins):
        for j in range(bins):
            # In index space, i is y, j is x; keep cells with y<=x
            if i <= j:
                v = avg[i, j]
                if not np.isnan(v):
                    data.append([int(j), int(i), float(v)])
    return {
        "bins": bins,
        "duration_seconds": int(duration),
        "data": data,
    }


def _compute_bar_payload(square: Dict[str, Any], n_bins: int = 12) -> Dict[str, Any]:
    xs = np.asarray(square["x_sec"], dtype=float)
    ys = np.asarray(square["y_sec"], dtype=float)
    vs = np.asarray(square["value"], dtype=float)
    duration = float(max(xs.max(initial=0.0), ys.max(initial=0.0), 1.0))
    x = xs / max(duration, 1.0)
    y = ys / max(duration, 1.0)
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
    means_desc = means[order]
    return {
        "n_bins": n_bins,
        "means_desc": [None if np.isnan(v) else float(v) for v in means_desc],
    }


def create_app(data_path: str | None = None) -> FastAPI:
    app = FastAPI(title="EgoCL Visualize API")

    # Cache dataset in app state
    dataset = load_dataset(path=data_path, n_squares=1, grid_size=80, duration_seconds=3600)
    square = get_square(dataset, 0)

    @app.get("/api/dataset")
    def get_dataset():
        return {
            "meta": dataset.get("meta", {}),
            "heatmap": _compute_heatmap_payload(square, bins=120),
            "bars": _compute_bar_payload(square, n_bins=12),
        }

    @app.get("/")
    def index() -> HTMLResponse:
        html_path = Path(__file__).with_name("static").joinpath("index.html")
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())

    return app


if __name__ == "__main__":
    import uvicorn
    path = os.environ.get("VIS_DATA", None)
    uvicorn.run(create_app(path), host="127.0.0.1", port=8000)
