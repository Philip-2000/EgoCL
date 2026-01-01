from . import YOG
from ...Base import Memorize

class VideoMemorize(Memorize):
    def __init__(self, METHOD, **kwargs):
        super().__init__()
        self.name = "VideoMemorize"
        self.METHOD = METHOD

        from . import VideoMemory
        self.MEMORY = VideoMemory(self, **kwargs)

        self.VideoBufferSize = kwargs.get("VideoBufferSize", 1024)
        self.VideoBufferState= 0
        self.MODEL = kwargs.get("MODEL", "Qwen3-VL-8B-Instruct") 
        self.width = kwargs.get("width", 1080)         #resize width for video understanding
        self.FPS = kwargs.get("FPS", 2)  #frame rate when we concatenate these frames into a NEW video, ONLY for video understanding model calls, such video's framerate is usually high, much higher than original video, in order to save space
        self.I_Cant_See = kwargs.get("I_Cant_See", True) #False) #

        
        self.strategy = {
            "segment": {
                "adjust": kwargs.get("strategy",{}).get("segment", {}).get("adjust", "None"),
                "split": kwargs.get("strategy",{}).get("segment", {}).get("split", "Force"),
            },
            "memory": {
                "adjust": kwargs.get("strategy",{}).get("memory", {}).get("adjust", "None"),
                "split": kwargs.get("strategy",{}).get("memory", {}).get("split", "None"),
            }
        }
        #策略是两方面，顶层方面是：第一这个站在Memory的角度之下，是否需要调节各个Segment中的Clip的划分位置；第二这个站在Memory的角度之下，是否需要将最后一个Segment划分成两个Segment
        #底层方面是：第一这个站在Segment的角度之下，是否需要调节各个Clip中的Atom的划分位置；第二这个站在Segment的角度之下，是否需要将最后一个Clip划分成两个Clip


    @property
    def atom_s(self):
        return self.MEMORY.atom_s
    
    @property
    def num_segments(self):
        return self.MEMORY.num_segments

    @property
    def EXPERIENCE(self):
        return self.METHOD.EXPERIENCE
    
    @property
    def TIME(self):
        return self.MEMORY.TIME

    def save(self):
        self.MEMORY.save()
    
    def __s2timespan(self, start_s, end_s):
        from ....data.elements import TimeSpan, TimeStamp
        STARTTIMESTAMP = TimeStamp()
        STARTTIMESTAMP.EXPERIENCE = self.EXPERIENCE
        STARTTIMESTAMP.seconds_experience = start_s
        ENDTIMESTAMP = TimeStamp()
        ENDTIMESTAMP.EXPERIENCE = self.EXPERIENCE
        ENDTIMESTAMP.seconds_experience = end_s
        TIMESPAN = TimeSpan(STARTTIMESTAMP, ENDTIMESTAMP)
        return TIMESPAN
    
    def content(self, **kwargs):
        if not self.EXPERIENCE.EGO:
            from .. import MEMORIZE_PROMPT_SIMPLE as MEMORIZE_PROMPT
        else:
            from .. import MEMORIZE_PROMPT
        if "transcripts" in kwargs and len(kwargs["transcripts"]) > 0:
            TRANSCRIPT = "\nHere is the transcript of the following video segment:\n" + "\n".join(kwargs["transcripts"])
        else:     
            TRANSCRIPT = ""
        return [
            {"text": MEMORIZE_PROMPT(self.MEMORY.MEMORY_CONTEXT) + TRANSCRIPT},
            {"video": kwargs.get("video_cache_path", "")},
        ]

    def __cache_video(self, clip, start_s, end_s):
        import os
        from ... import CACHE_DIR
        os.makedirs(CACHE_DIR, exist_ok=True)
        video_cache_path = os.path.join(CACHE_DIR, f"{self.EXPERIENCE.name}_{self.name}_{int(start_s)}_{int(end_s)}_cache={self.VideoBufferState}.mp4")
        search = [f for f in os.listdir(CACHE_DIR) if f.startswith(f"{self.EXPERIENCE.name}_{self.name}_") and f.endswith(f"_cache={self.VideoBufferState}.mp4")]
        if len(search) > 0: #remove such cache file first
            os.remove(os.path.join(CACHE_DIR, search[0]))
        
        #clip.write_videofile(video_cache_path, codec="libx264", audio_codec="aac", logger=None, fps=self.num_segments / self.atom_s)
        #change the following line to, get the frames at 0/self.num_segments, 1/self.num_segments, 2/self.num_segments...... (self.num_segments-1)/self.num_segments time position of "clip", whose length is self.atom_s, and concatenate them with a frame rate of 2, as a new clip, and then save that clip
        from moviepy import concatenate_videoclips, ImageClip
        frame_clips = []
        for i in range(self.num_segments):
            t = (i / self.num_segments) * (end_s - start_s)
            frame = clip.get_frame(t)
            ratio = frame.shape[1] / frame.shape[0]
            img_clip = ImageClip(frame).with_duration(1/self.FPS)
            img_clip = img_clip.resized((self.width, int(self.width * ratio)))
            frame_clips.append(img_clip)
        sampled_clip = concatenate_videoclips(frame_clips, method="compose")
        sampled_clip.write_videofile(video_cache_path, codec="libx264", audio_codec="aac", logger=None, fps=self.FPS)
                
        YOG.debug(f"Video cached at {video_cache_path}", tag="Video Caching")
        self.VideoBufferState = (self.VideoBufferState + 1) % self.VideoBufferSize
        return video_cache_path

    def humanize_time(self, seconds):
        import time
        return time.strftime("%H:%M:%S", time.gmtime(seconds))
    
    def call(self, *args, **kwargs):
        from MyLm import call
        return call(self.MODEL, *args, **kwargs)

    def transform_transcripts(self, transcripts):
        # transcripts is a list of pysrts.Subtitle, please convert it to time + text
        # convert to text
        text_list = []
        for subtitle in transcripts:
            start_time = subtitle.start.to_time()
            end_time = subtitle.end.to_time()
            #the start_time and end_time are datetime.time object, convert them to string
            start_time = f"{start_time.minute:01d}min{start_time.second:02d}s"
            end_time = f"{end_time.minute:01d}min{end_time.second:02d}s"
            text = subtitle.text.replace("\n", " ")
            text_list.append(f"[{start_time}-{end_time}] {text}")
        return text_list
    
    def natural_string(self, seconds):
        #result should be as DAY?_hh:mm:ss
        import time
        days = seconds // 86400
        remainder = seconds % 86400
        time_str = time.strftime("%H:%M:%S", time.gmtime(remainder))
        return f"Day{int(days)+1}_{time_str}"

    def __call__(self, start_s, end_s):
        TIMESTAMPS = self.EXPERIENCE.time_to_timestamps(start_s, end_s)
        STARTSTAMP = TIMESTAMPS[0]
        START_NATURAL = self.natural_string(STARTSTAMP.seconds_natural)


        clip, transcripts = self.EXPERIENCE.time_to_video(start_s, end_s)
        transcripts = self.transform_transcripts(transcripts)
        
        #if clip is None: return
        end_s = min(end_s, start_s + clip.duration)  #just in case that the clip is shorter
        video_cache_path = self.__cache_video(clip, start_s, start_s + clip.duration)
        import time
        timer_start = time.time()
        if self.I_Cant_See:
            summary = "fake response"
        else:
            summary = self.call({"content": self.content(video_cache_path=video_cache_path, transcripts=transcripts), "num_segments": self.num_segments})
            YOG.debug(("Time at", start_s, "to", end_s, "num_segments=", self.num_segments, "VideoMemorize summary:", summary), tag="VideoMemorize")
            one_time = time.time() - timer_start
            total_time = one_time * (self.EXPERIENCE.duration_s / (end_s - start_s))
            total_time_humanized = self.humanize_time(total_time)
            YOG.info(("Time at", start_s, "to", end_s,
                "cached at ", video_cache_path, "Time cost for VideoMemorize model call:", round(one_time, 3),
                "seconds, estimated total time for full video:", total_time_humanized, 
                "ratio than the video time is ", round(total_time / self.EXPERIENCE.duration_s, 2)), tag="VideoMemorize")
            timer_start = time.time()
        
        metaa = {
            "start_natural": START_NATURAL,
            #"video_cache_path": video_cache_path,
        }
        if transcripts is not None and len(transcripts) > 0: metaa["transcripts"] = transcripts
        self.MEMORY(clip, self.__s2timespan(start_s, end_s), summary, meta=metaa)

        #MEMORIZE方法用于处理信息，例如调用模型进行总结
        #MEMORY用于存储处理后的信息