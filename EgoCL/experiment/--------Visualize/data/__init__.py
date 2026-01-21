"""Data package for experiment visualization.

Modules:
- generator: Random data generation for triangular region within squares.
- loader: IO helpers to save/load datasets and small utilities.
"""

from .generator import RandomDataGenerator
from .loader import (
    save_dataset,
    load_dataset,
    get_square,
    seconds_to_hms,
)

__all__ = [
    "RandomDataGenerator",
    "save_dataset",
    "load_dataset",
    "get_square",
    "seconds_to_hms",
]
