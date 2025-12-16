from __future__ import annotations

import gzip
import json
import math
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np


def _now_iso() -> str:
	return datetime.now(timezone.utc).isoformat()


@dataclass
class SquarePoints:
	"""Container for a single square's points. Put things with same type together for compactness and efficiency, better compression.
	However, this would degrade readability for human. Anyway, this is th idea of AI, not me, so...... fuck AI

	Arrays are stored as Python lists for JSON compatibility.
	- x_sec, y_sec: time in seconds from t0 for each coordinate
	- value: float in [0, 1]
	- text: {
		"question": str,
		"answer": str,
		"response": str,
	}
	"""

	id: int
	x_sec: List[int]
	y_sec: List[int]
	value: List[float]
	text: List[dict]

	def to_dict(self) -> Dict[str, Any]:
		return asdict(self)


class RandomDataGenerator:
	"""Generate random experimental data within the lower-right triangle of squares.

	Points lie in the region y_norm <= x_norm (below y=x), where x_norm,y_norm in [0, 1].
	Values follow the trend: the closer to the diagonal (x+y=1), the larger the value.
	"""

	def __init__(self, seed: Optional[int] = None):
		self.rng = np.random.default_rng(seed)

	def generate(
		self,
		n_squares: int = 1,
		grid_size: int = 60,
		duration_seconds: int = 3600,
		noise_std: float = 0.05,
		alpha: float = 3.0,
		start_epoch_sec: int = 0,
	) -> Dict[str, Any]:
		"""Generate a dataset dictionary.

		Args:
			n_squares: number of independent squares to generate
			grid_size: resolution per axis; number of candidate bins along each axis
			duration_seconds: time span for each axis (0..duration_seconds)
			noise_std: std of additive Gaussian noise before clipping
			alpha: decay rate for distance to diagonal (larger -> sharper near diagonal)
			start_epoch_sec: optional start timestamp (seconds from some epoch), used for display

		Returns:
			dataset dict with keys: meta, squares
		"""

		squares: List[SquarePoints] = []

		# Generate random points uniformly within the lower-right triangle
		for sid in range(n_squares):
			num_points = grid_size ** 2  # Approximate number of points
			xs = self.rng.uniform(0, 1, num_points)
			ys = self.rng.uniform(0, 1, num_points)

			# Filter points to keep only those in the lower-right triangle (y <= x)
			mask = ys <= xs
			xs = xs[mask]
			ys = ys[mask]

			# Map to time in seconds
			xs_sec = np.round(xs * duration_seconds).astype(int)
			ys_sec = np.round(ys * duration_seconds).astype(int)

			# Compute values based on distance to diagonal
			dist = np.maximum(0.0, (xs - ys) / math.sqrt(2))
			base_value = np.exp(-alpha * dist)

			# Add noise and clip values
			noise = self.rng.normal(loc=0.0, scale=noise_std, size=base_value.shape)
			values = base_value + noise
			values = np.clip(values, 0.0, 1.0)

			square = SquarePoints(
				id=sid,
				x_sec=xs_sec.tolist(),
				y_sec=ys_sec.tolist(),
				value=values.tolist(),
			)
			squares.append(square)

		dataset: Dict[str, Any] = {
			"meta": {
				"version": 1,
				"created": _now_iso(),
				"n_squares": n_squares,
				"grid_size": grid_size,
				"duration_seconds": duration_seconds,
				"start_epoch_sec": int(start_epoch_sec),
				"note": "Values are higher near the diagonal (x+y=1). Points lie in lower-right triangle.",
			},
			"squares": [s.to_dict() for s in squares],
		}
		return dataset

	# ------------------- Persistence helpers -------------------
	@staticmethod
	def save_json_gz(dataset: Dict[str, Any], path: str) -> None:
		"""Save dataset as gzipped JSON for portability."""
		with gzip.open(path, "wt", encoding="utf-8") as f:
			json.dump(dataset, f, ensure_ascii=False)

	@staticmethod
	def load_json_gz(path: str) -> Dict[str, Any]:
		"""Load dataset from gzipped JSON file."""
		with gzip.open(path, "rt", encoding="utf-8") as f:
			return json.load(f)
