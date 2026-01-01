import time

DEFAULT_EXPERIENCE_START_BASE = 8*3600  #assuming experience starts at 8:00 AM

class TimeStamp:
    def __init__(self):
        self.seconds_natural = None

        self.EXPERIENCE = None
        self.seconds_experience = None

        self.ACTIVITY = None
        self.seconds_activity = None

        self.VIDEO = None
        self.seconds_video = None
    
    @staticmethod
    def ddhhmmss(seconds_natural: float):
        days = int(seconds_natural // 86400)
        rem = seconds_natural - days * 86400
        hours = int(rem // 3600)
        rem -= hours * 3600
        minutes = int(rem // 60)
        rem -= minutes * 60
        seconds = rem
        return f"{days:02d}-{hours:02d}:{minutes:02d}:{seconds:06.3f}"

    @staticmethod
    def human_time(seconds: float):
        days = int(seconds // 86400)
        rem = seconds - days * 86400
        hours = int(rem // 3600)
        rem -= hours * 3600
        minutes = int(rem // 60)
        rem -= minutes * 60
        whole_seconds = int(rem)
        frac = rem - whole_seconds
        frac_str = f"{frac:.2f}"[2:]  # remove leading '0.' keep 2 digits
        if days > 0:
            return f"D{days}-{hours:02d}h{minutes:02d}min{whole_seconds:02d}.{frac_str}s"
        elif hours > 0:
            return f"{hours:02d}h{minutes:02d}min{whole_seconds:02d}.{frac_str}s"
        elif minutes > 0:
            return f"{minutes:02d}min{whole_seconds:02d}.{frac_str}s"
        else:
            return f"{whole_seconds:02d}.{frac_str}s"

    def time_s(self, domain: str = 'experience'):
        if domain == 'experience':
            if self.seconds_experience is not None: return self.seconds_experience
            raise ValueError("Experience time not set")
        elif domain == 'activity':
            if self.seconds_activity is not None: return self.seconds_activity
            raise ValueError("Activity time not set")
        elif domain == 'video':
            if self.seconds_video is not None: return self.seconds_video
            raise ValueError("Video time not set")
        else:
            raise ValueError(f"Unknown domain: {domain}")

    def time_hu(self, domain: str = 'experience'):
        return TimeStamp.human_time(self.time_s(domain))
    
    def __str__(self):
        return self.time_hu('experience')

    def __repr__(self):
        return f"TimeStamp(EXPERIENCE_s={self.seconds_experience}, ACTIVITY_s={self.seconds_activity}, VIDEO_s={self.seconds_video}" + ((", N" + f"{self.seconds_natural}") if self.seconds_natural is not None else "") + ")"
    
    @classmethod
    def from_experience(cls, seconds, EXPERIENCE=None):
        ts = cls()
        ts.seconds_experience = seconds
        ts.EXPERIENCE = EXPERIENCE
        ts.seconds_natural = DEFAULT_EXPERIENCE_START_BASE + seconds  #assuming experience starts at 8:00 AM

        ACTIVITY = EXPERIENCE.get_activity_at_time(seconds)
        ts.ACTIVITY = ACTIVITY
        ts.seconds_activity = (seconds - ACTIVITY.STARTSTAMP) + ACTIVITY.STARTSTAMP.seconds_activity

        VIDEO = ACTIVITY.VIDEO.get_video_at_time(ts.seconds_activity)
        ts.VIDEO = VIDEO
        ts.seconds_video = (ts.seconds_activity - VIDEO.STARTSTAMP) + VIDEO.STARTSTAMP.seconds_video
        return ts
    
    @classmethod
    def from_activity(cls, seconds, ACTIVITY=None):
        ts = cls()
        ts.seconds_activity = seconds
        ts.ACTIVITY = ACTIVITY

        VIDEO = ACTIVITY.VIDEO.get_video_at_time(seconds)
        ts.VIDEO = VIDEO
        ts.seconds_video = (seconds - VIDEO.STARTSTAMP) + VIDEO.STARTSTAMP.seconds_video

        return ts

    @classmethod
    def by_concat(cls, ts_activity, start_experience_s, EXPERIENCE, ACTIVITY, VIDEO):
        ts = cls()
        ts.seconds_experience = start_experience_s + ts_activity.seconds_activity
        ts.seconds_natural = DEFAULT_EXPERIENCE_START_BASE + ts.seconds_experience  #assuming experience starts at 8:00 AM
        ts.EXPERIENCE = EXPERIENCE
        ts.ACTIVITY = ACTIVITY
        ts.seconds_activity = ts_activity.seconds_activity
        ts.VIDEO = VIDEO
        ts.seconds_video = ts_activity.seconds_video
        return ts


    def __sub__(self, other): #the result of sub is a "ABSOLUTE" seconds difference, regardless of the domain
        if not isinstance(other, TimeStamp):
            raise ValueError("Can only subtract TimeStamp from TimeStamp")
        # if self.EXPERIENCE is None or other.EXPERIENCE is None or self.EXPERIENCE != other.EXPERIENCE:
        #     raise ValueError("Experience mismatch in TimeStamp subtraction")
        return self.seconds_experience - other.seconds_experience

    def __lt__(self, other):
        if not isinstance(other, TimeStamp):
            raise ValueError("Can only compare TimeStamp with TimeStamp")
        # if self.EXPERIENCE is None or other.EXPERIENCE is None or self.EXPERIENCE != other.EXPERIENCE:
        #     raise ValueError("Experience mismatch in TimeStamp comparison")
        if self.seconds_experience is not None and other.seconds_experience is not None:
            return self.seconds_experience < other.seconds_experience
        elif self.seconds_activity is not None and other.seconds_activity is not None:
            return self.seconds_activity < other.seconds_activity
        elif self.seconds_video is not None and other.seconds_video is not None:
            return self.seconds_video < other.seconds_video
    
    def __gt__(self, other):
        if not isinstance(other, TimeStamp):
            raise ValueError("Can only compare TimeStamp with TimeStamp")
        # if self.EXPERIENCE is None or other.EXPERIENCE is None or self.EXPERIENCE != other.EXPERIENCE:
        #     raise ValueError("Experience mismatch in TimeStamp comparison")
        if self.seconds_experience is not None and other.seconds_experience is not None:
            return self.seconds_experience > other.seconds_experience
        elif self.seconds_activity is not None and other.seconds_activity is not None:
            return self.seconds_activity > other.seconds_activity
        elif self.seconds_video is not None and other.seconds_video is not None:
            return self.seconds_video > other.seconds_video
    
    def from_dict(self, data_dict, Video, Activity, Experience=None):
        self.seconds_natural = data_dict.get('seconds_natural_s', None)
        self.seconds_experience = data_dict.get('seconds_experience_s', None)
        self.seconds_activity = data_dict.get('seconds_activity_s', None)
        self.seconds_video = data_dict.get('seconds_video_s', None)

        self.EXPERIENCE = Experience
        self.ACTIVITY = Activity
        self.VIDEO = Video

    @property
    def to_dict(self):
        return {
            "seconds_natural_s": self.seconds_natural,
            "seconds_experience_s": self.seconds_experience,
            "seconds_activity_s": self.seconds_activity,
            "seconds_video_s": self.seconds_video
        }
    
    def offset_start(self, offset_s: float, EXPERIENCE):
        self.seconds_experience = self.seconds_activity + offset_s
        self.seconds_natural = DEFAULT_EXPERIENCE_START_BASE + self.seconds_experience  #assuming experience starts at 8:00 AM
        self.EXPERIENCE = EXPERIENCE
        
    def copy(self):
        ts = TimeStamp()
        ts.seconds_natural = self.seconds_natural
        ts.seconds_experience = self.seconds_experience
        ts.seconds_activity = self.seconds_activity
        ts.seconds_video = self.seconds_video
        ts.EXPERIENCE = self.EXPERIENCE
        ts.ACTIVITY = self.ACTIVITY
        ts.VIDEO = self.VIDEO
        return ts

    def template(self, seconds_experience_s: float):
        ts = TimeStamp()
        ts.seconds_experience = seconds_experience_s
        ts.EXPERIENCE = self.EXPERIENCE
        shift = seconds_experience_s - self.seconds_experience
        ts.seconds_natural = self.seconds_natural + shift if self.seconds_natural is not None else None
        ts.seconds_activity = self.seconds_activity + shift if self.seconds_activity is not None else None
        ts.ACTIVITY = self.ACTIVITY
        ts.seconds_video = self.seconds_video + shift if self.seconds_video is not None else None
        ts.VIDEO = self.VIDEO
        return ts

    def related_to(self, TS):  #self.related_to(TS), if TS is 2 seconds later than self (i.e., self<TS, TS-self=2), then say "2 seconds earlier"
        #give a string to describe the time relationship between self and TS
        if self < TS:
            return f"{TimeStamp.human_time(TS-self)} earlier"
        elif self > TS:
            return f"{TimeStamp.human_time(self-TS)} later"
        else:
            return "same time"

class TimeSpan:
    def __init__(self, start: TimeStamp, end: TimeStamp):
        # if start.EXPERIENCE != end.EXPERIENCE:
        #     raise ValueError("Experience mismatch in TimeSpan")
        # if start.seconds_experience > end.seconds_experience:
        #     raise ValueError("Start time must be less than or equal to end time in TimeSpan")
        self.STARTSTAMP = start
        self.ENDSTAMP = end

    @property
    def duration_s(self):
        if self.STARTSTAMP.seconds_experience is not None and self.ENDSTAMP.seconds_experience is not None and self.STARTSTAMP.EXPERIENCE == self.ENDSTAMP.EXPERIENCE: 
            return self.ENDSTAMP.seconds_experience - self.STARTSTAMP.seconds_experience
        if self.STARTSTAMP.seconds_activity is not None and self.ENDSTAMP.seconds_activity is not None and self.STARTSTAMP.ACTIVITY == self.ENDSTAMP.ACTIVITY:
            return self.ENDSTAMP.seconds_activity - self.STARTSTAMP.seconds_activity

    def format(self, domain: str = 'experience'):
        start_f = self.STARTSTAMP.time_hu(domain)
        end_f = self.ENDSTAMP.time_hu(domain)
        return f"[{start_f} -> {end_f}]"

    def __repr__(self):
        return f"TimeSpan(start={self.STARTSTAMP.seconds_experience}, end={self.ENDSTAMP.seconds_experience})"

    def __lt__(self, other):
        if self.STARTSTAMP.seconds_experience is not None and other.STARTSTAMP.seconds_experience is not None and self.STARTSTAMP.EXPERIENCE == other.STARTSTAMP.EXPERIENCE:
            return self.STARTSTAMP.seconds_experience < other.STARTSTAMP.seconds_experience or (self.STARTSTAMP.seconds_experience == other.STARTSTAMP.seconds_experience and self.duration_s < other.duration_s)
        if self.STARTSTAMP.seconds_activity is not None and other.STARTSTAMP.seconds_activity is not None and self.STARTSTAMP.ACTIVITY == other.STARTSTAMP.ACTIVITY:
            return self.STARTSTAMP.seconds_activity < other.STARTSTAMP.seconds_activity or (self.STARTSTAMP.seconds_activity == other.STARTSTAMP.seconds_activity and self.duration_s < other.duration_s)

    def __gt__(self, other):
        if self.STARTSTAMP.seconds_experience is not None and other.STARTSTAMP.seconds_experience is not None and self.STARTSTAMP.EXPERIENCE == other.STARTSTAMP.EXPERIENCE:
            return self.STARTSTAMP.seconds_experience > other.STARTSTAMP.seconds_experience or (self.STARTSTAMP.seconds_experience == other.STARTSTAMP.seconds_experience and self.duration_s > other.duration_s)
        if self.STARTSTAMP.seconds_activity is not None and other.STARTSTAMP.seconds_activity is not None and self.STARTSTAMP.ACTIVITY == other.STARTSTAMP.ACTIVITY:
            return self.STARTSTAMP.seconds_activity > other.STARTSTAMP.seconds_activity or (self.STARTSTAMP.seconds_activity == other.STARTSTAMP.seconds_activity and self.duration_s > other.duration_s)

    @classmethod
    def from_dict(cls, data_dict, VIDEOS, Activity, Experience=None):
        from .Video import Videos
        start_dict = data_dict.get('STARTSTAMP', {})
        end_dict = data_dict.get('ENDSTAMP', {})
        STARTSTAMP = TimeStamp()
        STARTSTAMP.from_dict(start_dict, None if VIDEOS is None else VIDEOS[0] if isinstance(VIDEOS, Videos) else VIDEOS, Activity, Experience)
        ENDSTAMP = TimeStamp()
        ENDSTAMP.from_dict(end_dict, None if VIDEOS is None else VIDEOS[-1] if isinstance(VIDEOS, Videos) else VIDEOS, Activity, Experience)
        return cls(STARTSTAMP, ENDSTAMP)
    
    @property
    def to_dict(self):
        return {
            "STARTSTAMP": self.STARTSTAMP.to_dict,
            "ENDSTAMP": self.ENDSTAMP.to_dict
        }
    
    def offset_start(self, offset_s: float, EXPERIENCE):
        self.STARTSTAMP.offset_start(offset_s, EXPERIENCE)
        self.ENDSTAMP.offset_start(offset_s, EXPERIENCE)
    
    def copy(self):
        return TimeSpan(self.STARTSTAMP.copy(), self.ENDSTAMP.copy())

    
    def related_to(self, TIMESTAMP):  #self.related_to(TS), if TS is 2 seconds later than self (i.e., self<TS, TS-self=2), then say "2 seconds earlier"
        #give a string to describe the time relationship between self and TS
        if type(TIMESTAMP) == TimeSpan:
            TIMESTAMP = TIMESTAMP.STARTSTAMP

        start_diff = self.STARTSTAMP - TIMESTAMP
        end_diff = self.ENDSTAMP - TIMESTAMP
        if abs(start_diff) < 1e-3:
            return f"from current time to {TimeStamp.human_time(end_diff)} later"
        elif abs(end_diff) < 1e-3:
            return f"from {TimeStamp.human_time(-start_diff)} earlier to current time"
        elif start_diff > 0 and end_diff > 0:
            return f"from {TimeStamp.human_time(start_diff)} later to {TimeStamp.human_time(end_diff)} later"
        elif start_diff < 0 and end_diff < 0:
            return f"from {TimeStamp.human_time(-start_diff)} earlier to {TimeStamp.human_time(-end_diff)} earlier"
        else:
            return f"from {TimeStamp.human_time(-start_diff)} earlier to {TimeStamp.human_time(end_diff)} later"