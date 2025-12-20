from .Activity import Activity, Activities
import os, json
from typing import List, Optional

class Experience:
    """An Experience is an ordered sequence of Activity objects arranged in time.

    Each Activity's Video time (VIDEO.start_s/VIDEO.end_s) is used to determine its duration when available.
    When concatenating activities, we assign start/end times sequentially.
    """
    def __init__(self, activities: Optional[List[Activity]] | Activities = [], start_s: float = 0.0, *args, **kwargs):
        # activities may be a Activities container or list of Activity
        self.ACTIVITIES = activities if isinstance(activities, Activities) else Activities(list(activities))
        import time
        self.name = kwargs.get('name', f"Unnamed_{time.strftime('%m%d_%H_%M_%S', time.localtime())}")
        self.start_s = float(start_s)
        durations = kwargs.get('durations', [])
        durations = durations + [None] * (len(self.ACTIVITIES) - len(durations))
        self.schedules(durations)

    @classmethod
    def from_loader(cls, *args, **kwargs):
        from ..load import loader
        activities = loader(*args, **kwargs)
        return cls(activities.activities, *args, **kwargs)

    def __len__(self):
        return len(self.ACTIVITIES)
    
    def schedule(self, i, duration_s = None):   # determine offset: if there are existing timeline entries, append after last end
        if duration_s == 0.0: return
        if duration_s is not None: self.ACTIVITIES.activities[i] = self.ACTIVITIES[i].clip(duration_s)
        offset = self.ACTIVITIES[i-1].TIMESPAN.ENDSTAMP.seconds_experience if i > 0 else self.start_s
        self.ACTIVITIES[i].s_EXPERIENCE = self
        self.ACTIVITIES[i].offset_start(offset, self)
        
    def schedules(self, durations: Optional[List[float]] = [], use_tqdm: bool = True):
        if not use_tqdm:
            for i in range(len(self.ACTIVITIES)): self.schedule(i, durations[i])
            return
        from tqdm import tqdm
        with tqdm(total=len(self.ACTIVITIES)) as bar:
            for i in range(len(self.ACTIVITIES)):
                bar.set_description("scheduling: " + self.ACTIVITIES[i].name[:8])
                self.schedule(i, durations[i])
                bar.update(1)

    def __getitem__(self, index):
        return self.ACTIVITIES[index] #???

    @property
    def timeline(self):
        """Return list of tuples (start_s, end_s, activity) ordered by start time."""
        return [(act.start_s, act.end_s, act.name) for act in self.ACTIVITIES]
    
    @property
    def duration_s(self):
        return self.ACTIVITIES[-1].TIMESPAN.ENDSTAMP - self.ACTIVITIES[0].TIMESPAN.STARTSTAMP

    @property
    def to_dict(self):
        return {
            'name': self.name,
            'start_s': self.start_s,
            'duration_s': self.duration_s,
            'activities': [a.to_dict for a in self.ACTIVITIES]
        }

    def save(self, out_path: str = ""):
        from .. import EPRC_ROOT
        if out_path == "": out_path = os.path.join(EPRC_ROOT, f'{self.name}.json')
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        open(out_path, 'w', encoding='utf-8').write(json.dumps(self.to_dict, ensure_ascii=False, indent=2))

    @classmethod
    def from_dict(cls, data: dict): #这个from_dict和to_dict我觉得以后需要重新写，重新替换一下，现在是完全存储然后完全加载活动的全部信息；我想改成存储活动文件的路径，和加载方式，然后加载活动文件来构建活动对象；但这个是底层的东西，可以到时候替换的，不影响上层逻辑；顶多就是前一个版本的经历文件和后一个版本的经历文件不兼容而已
        acts = []
        from . import TimeSpan
        for ad in data.get('activities', []):
            a = Activity({'name': ad.get('name', 'Unknown Activity'), 'source': ad.get('source', 'Unknown Source')})
            # load VIDEO and ANNOS if present
            a.VIDEOS.from_dict(ad.get('VIDEOS', {}))
            a.ANNOS.from_dict(ad.get('ANNOS', {}))
            a.TIMESPAN = TimeSpan.from_dict(ad.get('TIMESPAN', {}), a.VIDEOS, a, None)
            acts.append(a)
        # construct Experience without re-computing timeline if timeline provided
        exp = cls(activities=[], start_s=data.get('start_s', 0.0), name=data.get('name', 'Unnamed'))
        exp.ACTIVITIES = Activities(acts)
        return exp

    @classmethod
    def load(cls, in_path: str):
        print(in_path)
        with open(in_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)

    @classmethod
    def load_from_name(cls, experience_name: str):
        from .. import EPRC_ROOT
        in_path = os.path.join(EPRC_ROOT, f'{experience_name}.json')
        return cls.load(in_path)


    def __repr__(self):
        return f'Experience(start_s={self.start_s}, duration={self.duration}, num_activities={len(self.activities)})'

    def clip(self, start_s: float, end_s: float):
        """Return a new Experience clipped to the specified time range."""
        clipped_activities = []
        for act in self.ACTIVITIES:
            if act.end_s <= start_s:
                continue
            if act.start_s >= end_s:
                break
            # clip activity to fit within start_s and end_s
            clip_start = max(act.start_s, start_s)
            clip_end = min(act.end_s, end_s)
            clipped_act = act.clip(clip_end, clip_start)
            clipped_activities.append(clipped_act)
        return Experience(clipped_activities, start_s=start_s)


    def progress(self, method, start_s, end_s):
        if method.MEMORIZER.__class__.__name__ == "CheatMemorize":
            self.cheat_progress(method, start_s=start_s, end_s=end_s)
            return
        for t in self.iterate_time(start_s=start_s, end_s=end_s):
            method.MEMORIZER(self, t)

    def cheat_progress(self, method, start_s, end_s):
        for anno in self.iterate_annos(start_s=start_s, end_s=end_s):
            method.MEMORIZER.Memory.append(anno.to_dict)

    def iterate_act(self, start_s=0.0, end_s=None):
        """Generator to iterate through activities within a time range."""
        for act in self.ACTIVITIES:
            if end_s is not None and act.TIMESPAN.STARTSTAMP.seconds_experience >= end_s:
                break
            if act.TIMESPAN.ENDSTAMP.seconds_experience > start_s:
                yield act
        
    def iterate_annos(self, start_s=0.0, end_s=None):
        """Generator to iterate through annotations within a time range."""
        for act in self.iterate_act(start_s, end_s):
            ANNOS = [anno for category in act.ANNOS.ANNOS for anno in act.ANNOS.ANNOS[category] if (end_s is None or anno.TIMESPAN.STARTSTAMP.seconds_experience < end_s) and anno.TIMESPAN.ENDSTAMP.seconds_experience > start_s]
            ANNOS.sort(key=lambda x: x.TIMESPAN.STARTSTAMP.seconds_experience)
            for anno in ANNOS:
                yield anno

    def iterate_time(self, step_s=1.0, start_s=0.0, end_s=None):
        """Generator to iterate through time steps within the experience."""
        current_s = start_s
        end_s = end_s if end_s is not None else self.start_s + self.duration_s
        while current_s < end_s:
            yield current_s
            current_s += step_s
        
    def time_to_timestamps(self, start_s: float, end_s: float):
        from . import TimeStamp
        TIMESTAMPS = []
        current_s = start_s
        for act_id, act in enumerate(self.ACTIVITIES):
            if act.TIMESPAN.STARTSTAMP.seconds_experience <= current_s < act.TIMESPAN.ENDSTAMP.seconds_experience:
                ts_current = TimeStamp()
                ts_current.EXPERIENCE = self
                ts_current.seconds_experience = current_s

                ts_current.ACTIVITY = act
                ts_current.seconds_activity = current_s - act.TIMESPAN.STARTSTAMP.seconds_experience

                ts_current.VIDEO = act.VIDEO
                ts_current.seconds_video = act.VIDEO.start_s + (current_s - act.TIMESPAN.STARTSTAMP.seconds_experience)  #FIXME: MAYBE WRONG IF MULTI-VIDEO ACTIVITY
                TIMESTAMPS.append(ts_current)
                current_s = act.TIMESPAN.ENDSTAMP.seconds_experience + 0.1  # move to next moment
                if current_s >= end_s:
                    ts_current = TimeStamp()
                    ts_current.EXPERIENCE = self
                    ts_current.seconds_experience = end_s
                    ts_current.ACTIVITY = act
                    ts_current.seconds_activity = end_s - act.TIMESPAN.STARTSTAMP.seconds_experience
                    ts_current.VIDEO = act.VIDEO
                    ts_current.seconds_video = act.VIDEO.start_s + (end_s - act.TIMESPAN.STARTSTAMP.seconds_experience)
                    TIMESTAMPS.append(ts_current)
                    break
                else:
                    ts_current = TimeStamp()
                    ts_current.EXPERIENCE = self
                    ts_current.seconds_experience = act.TIMESPAN.ENDSTAMP.seconds_experience
                    ts_current.ACTIVITY = act
                    ts_current.seconds_activity = act.TIMESPAN.ENDSTAMP.seconds_experience - act.TIMESPAN.STARTSTAMP.seconds_experience
                    ts_current.VIDEO = act.VIDEO
                    ts_current.seconds_video = act.VIDEO.start_s + (act.TIMESPAN.ENDSTAMP.seconds_experience - act.TIMESPAN.STARTSTAMP.seconds_experience)
                    TIMESTAMPS.append(ts_current)
                    if act_id + 1 < len(self.ACTIVITIES):
                        ts_current = TimeStamp()
                        ts_current.EXPERIENCE = self
                        act_1 = self.ACTIVITIES[act_id + 1]
                        ts_current.seconds_experience = act_1.TIMESPAN.STARTSTAMP.seconds_experience
                        ts_current.ACTIVITY = act_1
                        ts_current.seconds_activity = 0.0
                        ts_current.VIDEO = act_1.VIDEO
                        ts_current.seconds_video = act_1.VIDEO.start_s
                        TIMESTAMPS.append(ts_current)
        return TIMESTAMPS
    
    def time_to_video(self, start_s: float, end_s: float) -> Optional[float]:
        TIMESTAMPS = self.time_to_timestamps(start_s, end_s)
        if len(TIMESTAMPS) < 2:
            return None
        import moviepy

        video_clips = []
        for i in range(len(TIMESTAMPS) - 1):
            ts_start = TIMESTAMPS[i]
            ts_end = TIMESTAMPS[i + 1]
            video = ts_start.VIDEO
            if video.path is None or not os.path.exists(video.path):
                continue
            clip = moviepy.VideoFileClip(video.path)
            clip = clip.subclipped(ts_start.seconds_video - video.start_s, min(ts_end.seconds_video - video.start_s, clip.duration-0.01))
            video_clips.append(clip)
        if not video_clips:
            return None
        if len(video_clips) == 1:
            return video_clips[0]
        final_clip = moviepy.concatenate_videoclips(video_clips)
        return final_clip

class Experiences:
    """Container for multiple Experience objects"""
    def __init__(self, experiences: Optional[List[Experience]] = None):
        self.experiences = experiences.copy() if experiences else []

    def __iadd__(self, exp: Experience):
        self.experiences.append(exp)
        return self