#!/usr/bin/env python3
import gzip
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

def summarize_array(name: str, arr: List[Any], max_preview: int = 5) -> Dict[str, Any]:
    return {
        "name": name,
        "type": type(arr).__name__,
        "length": len(arr),
        "preview": arr[:max_preview],
    }

def main(path: str):
    p = Path(path)
    if not p.exists():
        print(f"File not found: {p}")
        sys.exit(1)
    with gzip.open(p, 'rt', encoding='utf-8') as f:
        data = json.load(f)
    summary = {}
    # Top-level keys
    summary['top_level_keys'] = list(data.keys())
    # Meta
    meta = data.get('meta', {})
    summary['meta_keys'] = list(meta.keys())
    summary['meta'] = meta
    # Squares list
    squares = data.get('squares', [])
    summary['n_squares'] = len(squares)
    square_summaries = []
    for sq in squares:
        s = {
            'keys': list(sq.keys()),
        }
        # id
        s['id'] = sq.get('id')
        # arrays detection: any list valued fields
        for k, v in sq.items():
            if isinstance(v, list):
                s.setdefault('arrays', []).append(summarize_array(k, v))
        square_summaries.append(s)
        # Only fully summarize first few to keep output manageable
        if len(square_summaries) >= 3:
            break
    summary['sample_square_summaries'] = square_summaries
    # For statistics on arrays across all squares, gather length stats for matching field names
    length_stats: Dict[str, List[int]] = {}
    for sq in squares:
        for k, v in sq.items():
            if isinstance(v, list):
                length_stats.setdefault(k, []).append(len(v))
    length_stats_summary = {
        k: {
            'count_squares_with_field': len(lengths),
            'min_length': min(lengths),
            'max_length': max(lengths),
            'avg_length': sum(lengths)/len(lengths)
        } for k, lengths in length_stats.items()
    }
    summary['array_length_stats'] = length_stats_summary
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python inspect_sample_json.py /path/to/sample.json.gz")
        sys.exit(1)
    main(sys.argv[1])
