"""Builder utilities to construct Experience objects by concatenating Activities.

Functions:
 - build_random_experience(activities, n, min_gap, max_gap, prefer_duration)
"""
import random
from pathlib import Path
from typing import Optional, List

# Delay importing project modules that may import heavy deps like cv2



def _activity_duration(activity, default=5.0):
    try:
        v = activity.VIDEO.to_dict
        s = float(v.get('start_s', 0) or 0)
        e = float(v.get('end_s', 0) or 0)
        if e > s:
            return e - s
    except Exception:
        pass
    return default


def build_random_experience(activities, n: int = 5, min_gap: float = 0.0, max_gap: float = 2.0, prefer_duration: bool = True, seed: Optional[int] = None):
    """Randomly pick `n` activities from `activities` and concatenate them into an Experience.

    - activities: an `Activities` container
    - n: number of activities to pick
    - min_gap/max_gap: random gap in seconds inserted between activities
    - prefer_duration: if True, use activity.VIDEO durations when available; else use default 5s
    - seed: optional random seed for reproducibility
    """
    if seed is not None:
        random.seed(seed)

    total_available = len(activities)
    if total_available == 0:
        raise ValueError('No activities available to build experience')

    n = min(n, total_available)
    # support either Activities container or a plain list
    if hasattr(activities, 'activities'):
        pool = activities.activities
    else:
        pool = list(activities)

    picked = random.sample(pool, n)

    # lazy import to avoid requiring cv2 during module import
    from ..elements.Experience import Experience

    exp = Experience(start_s=0.0)
    for act in picked:
        dur = None
        if prefer_duration:
            dur = _activity_duration(act)
        exp.add_activity(act, duration=dur)
        # add a random gap by adjusting the next activity's start via its duration already set
        gap = random.uniform(min_gap, max_gap) if max_gap > 0 else 0.0
        # advance last activity end by gap (i.e., set next offset)
        last = exp.activities.activities[-1]
        last._exp_end_s += gap

    return exp


def save_experience(exp, out_dir: str, name: str = 'experience.json') -> str:
    p = Path(out_dir)
    p.mkdir(parents=True, exist_ok=True)
    out_path = p / name
    exp.save(str(out_path))
    return str(out_path)
