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
    def VlmBase(self):
        return self.RESPOND.VlmBase

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
        import time
        timer_start = time.time()
        one_time_avg, tiny_time_avg = (0,0), (0,0)
        for s_s, e_s in self.EXPERIENCE.iterate_time(step_s=self.atom_s, start_s=start_s, end_s=end_s):
            time_log = self.MEMORIZER(start_s=s_s, end_s=e_s)
            
            one_time = time.time() - timer_start
            remain_time = one_time * (self.EXPERIENCE.duration_s - e_s) / (e_s - s_s)
            remain_time_humanized = time.strftime("%H:%M:%S", time.gmtime(remain_time))
            YOG.info((f"Time log for segment {s_s}-{e_s}: {time_log}"), tag="VideoMemorize")
            YOG.info(("Time at", s_s, "to", e_s, #"cached at ", video_cache_path,
                "Time cost for VideoMemorize model call:", round(one_time, 3),
                "seconds, estimated remain time:", remain_time_humanized, 
                "ratio than the video:", round(remain_time / max(self.EXPERIENCE.duration_s - e_s, 1e-2), 2)), tag="VideoMemorize")
            timer_start = time.time()

            one_time_avg = ((one_time_avg[0] * one_time_avg[1] + one_time) / (one_time_avg[1] + 1), one_time_avg[1] + 1)
            tiny_time_avg = ((tiny_time_avg[0] * tiny_time_avg[1] + time_log["summarization"]) / (tiny_time_avg[1] + 1), tiny_time_avg[1] + 1)
            YOG.debug(f"Average time per MEMORIZER call: {one_time_avg[0]:.3f}s over {one_time_avg[1]} calls; Average time per tiny segment: {tiny_time_avg[0]:.3f}s over {tiny_time_avg[1]} calls")

    
    def query(self, query):#first check the self.RESPOND.TIME and self.TIME
        if self.RESPOND.TIME.seconds_experience < self.TIME.seconds_experience:
            self.MEMORIZER.save()
            self.RESPOND.load(self.TIME.seconds_experience)

        s = self.RESPOND(query)
        YOG.info(("VideoMethod response:", s))
        return s