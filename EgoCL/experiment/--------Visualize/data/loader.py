from __future__ import annotations

import os
from typing import Any, Dict

from .generator import RandomDataGenerator


def seconds_to_hms(sec: int) -> str:
	h = sec // 3600
	m = (sec % 3600) // 60
	s = sec % 60
	return f"{h:02d}:{m:02d}:{s:02d}"


def save_dataset(dataset: Dict[str, Any], path: str) -> None:
	if path.endswith(".json.gz"):
		RandomDataGenerator.save_json_gz(dataset, path)
	else:
		raise ValueError("Unsupported format. Use .json.gz")


def load_dataset(path: str | None = None, **gen_kwargs) -> Dict[str, Any]:
	"""Load dataset from path; if path is None or missing, generate a new one.

	gen_kwargs: forwarded to RandomDataGenerator.generate
	"""
	if path and os.path.exists(path):
		return RandomDataGenerator.load_json_gz(path)
	# Fallback to generation
	gen = RandomDataGenerator(seed=gen_kwargs.pop("seed", None))
	return gen.generate(**gen_kwargs)


def get_square(dataset: Dict[str, Any], index: int = 0) -> Dict[str, Any]:
	squares = dataset.get("squares", [])
	if not squares:
		raise ValueError("Dataset has no squares")
	if not (0 <= index < len(squares)):
		raise IndexError(f"Square index out of range: {index}")
	return squares[index]
