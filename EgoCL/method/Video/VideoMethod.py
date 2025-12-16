from ..Base import Method

class VideoMethod(Method):
    def __init__(self, EXPERIENCE, **kwargs):
        super().__init__()
        self.name = "VideoMethod"
        self.EXPERIENCE = EXPERIENCE
        from . import VideoMemorize, VideoRespond
        self.MEMORIZER = VideoMemorize(self, **kwargs)
        self.EXECUTION = kwargs.get("EXECUTION", None)
        self.RESPOND = VideoRespond(self, **kwargs)
    
    @property
    def atom_s(self):
        return self.MEMORIZER.atom_s
    
    @property
    def num_segments(self):
        return self.MEMORIZER.num_segments

    @property
    def fps(self):
        return self.MEMORIZER.fps

    @property
    def MODEL(self):
        return self.MEMORIZER.MODEL

    @property
    def TIME(self):
        return self.MEMORIZER.TIME
    
    @property
    def MEMORY(self):
        return self.MEMORIZER.MEMORY

    def progress(self, start_s, end_s):
        for current_s in self.EXPERIENCE.iterate_time(step_s=self.atom_s, start_s=start_s, end_s=end_s):
            self.MEMORIZER(start_s=current_s, end_s=current_s + self.atom_s)
    
    def query(self, query):#first check the self.RESPOND.TIME and self.TIME
        print(self.RESPOND.TIME.seconds_experience, "self.RESPOND.TIME.seconds_experience")
        print(self.TIME.seconds_experience, "self.TIME.seconds_experience")
        
        if self.RESPOND.TIME.seconds_experience < self.TIME.seconds_experience:
            self.MEMORIZER.save()
            self.RESPOND.load(self.TIME.seconds_experience)

        s = self.RESPOND(query)
        print("VideoMethod response:", s)
        return s