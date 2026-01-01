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
        for s_s, e_s in self.iterate_time(start_s=start_s, end_s=end_s):
            method.MEMORIZER(self, s_s)

    def cheat_progress(self, method, start_s, end_s):
        for anno in self.iterate_annos(start_s=start_s, end_s=end_s):
            method.MEMORIZER.Memory.append(anno.to_dict)
        
    def iterate_video(self, start_s=0.0, end_s=None):
        assert start_s == 0.0 and end_s is None, "iterate_video currently only supports full experience iteration."
        for act in self.ACTIVITIES: #其实是懒得写了，先这样吧
            for video in act.VIDEOS:
                yield video
        
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
        # current_s = start_s
        end_s = end_s if end_s is not None else self.start_s + self.duration_s
        # while current_s < end_s:
        #     yield current_s
        #     current_s += step_s
        start_end_s_list = []
        #我觉得还不如为这个start_s, step_s 和 end_s先生成一份时间秒数列表，然后再遍历这个时间戳列表更好一些
        #那么生成这个列表的第一步，先找到这个start_s落在的ACTIVITY的位置ID，然后找到end_s落在的ACTIVITY的位置ID，然后再从start_s所在的ACTIVITY的start_s开始，遍历到end_s所在的ACTIVITY的end_s结束，中间每隔step_s生成一个时间戳
        #注意如果current_s + step_s超过了当前ACTIVITY的end_s，那么就只输出到这个ACTIVITY的end_s为止，然后列表的下一项是下一个ACTIVITY的start_s，然后继续，
        start_id = None
        end_id = None
        for act_id, act in enumerate(self.ACTIVITIES):
            if act.TIMESPAN.STARTSTAMP.seconds_experience <= start_s < act.TIMESPAN.ENDSTAMP.seconds_experience:
                start_id = act_id
            if act.TIMESPAN.STARTSTAMP.seconds_experience < end_s <= act.TIMESPAN.ENDSTAMP.seconds_experience:
                end_id = act_id
            
        assert start_id is not None and end_id is not None, "start_s or end_s not within experience range."
        current_s = start_s
        while current_s < end_s:
            act = self.ACTIVITIES[start_id]
            if current_s + step_s < act.TIMESPAN.ENDSTAMP.seconds_experience:
                start_end_s_list.append((current_s, current_s + step_s))
                current_s += step_s
            else:
                start_end_s_list.append((current_s,act.TIMESPAN.ENDSTAMP.seconds_experience))
                current_s = act.TIMESPAN.ENDSTAMP.seconds_experience
                start_id += 1
                if start_id > end_id:
                    break
                act = self.ACTIVITIES[start_id]
                current_s = act.TIMESPAN.STARTSTAMP.seconds_experience
        
        for s_e in start_end_s_list:
            yield s_e
        
    def time_to_timestamps(self, start_s: float, end_s: float):
        from . import TimeStamp
        TIMESTAMPS = []
        current_s = start_s

        for act_id, act in enumerate(self.ACTIVITIES):
            if act.TIMESPAN.STARTSTAMP.seconds_experience <= current_s < act.TIMESPAN.ENDSTAMP.seconds_experience:
                for video_id, vid in enumerate(act.VIDEOS):
                    if vid.TIMESPAN.STARTSTAMP.seconds_experience <= current_s < vid.TIMESPAN.ENDSTAMP.seconds_experience:
                        #start one
                        ts_start = vid.TIMESPAN.STARTSTAMP.template(current_s)
                        TIMESTAMPS.append(ts_start)
                        if vid.TIMESPAN.ENDSTAMP.seconds_experience < end_s:
                            ts_end = vid.TIMESPAN.ENDSTAMP.copy()
                            current_s = vid.TIMESPAN.ENDSTAMP.seconds_experience + 0.1
                        else:
                            ts_end = vid.TIMESPAN.STARTSTAMP.template(end_s)
                            current_s = end_s
                        TIMESTAMPS.append(ts_end)
        
        return TIMESTAMPS

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
        from . import YOG
        # YOG.debug("\n".join([t.__repr__() for t in TIMESTAMPS]), "TIMESTAMPS in time_to_video")
        if len(TIMESTAMPS) < 2:
            return None, []
        import moviepy

        video_clips, transcripts = [], []
        _0_experience_start_s = TIMESTAMPS[0].seconds_experience
        for i in range(0, len(TIMESTAMPS), 2):
            ts_start = TIMESTAMPS[i]
            ts_end = TIMESTAMPS[i + 1]
            video = ts_start.VIDEO
            if video.path is None or not os.path.exists(video.path):
                continue
            clip = moviepy.VideoFileClip(video.path)
            video_start_s = video.TIMESPAN.STARTSTAMP.seconds_video
            clip = clip.subclipped(ts_start.seconds_video - video_start_s, min(ts_end.seconds_video - video_start_s, clip.duration-0.01))
            video_clips.append(clip)

            if video.transcript_path and os.path.exists(video.transcript_path):
                import pysrt
                subs = pysrt.open(video.transcript_path)
                clip_subs = subs.slice(starts_after={'seconds': ts_start.seconds_video}, ends_before={'seconds': ts_end.seconds_video})
                # adjust subtitle times to be relative to the clip start
                for sub in clip_subs:
                    sub_start_seconds_origin = sub.start.hours * 3600 + sub.start.minutes * 60 + sub.start.seconds + sub.start.milliseconds / 1000.0
                    sub_start_seconds_real = sub_start_seconds_origin - video_start_s + (ts_start.seconds_experience - _0_experience_start_s)
                    sub.start.hours = int(sub_start_seconds_real // 3600)
                    sub.start.minutes = int((sub_start_seconds_real % 3600) // 60)
                    sub.start.seconds = int(sub_start_seconds_real % 60)
                    sub.start.milliseconds = int((sub_start_seconds_real - int(sub_start_seconds_real)) * 1000)
                    
                    sub_end_seconds_origin = sub.end.hours * 3600 + sub.end.minutes * 60 + sub.end.seconds + sub.end.milliseconds / 1000.0
                    sub_end_seconds_real = sub_end_seconds_origin - video_start_s + (ts_start.seconds_experience - _0_experience_start_s)
                    sub.end.hours = int(sub_end_seconds_real // 3600)
                    sub.end.minutes = int((sub_end_seconds_real % 3600) // 60)
                    sub.end.seconds = int(sub_end_seconds_real % 60)
                    sub.end.milliseconds = int((sub_end_seconds_real - int(sub_end_seconds_real)) * 1000)
                    
                    transcripts.append(sub)

        if not video_clips:
            return None, []
        if len(video_clips) == 1:
            return video_clips[0], transcripts
            
        final_clip = moviepy.concatenate_videoclips(video_clips)
        return final_clip, transcripts

class Experiences:
    """Container for multiple Experience objects"""
    def __init__(self, experiences: Optional[List[Experience]] = None):
        self.experiences = experiences.copy() if experiences else []

    def __iadd__(self, exp: Experience):
        self.experiences.append(exp)
        return self