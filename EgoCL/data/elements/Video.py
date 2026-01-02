import cv2

from .TimeStamp import TimeStamp, TimeSpan

class Video:
    def __init__(self, config={}, s_ACTIVITY=None):
        self.path = config.get('video_path', 'unknown_path.mp4')
        self.TIMESPAN = TimeSpan(TimeStamp(), TimeStamp())
        self.TIMESPAN.from_dict(config.get('TIMESPAN', {}), self, s_ACTIVITY)
        self.clip_id = config.get('clip_id', "")
        self.config = config
        self.s_ACTIVITY = s_ACTIVITY
        self.offset_s = 0.0
        self.transcript_path = config.get('transcript_path', 'unknown_path.srt')
    
    def offset_start(self, start_s: float, EXPERIENCE):
        self.TIMESPAN.offset_start(start_s, EXPERIENCE)
    
    @property
    def start_s(self):
        return self.TIMESPAN.STARTSTAMP.seconds_experience
    
    @property
    def end_s(self):
        return self.TIMESPAN.ENDSTAMP.seconds_experience

    def __call__(self, t):
        raise NotImplementedError
        return False
        if isinstance(t, int):
            return self[t-self.offset_s]
        elif isinstance(t, tuple) and len(t) == 2:
            c = self.config.copy()
            c['start_s'], c['end_s'] = t[0]-self.offset_s, t[1]-self.offset_s #???????????
            return Video(c, self.s_ACTIVITY)

    def __getitem__(self, t):
        raise NotImplementedError
        return False
        if isinstance(t, int):
            # get frame at second t (relative to self.start_s)
            cap = cv2.VideoCapture(self.path)
            if not cap.isOpened():
                raise IOError(f'Cannot open video: {self.path}')

            target_s = float(self.start_s + t) #FIXME
            # seek by milliseconds
            cap.set(cv2.CAP_PROP_POS_MSEC, target_s * 1000.0)
            ret, frame = cap.read()
            cap.release()

            if not ret or frame is None:
                raise IndexError(f'Could not read frame at {target_s}s from {self.path}')

            # convert BGR (OpenCV) -> RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return frame
        elif isinstance(t, tuple) and len(t) == 2:
            c = self.config.copy()
            c['start_s'], c['end_s'] = t[0], t[1]
            return Video(c, self.s_ACTIVITY)

    def __repr__(self):
        return f'Video(path={self.path}, activity={self.s_ACTIVITY.name})'
    
    @property
    def to_dict(self):
        return {
            'video_path': self.path,
            'TIMESPAN': self.TIMESPAN.to_dict,
            'clip_id': self.clip_id,
            'transcript_path': self.transcript_path
        }
    
    def from_dict(self, data_dict):
        self.path = data_dict.get('video_path', 'unknown_path.mp4')
        self.transcript_path = data_dict.get('transcript_path', 'unknown_path.srt')
        import pysrt
        self.transcripts = pysrt.open(self.transcript_path) if self.transcript_path != 'unknown_path.srt' else []
        self.TIMESPAN = TimeSpan(TimeStamp(), TimeStamp())
        self.TIMESPAN.from_dict(data_dict.get('TIMESPAN', {}), self, self.s_ACTIVITY)
        self.clip_id = data_dict.get('clip_id', "")
        self.config = data_dict
    
    @property
    def duration_s(self):
        return self.TIMESPAN.duration_s

    def clip(self, start_s: float, end_s: float):
        raise NotImplementedError
        c = self.config.copy()
        c['start_s'] = start_s
        c['end_s'] = end_s
        return Video(c, self.s_ACTIVITY)
    

class Videos:
    def __init__(self, videos_list=[], s_ACTIVITY=None):
        self.VIDEOS = [Video(v_config, s_ACTIVITY) for v_config in videos_list]
        self.s_ACTIVITY = s_ACTIVITY

    def offset_start(self, start_s: float, EXPERIENCE):
        for VIDEO in self.VIDEOS: VIDEO.TIMESPAN.offset_start(start_s, EXPERIENCE)

    @property
    def STARTSTAMP(self):
        if len(self.VIDEOS) == 0:
            return TimeStamp()
        return min([video.TIMESPAN.STARTSTAMP for video in self.VIDEOS])
    
    @property
    def ENDSTAMP(self):
        if len(self.VIDEOS) == 0:
            return TimeStamp()
        return max([video.TIMESPAN.ENDSTAMP for video in self.VIDEOS])

    @property
    def TIMESPAN(self):
        return TimeSpan(self.STARTSTAMP, self.ENDSTAMP)
    
    @property
    def duration_s(self):
        return self.TIMESPAN.duration_s
    
    def __iadd__(self, video):
        self.VIDEOS.append(video)
        return self
    
    def __getitem__(self, index):
        if isinstance(index, slice):
            return Videos(self.VIDEOS[index])
        elif isinstance(index, int):
            return self.VIDEOS[index]
        elif isinstance(index, str):
            for video in self.VIDEOS:
                if video.clip_id == index:
                    return video
            return None
        
    @property
    def to_dict(self):
        return [VIDEO.to_dict for VIDEO in self.VIDEOS]
    
    def from_dict(self, data_list):
        self.VIDEOS = []
        for video_dict in data_list:
            v = Video()
            v.from_dict(video_dict)
            self.VIDEOS.append(v)
        
    def __iter__(self):
        return iter(self.VIDEOS)
    
    def __len__(self):
        return len(self.VIDEOS)