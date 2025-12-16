
from __future__ import annotations

import argparse
import gzip,os
import json
import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional



from .generator import SquarePoints, RandomDataGenerator


def _now_iso() -> str:
	return datetime.now(timezone.utc).isoformat()


def _open_json_maybe_gz(path: str) -> Any:
	if path.endswith(".gz"):
		with gzip.open(path, "rt", encoding="utf-8") as f:
			return json.load(f)
	with open(path, "r", encoding="utf-8") as f:
		return json.load(f)


def _safe_get(d: Dict[str, Any], *keys, default=None):
	cur: Any = d
	for k in keys:
		if not isinstance(cur, dict) or k not in cur:
			return default
		cur = cur[k]
	return cur


def _to_int_seconds(x: Optional[float]) -> Optional[int]:
	if x is None:
		return None
	try:
		return int(math.floor(float(x)))
	except (TypeError, ValueError):
		return None


def build_square_from_questions(questions: List[Dict[str, Any]], sid: int = 0) -> SquarePoints:
	xs: List[int] = []
	ys: List[int] = []
	vals: List[float] = []

	for q in questions:
		x_sec_f = _safe_get(q, "TIME", "seconds_experience_s")
		start_f = _safe_get(q, "ref_time", "STARTSTAMP", "seconds_experience_s")
		end_f = _safe_get(q, "ref_time", "ENDSTAMP", "seconds_experience_s")
		score = q.get("score", None)

		x_i = _to_int_seconds(x_sec_f)
		s_i = _to_int_seconds(start_f)
		e_i = _to_int_seconds(end_f)

		if x_i is None or s_i is None or e_i is None:
			continue

		y_i = int((s_i + e_i) // 2)

		try:
			v = float(score) if score is not None else None
		except (TypeError, ValueError):
			v = None
		if v is None:
			continue

		xs.append(x_i)
		ys.append(y_i)
		vals.append(v)

	return SquarePoints(id=sid, x_sec=xs, y_sec=ys, value=vals)


def load_exe_dataset(input_path: str) -> Dict[str, Any]: #support both single json(.gz) file and folder of multiple execution.json files
	questionses = []
    
	if input_path.endswith(".json") or input_path.endswith(".json.gz") and os.path.isfile(input_path):
		questionses = _open_json_maybe_gz(input_path).get("questions", []) if isinstance(_open_json_maybe_gz(input_path), dict) else []
	else:
		for file in os.listdir(input_path):
			data = _open_json_maybe_gz(os.path.join(input_path, file, "execution.json"))
			questions = data.get("questions", []) if isinstance(data, dict) else []
			questionses.extend(questions)
			
	square = build_square_from_questions(questionses, sid=0)
	import math
	dataset: Dict[str, Any] = {
		"meta": {
			"version": 1,
			"created": _now_iso(),
			"source": input_path,
			"n_squares": 1,
			"note": "Loaded from experience QA results. x=TIME.seconds_experience_s, y=midpoint(START,END), value=score.",
			"duration_seconds": math.ceil(max(square.x_sec) if len(square.x_sec)>0 else 0),
			"start_epoch_sec": 0,
		},
		"squares": [square.to_dict()],
	}
	return dataset