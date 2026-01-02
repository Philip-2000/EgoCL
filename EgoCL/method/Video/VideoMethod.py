from ..Base import Method
from . import YOG
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

    def load(self, ckpt):
        return self.MEMORIZER.load(ckpt)

    def progress(self, start_s, end_s):
        for s_s, e_s in self.EXPERIENCE.iterate_time(step_s=self.atom_s, start_s=start_s, end_s=end_s):
            self.MEMORIZER(start_s=s_s, end_s=e_s)
    
    def query(self, query):#first check the self.RESPOND.TIME and self.TIME
        if self.RESPOND.TIME.seconds_experience < self.TIME.seconds_experience:
            self.MEMORIZER.save()
            self.RESPOND.load(self.TIME.seconds_experience)

        s = self.RESPOND(query)
        YOG.info(("VideoMethod response:", s))
        return s