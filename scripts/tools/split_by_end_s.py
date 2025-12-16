#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Split JSON files into K groups with balanced sum of VIDEO.end_s.

- Read a txt list of IDs or filenames to consider.
- Search under a root directory for matching JSON files.
- Extract VIDEO.end_s from each JSON (fallbacks tolerated).
- Partition into K bins via LPT greedy.
- Save summary JSON and per-bin lists.

Usage (example):
  python scripts/tools/split_by_end_s.py \
    --root /home/yl/D/Ego4d \
    --list /mnt/data/yl/C/EgoCL/scripts/data/unify/item_ego4d.txt \
    --bins 8 \
    --out outputs/ego4d/splits_end_s
"""
from __future__ import annotations
import os, sys, json, glob, argparse, time
from typing import List, Tuple, Dict, Any


def safe_load_json(path: str) -> Dict[str, Any] | None:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except UnicodeDecodeError:
        with open(path, 'r', encoding='latin-1', errors='ignore') as f:
            txt = f.read()
        txt = txt.replace('\x00', '')
        try:
            return json.loads(txt)
        except Exception:
            return None
    except Exception:
        return None


def get_end_s(obj: Dict[str, Any]) -> float | None:
    if not isinstance(obj, dict):
        return None
    # Common shape: obj['VIDEO']['end_s']
    video = obj.get('VIDEO') or obj.get('video') or {}
    if isinstance(video, dict):
        val = video.get('end_s') or video.get('end') or video.get('duration')
        try:
            if val is not None:
                return float(val)
        except Exception:
            pass
    return None


def find_json_for_id(root: str, id_token: str) -> List[str]:
    # Search recursively for files containing the token and ending with .json
    pat = os.path.join(root, '**', f'*{id_token}*.json')
    return glob.glob(pat, recursive=True)


def read_id_list(path: str) -> List[str]:
    ids = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith('#'):
                continue
            ids.append(s)
    return ids


def lpt_partition(items: List[Tuple[str, str, float]], bins: int) -> List[Dict[str, Any]]:
    # items: list of (id_token, path, end_s)
    items_sorted = sorted(items, key=lambda x: -x[2])
    parts = [{'sum': 0.0, 'items': []} for _ in range(bins)]
    for it in items_sorted:
        # pick bin with smallest sum
        idx = min(range(bins), key=lambda i: parts[i]['sum'])
        parts[idx]['items'].append({'id': it[0], 'path': it[1], 'end_s': it[2]})
        parts[idx]['sum'] += it[2]
    return parts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True, help='Root directory containing JSON files')
    ap.add_argument('--list', required=True, help='Txt file with IDs or basenames to match')
    ap.add_argument('--bins', type=int, default=8, help='Number of groups to split into')
    ap.add_argument('--out', default='outputs/ego4d/splits_end_s', help='Output directory for reports')
    ap.add_argument('--max-per-id', type=int, default=1, help='Max files to pick per id (1=first match)')
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)

    ids = read_id_list(args.list)
    print(f"Loaded {len(ids)} ids from {args.list}")

    items = []
    missing = []
    no_end = []

    for i, tok in enumerate(ids):
        matches = find_json_for_id(args.root, tok)
        if not matches:
            missing.append(tok)
            continue
        picked = 0
        for m in matches:
            obj = safe_load_json(m)
            if obj is None:
                continue
            end_s = get_end_s(obj)
            if end_s is None:
                no_end.append(m)
                continue
            items.append((tok, m, float(end_s)))
            picked += 1
            if picked >= args.max_per_id:
                break
        if (i+1) % 200 == 0:
            print(f"Scanned {i+1}/{len(ids)} ids... current usable items: {len(items)}")

    total = sum(x[2] for x in items)
    print(f"Collected {len(items)} items with end_s, total end_s={total:.2f}")

    parts = lpt_partition(items, args.bins)
    # enrich with stats
    for p in parts:
        p['count'] = len(p['items'])
    sums = [p['sum'] for p in parts]
    print("Per-bin sums:", [round(s, 2) for s in sums])

    # save reports
    ts = time.strftime('%Y%m%d-%H%M%S')
    summary = {
        'root': args.root,
        'list': args.list,
        'bins': args.bins,
        'total_items': len(items),
        'total_end_s': total,
        'per_bin_sum': sums,
        'missing_ids': missing,
        'files_without_end_s': no_end,
        'bins_detail': parts,
    }
    sum_path = os.path.join(args.out, f'summary_{ts}.json')
    with open(sum_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # write per-bin file lists
    for i, p in enumerate(parts):
        with open(os.path.join(args.out, f'bin_{i+1}.txt'), 'w', encoding='utf-8') as f:
            for it in p['items']:
                f.write(f"{it['path']}\t{it['end_s']}\n")

    # also a CSV of id -> bin
    with open(os.path.join(args.out, 'assignments.tsv'), 'w', encoding='utf-8') as f:
        f.write('id\tbin\tend_s\tpath\n')
        for i, p in enumerate(parts):
            for it in p['items']:
                f.write(f"{it['id']}\t{i+1}\t{it['end_s']}\t{it['path']}\n")

    print(f"Written summary to {sum_path} and per-bin lists to {args.out}")


if __name__ == '__main__':
    main()
