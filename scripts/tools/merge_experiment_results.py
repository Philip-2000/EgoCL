#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge multiple experiment result json.gz files into a single bin.json.gz.

Input files follow the structure produced by Experiment.save_result:
{
  "meta": {...},
  "squares": [ {"id": 0, "x_sec": [...], "y_sec": [...], "value": [...]} ]
}

Merge strategy:
- Concatenate all squares; reassign sequential ids (0..N-1).
- meta.version: max of versions (if present), else 1.
- meta.created: new current UTC timestamp.
- meta.n_squares: total squares after merge.
- meta.grid_size: sum of individual lengths of value lists.
- meta.duration_seconds: max of per-file meta.duration_seconds (fallback 0).
- meta.start_epoch_sec: min of per-file meta.start_epoch_sec (fallback 0).
- Preserve a list of source filenames in meta.sources.

Usage:
  python scripts/tools/merge_experiment_results.py \
    --in-dir outputs/experiments \
    --out-path outputs/experiments/bin.json.gz
"""
from __future__ import annotations
import os, json, gzip, argparse, datetime
from typing import Dict, Any, List


def load_json_gz(path: str) -> Dict[str, Any]:
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        return json.load(f)


def save_json_gz(obj: Dict[str, Any], path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path, 'wt', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def merge(files: List[str]) -> Dict[str, Any]:
    squares_all = []
    versions = []
    durations = []
    starts = []
    sources = []

    for fpath in files:
        try:
            data = load_json_gz(fpath)
        except Exception:
            continue
        meta = data.get('meta', {})
        versions.append(meta.get('version', 1))
        durations.append(meta.get('duration_seconds', 0))
        starts.append(meta.get('start_epoch_sec', 0))
        sources.append(os.path.basename(fpath))
        for sq in data.get('squares', []):
            # shallow copy to avoid mutating original
            squares_all.append({
                'x_sec': list(sq.get('x_sec', [])),
                'y_sec': list(sq.get('y_sec', [])),
                'value': list(sq.get('value', []))
            })

    # reassign ids
    for i, sq in enumerate(squares_all):
        sq['id'] = i

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    merged_meta = {
        'version': max(versions) if versions else 1,
        'created': now_iso,
        'n_squares': len(squares_all),
        'grid_size': sum(len(sq.get('value', [])) for sq in squares_all),
        'duration_seconds': max(durations) if durations else 0,
        'start_epoch_sec': min(starts) if starts else 0,
        'note': 'Merged result from multiple experiment json.gz files; squares concatenated.',
        'sources': sources,
    }

    return {
        'meta': merged_meta,
        'squares': squares_all
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in-dir', required=True, help='Directory containing bin_*_results.json.gz files')
    ap.add_argument('--pattern', default='bin_*_results.json.gz', help='Glob pattern to match')
    ap.add_argument('--out-path', required=True, help='Output path for merged bin.json.gz')
    args = ap.parse_args()

    import glob
    files = sorted(glob.glob(os.path.join(args.in_dir, args.pattern)))
    if not files:
        raise SystemExit(f'No input files matched pattern {args.pattern} in {args.in_dir}')

    merged = merge(files)
    save_json_gz(merged, args.out_path)
    print(f"Merged {len(files)} files -> {args.out_path}. n_squares={merged['meta']['n_squares']} grid_size={merged['meta']['grid_size']}")


if __name__ == '__main__':
    main()
