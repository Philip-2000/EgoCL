from ....Base import Memory
from .....data.elements import TimeSpan, TimeStamp

class VideoMemAtom:
    #the basic unit of video memory, whose time span never changes, as a short time span, and the shortest time span
    #about 10 seconds ~ 30 seconds
    def __init__(self, data, meta, CLIP):
        self.TIMESPAN=None
        self.data = data
        self.meta = meta
        self.CLIP = CLIP
    
    def __repr__(self):
        return f"\t\t\t<VideoMemAtom: from {self.TIMESPAN.STARTSTAMP.seconds_experience}s to {self.TIMESPAN.ENDSTAMP.seconds_experience}s, data: {self.data}, meta: {self.meta}>"

    @property
    def SEGMENT(self):
        return self.CLIP.SEGMENT

    @property
    def MEMORY(self):
        return self.CLIP.MEMORY
    
    @property
    def EXPERIENCE(self):
        return self.CLIP.EXPERIENCE
    
    @property
    def ENCODER(self):
        return self.CLIP.ENCODER
    
    def encode(self, s):
        return self.CLIP.encode(s)

    @property
    def METHOD(self):
        return self.CLIP.METHOD
    
    @property
    def MODEL(self):
        return self.CLIP.MODEL
    
    def from_dict(self, dict_data):
        self.TIMESPAN = TimeSpan(TimeStamp(), TimeStamp())
        self.TIMESPAN.from_dict(dict_data['TIMESPAN'], None, None)
        self.data = dict_data['data']
        self.meta = dict_data['meta']
        return self
    
    @property
    def to_dict(self):
        return {
            'TIMESPAN': self.TIMESPAN.to_dict,
            'data': self.data,
            'meta': self.meta
        }
    
class VideoMemClip:    
    def __init__(self, SEGMENT):
        self.meta = {}
        self.data = ""
        self.VIDEO_MEM_ATOMS = []
        self.SEGMENT = SEGMENT
    
    def __len__(self):
        return len(self.VIDEO_MEM_ATOMS)
    
    def __repr__(self):
        return f"\t\t<VideoMemClip: {len(self)} atoms, from {self.TIMESPAN.STARTSTAMP.seconds_experience}s to {self.TIMESPAN.ENDSTAMP.seconds_experience}s>\n" + "\n".join([atom.__repr__() for atom in self.VIDEO_MEM_ATOMS])

    @property
    def EXPERIENCE(self):
        return self.MEMORY.EXPERIENCE

    @property
    def MEMORY(self):
        return self.SEGMENT.MEMORY

    @property
    def EXPERIMENT(self):
        return self.SEGMENT.EXPERIMENT
    
    @property
    def ENCODER(self):
        return self.SEGMENT.ENCODER

    def encode(self, s):
        return self.SEGMENT.encode(s)

    @property
    def METHOD(self):
        return self.SEGMENT.METHOD

    @property
    def strategy(self):
        return self.MEMORY.MEMORIZER.strategy["clip"]
    
    @property
    def MODEL(self):
        return self.SEGMENT.MODEL
    
    def call(self, *args, **kwargs):
        return self.SEGMENT.call(*args, **kwargs)
    
    def tall(self, *args, **kwargs):
        return self.SEGMENT.tall(*args, **kwargs)

    @property
    def TIMESPAN(self): #in such TIMESPAN, only seconds_experience is allowed, because Memory is only related to Experience time and it cannot see the video time or activity information
        TIMESPAN = TimeSpan(TimeStamp(), TimeStamp())
        TIMESPAN.STARTSTAMP.seconds_experience = self.VIDEO_MEM_ATOMS[0].TIMESPAN.STARTSTAMP.seconds_experience
        TIMESPAN.STARTSTAMP.EXPERIENCE = self.VIDEO_MEM_ATOMS[0].TIMESPAN.STARTSTAMP.EXPERIENCE
        TIMESPAN.ENDSTAMP.seconds_experience = self.VIDEO_MEM_ATOMS[-1].TIMESPAN.ENDSTAMP.seconds_experience
        TIMESPAN.ENDSTAMP.EXPERIENCE = self.VIDEO_MEM_ATOMS[-1].TIMESPAN.ENDSTAMP.EXPERIENCE
        return TIMESPAN

    def from_dict(self, dict_data):
        self.meta = dict_data['meta']
        self.data = dict_data['data']
        self.VIDEO_MEM_ATOMS = [VideoMemAtom(None, None, self).from_dict(atom_dict) for atom_dict in dict_data['VIDEO_MEM_ATOMS']]
        return self

    @property
    def to_dict(self):
        return {
            "meta": self.meta,
            "data": self.data,
            "TIMESPAN": self.TIMESPAN.to_dict if len(self.VIDEO_MEM_ATOMS) > 0 else None,
            'VIDEO_MEM_ATOMS': [ atom.to_dict for atom in self.VIDEO_MEM_ATOMS ]
        }
    
    def pop_front_atom(self):
        first = self.VIDEO_MEM_ATOMS[0]
        self.VIDEO_MEM_ATOMS = self.VIDEO_MEM_ATOMS[1:]
        return first
    
    def push_front_atom(self, atom):
        self.VIDEO_MEM_ATOMS = [atom] + self.VIDEO_MEM_ATOMS
        atom.CLIP = self

    def pop_back_atom(self):
        last = self.VIDEO_MEM_ATOMS[-1]
        self.VIDEO_MEM_ATOMS = self.VIDEO_MEM_ATOMS[:-1]
        return last

    def push_back_atom(self, atom):
        self.VIDEO_MEM_ATOMS.append(atom)
        atom.CLIP = self

    def summarize(self):
        # self.meta["summary"] = self.VIDEO_MEM_ATOMS[-1].data #FIXME: Shortcutting atom manipulation among and in clips
        # return #FIXME: Shortcutting atom manipulation among and in clips
        if self.strategy.get("summarize") == "Concat":
            self.meta["summary"] = "\n".join([atom.data for atom in self.VIDEO_MEM_ATOMS])
        elif self.strategy.get("summarize") == "Summary":
            if not self.EXPERIENCE.EGO:
                from ... import SUMMARIZE_CLIP_PROMPT_SIMPLE as SUMMARIZE_CLIP_PROMPT
            else:
                from ... import SUMMARIZE_CLIP_PROMPT
            SYSTEM_PROMPT, USER_PROMPT = SUMMARIZE_CLIP_PROMPT(self)
            # print(f"Summarizing clip with prompt: {PROMPT}")
            self.meta["summary"] = self.tall({"content": [{"system":SYSTEM_PROMPT},{"user":USER_PROMPT}]})
            print(self.meta["summary"])
        elif self.strategy.get("summarize") == "Empty":
            self.meta["summary"] = ""
        else:
            raise ValueError(f"Unknown summarize strategy: {self.strategy.get('summarize')}")
        #self.data += "\n" + self.VIDEO_MEM_ATOMS[-1].data
        #self.meta["description"] = f"VideoMemClip from {self.TIMESPAN.STARTSTAMP.seconds_experience} to {self.TIMESPAN.ENDSTAMP.seconds_experience}, containing {len(self.VIDEO_MEM_ATOMS)} atoms."
        #FIXME: such meta["description"] should be a LLM generated summary of the clip content, but for now we just put a simple description here.
        #does some figures should be saved here too?
    
    @property
    def structure(self):
        return f"({len(self)})"
    
    def __getitem__(self, index):
        return self.VIDEO_MEM_ATOMS[index] if isinstance(index, int) else self.VIDEO_MEM_ATOMS[index[0]]


class VideoMemSegment:
    #longer clip of video memory, containing several VideoMemClips, containing a whole activity
    #longer than VideoMemClip, about 5 minutes ~ 30 minutes, and
    # shorter than the whole Experience
    def __init__(self, MEMORY):
        self.meta = {}
        self.data = ""
        self.VIDEO_MEM_CLIPS = []
        self.MEMORY = MEMORY
    
    def __len__(self):
        return len(self.VIDEO_MEM_CLIPS)
    
    def __repr__(self):
        return f"\t<VideoMemSegment: {len(self)} clips, {self.len_atoms} atoms, from {self.TIMESPAN.STARTSTAMP.seconds_experience}s to {self.TIMESPAN.ENDSTAMP.seconds_experience}s>\n" + "\n".join([clip.__repr__() for clip in self.VIDEO_MEM_CLIPS])
    
    @property
    def len_atoms(self):
        return sum([len(clip) for clip in self.VIDEO_MEM_CLIPS])
    
    @property
    def strategy(self):
        return self.MEMORY.MEMORIZER.strategy["segment"]

    @property
    def EXPERIENCE(self):
        return self.MEMORY.EXPERIENCE
    
    @property
    def EXPERIMENT(self):
        return self.MEMORY.EXPERIMENT

    @property
    def ENCODER(self):
        return self.MEMORY.ENCODER
    
    def encode(self, s):
        return self.MEMORY.encode(s)

    @property
    def METHOD(self):
        return self.MEMORY.METHOD
    
    @property
    def MODEL(self):
        return self.MEMORY.MODEL
    
    def call(self, *args, **kwargs):
        return self.MEMORY.call(*args, **kwargs)

    def tall(self, *args, **kwargs):
        return self.MEMORY.tall(*args, **kwargs)

    @property
    def TIMESPAN(self):
        TIMESPAN = TimeSpan(TimeStamp(), TimeStamp())
        TIMESPAN.STARTSTAMP.seconds_experience = self.VIDEO_MEM_CLIPS[0].TIMESPAN.STARTSTAMP.seconds_experience
        TIMESPAN.STARTSTAMP.EXPERIENCE = self.VIDEO_MEM_CLIPS[0].TIMESPAN.STARTSTAMP.EXPERIENCE
        TIMESPAN.ENDSTAMP.seconds_experience = self.VIDEO_MEM_CLIPS[-1].TIMESPAN.ENDSTAMP.seconds_experience
        TIMESPAN.ENDSTAMP.EXPERIENCE = self.VIDEO_MEM_CLIPS[-1].TIMESPAN.ENDSTAMP.EXPERIENCE
        return TIMESPAN
    
    def from_dict(self, dict_data):
        self.meta = dict_data['meta']
        self.data = dict_data['data']
        self.VIDEO_MEM_CLIPS = [VideoMemClip(self).from_dict(clip_dict) for clip_dict in dict_data['VIDEO_MEM_CLIPS']]
        return self

    @property
    def to_dict(self):
        return {
            "meta": self.meta,
            "data": self.data,
            "TIMESPAN": self.TIMESPAN.to_dict if len(self.VIDEO_MEM_CLIPS) > 0 else None,
            'VIDEO_MEM_CLIPS': [ clip.to_dict for clip in self.VIDEO_MEM_CLIPS ]
        }
    
    def pop_front_clip(self):
        first = self.VIDEO_MEM_CLIPS[0]
        self.VIDEO_MEM_CLIPS = self.VIDEO_MEM_CLIPS[1:]
        return first
    
    def push_front_clip(self, clip):
        self.VIDEO_MEM_CLIPS = [clip] + self.VIDEO_MEM_CLIPS
        clip.SEGMENT = self
    
    def pop_back_clip(self):
        last = self.VIDEO_MEM_CLIPS[-1]
        self.VIDEO_MEM_CLIPS = self.VIDEO_MEM_CLIPS[:-1]
        return last
    
    def push_back_clip(self, clip):
        self.VIDEO_MEM_CLIPS.append(clip)
        clip.SEGMENT = self

    def append_atom(self, atom):
        if len(self.VIDEO_MEM_CLIPS) == 0 or True: #FIXME: Shortcutting atom manipulation among and in clips
            self.VIDEO_MEM_CLIPS.append(VideoMemClip(self))
        self.VIDEO_MEM_CLIPS[-1].push_back_atom(atom)
        atom.CLIP = self.VIDEO_MEM_CLIPS[-1]
    
    def adjust(self):
        return [] #FIXME: Shortcutting atom manipulation among and in clips
        #(1.1) 需要考虑这个clip中的atom配置是否合理，就是首先是否需要和上一个clip调整atom的切割位置（segment.adjust）
        if len(self.VIDEO_MEM_CLIPS) == 1: return []
        from ... import SEGMENT_ADJUST_CLIP_PROMPT
        SYSTEM_PROMPT, USER_PROMPT = SEGMENT_ADJUST_CLIP_PROMPT(self.VIDEO_MEM_CLIPS[-2], self.VIDEO_MEM_CLIPS[-1])
        advice = self.tall({"content": [{"system":SYSTEM_PROMPT},{"user":USER_PROMPT}]})
        import re
        adjustment_match = re.search(r"<adjust>(-?\d+)</adjust>", advice)
        if adjustment_match:
            adjustment = int(adjustment_match.group(1))
            if adjustment != 0:
                if adjustment > 0:
                    # print("Adjusting segments by", adjustment)
                    #move atoms from last clip to second last clip
                    for _ in range(adjustment):
                        atom = self.VIDEO_MEM_CLIPS[-1].pop_front_atom()
                        self.VIDEO_MEM_CLIPS[-2].push_back_atom(atom)
                else:
                    # print("Adjusting segments by", adjustment)
                    #move atoms from second last clip to last clip
                    for _ in range(-adjustment):
                        atom = self.VIDEO_MEM_CLIPS[-2].pop_back_atom()
                        self.VIDEO_MEM_CLIPS[-1].push_front_atom(atom)
                return [len(self.VIDEO_MEM_CLIPS)-2, len(self.VIDEO_MEM_CLIPS)-1]
        # print("No adjustment needed")
        return []

    def separate(self):
        return [len(self.VIDEO_MEM_CLIPS)-1] #FIXME: Shortcutting atom manipulation among and in clips
        #(1.2) 其次是当前这个clip中的atom们是否需要切成两份，后面一份形成新的clip（segment.separate）
        CLIP = self.VIDEO_MEM_CLIPS[-1]
        from ... import SEGMENT_SEPARATE_CLIP_PROMPT
        SYSTEM_PROMPT, USER_PROMPT = SEGMENT_SEPARATE_CLIP_PROMPT(CLIP)
        advice = self.tall({"content": [{"system":SYSTEM_PROMPT},{"user":USER_PROMPT}]})
        import re
        separate_match = re.search(r"<separate>(\d+|X)</separate>", advice)
        clip_id_sets, separate_index = [], None
        if separate_match:
            separate_index = separate_match.group(1)
            if separate_index != "X":
                separate_index = int(separate_index)
                if 1 <= separate_index < len(CLIP.VIDEO_MEM_ATOMS):
                    new_clip = VideoMemClip(SEGMENT=self)
                    new_clip.VIDEO_MEM_ATOMS = CLIP.VIDEO_MEM_ATOMS[separate_index:]
                    CLIP.VIDEO_MEM_ATOMS = CLIP.VIDEO_MEM_ATOMS[:separate_index]
                    self.VIDEO_MEM_CLIPS.append(new_clip)
                    clip_id_sets = [len(self.VIDEO_MEM_CLIPS)-2, len(self.VIDEO_MEM_CLIPS)-1]
        
        # print(f"Separating clip at index {separate_index}" if len(clip_id_sets) > 0 else "No separation needed")
        return clip_id_sets

    def separate_force(self):
        CLIP = self.VIDEO_MEM_CLIPS[-1]
        if len(CLIP.VIDEO_MEM_ATOMS) <= 1:
            # print("No separation needed, only one atom in clip.")
            return [-1]
        # print("Separating clip, ", 1, "atoms will be moved to new clip, remaining ", len(CLIP.VIDEO_MEM_ATOMS)-1, "atoms in current clip.")
        new_clip = VideoMemClip(SEGMENT=self)
        ATOM = CLIP.pop_back_atom()
        new_clip.push_front_atom(ATOM)
        self.VIDEO_MEM_CLIPS.append(new_clip)
        return [len(self.VIDEO_MEM_CLIPS)-2, len(self.VIDEO_MEM_CLIPS)-1]
    

    def summarize(self):
        if self.strategy.get("summarize") == "Concat":
            self.meta["summary"] = "\n".join([clip.meta.get("summary","") for clip in self.VIDEO_MEM_CLIPS])
        elif self.strategy.get("summarize") == "Summary":
            if not self.EXPERIENCE.EGO:
                from ... import SUMMARIZE_SEGMENT_PROMPT_SIMPLE as SUMMARIZE_SEGMENT_PROMPT
            else:
                from ... import SUMMARIZE_SEGMENT_PROMPT
            SYSTEM_PROMPT, USER_PROMPT = SUMMARIZE_SEGMENT_PROMPT(self)
            # print(f"Summarizing segment with prompt: {PROMPT}")
            self.meta["summary"] = self.tall({"content": [{"system":SYSTEM_PROMPT},{"user":USER_PROMPT}]})
        elif self.strategy.get("summarize") == "Empty":
            self.meta["summary"] = ""
        else:
            raise ValueError(f"Unknown summarize strategy: {self.strategy.get('summarize')}")

    def organize(self):
        clip_id_set, clip_id_sets = [], []
        if self.strategy.get("adjust") == "Try":
            clip_id_set = self.adjust()
        if self.strategy.get("split") == "Try":
            clip_id_sets = self.separate()
        elif self.strategy.get("split") == "Force":
            clip_id_sets = self.separate_force()

        if self.strategy.get("adjust") == "None" and self.strategy.get("split") == "Force":
            self.VIDEO_MEM_CLIPS[-1].summarize()
        else:
            for clip_id in set(clip_id_set+clip_id_sets): self.VIDEO_MEM_CLIPS[clip_id].summarize()
        self.summarize()
    
    @property
    def structure(self):
        return f"[{len(self)}({self.len_atoms}) : " + " ".join([clip.structure for clip in self.VIDEO_MEM_CLIPS])+ "]"

    def __getitem__(self, index):
        return self.VIDEO_MEM_CLIPS[index] if isinstance(index, int) else self.VIDEO_MEM_CLIPS[index[0]][index[1:]]


class VideoMemory(Memory):
    def __init__(self, MEMORIZER, **kwargs):
        super().__init__()
        self.name = "DumpMemory"
        self.MEMORIZER = MEMORIZER

        self.TIME = TimeStamp()
        self.TIME.EXPERIENCE = self.EXPERIENCE
        self.TIME.seconds_experience = 0
        self.MemorizeTime = 0
        self.meta = {}
        self.VIDEO_MEM_SEGMENTS = []

        self.atom_s = kwargs.get("atom_s", 844)  ##length in seconds for atom video understanding
        self.num_segments = kwargs.get("num_segments", 30)  #number of frames for atom video understanding

        self.encode_time = 0.0
        from .VideoEncode import StringEncodings
        self.ENCODINGS = StringEncodings(self, **kwargs)

    @property
    def encodes_config(self):
        return self.ENCODINGS.encodes_config

    def __len__(self):
        return len(self.VIDEO_MEM_SEGMENTS)
    
    def __repr__(self):
        return f"<VideoMemory: {len(self)} segments, {self.len_clips} clips, {self.len_atoms} atoms  at T{self.TIME.seconds_experience}s>\n" + "\n".join([SEG.__repr__() for SEG in self.VIDEO_MEM_SEGMENTS])

    @property
    def len_clips(self):
        return sum([len(segment) for segment in self.VIDEO_MEM_SEGMENTS])
    
    @property
    def len_atoms(self):
        return sum([segment.len_atoms for segment in self.VIDEO_MEM_SEGMENTS])

    @property
    def strategy(self):
        return self.MEMORIZER.strategy["memory"]

    @property
    def EXPERIENCE(self):
        return self.MEMORIZER.EXPERIENCE
    
    @property
    def METHOD(self):
        return self.MEMORIZER.METHOD
    
    @property
    def SCREEN_SHOT(self):
        return self.MEMORIZER.SCREEN_SHOT
    
    @property
    def EXPERIMENT(self):
        return self.MEMORIZER.EXPERIMENT
    
    @property
    def ENCODER(self):
        return self.MEMORIZER.ENCODER
    
    def encode(self, s):
        return self.MEMORIZER.encode(s)

    @property
    def MODEL(self):
        return self.MEMORIZER.MODEL
    
    def call(self, *args, **kwargs):
        return self.MEMORIZER.call(*args, **kwargs)

    def tall(self, *args, **kwargs):
        return self.MEMORIZER.tall(*args, **kwargs)
    
    @property
    def to_dict(self):
        return {
            "meta": self.meta,
            'TIME': self.TIME.to_dict,
            'MemorizeTime': self.MemorizeTime,
            'encode_time': self.encode_time,
            'VIDEO_MEM_SEGMENTS': [ segment.to_dict for segment in self.VIDEO_MEM_SEGMENTS ]
        }

    @property
    def MEMORY_CONTEXT(self):
        #FIXME: such MEMORY_CONTEXT should be more sophisticated, including summaries of video memory segments, important events, etc.
        
        #(a) the current segment data
        if len(self.VIDEO_MEM_SEGMENTS) == 0:
            return "It's the beginning of my memory.\n"
        CURRENT_SEGMENT = "Currently, " + self.VIDEO_MEM_SEGMENTS[-1].data + "\n"
        #(b) the second last clip data
        LAST_SECOND_CLIP = ""
        if len(self.VIDEO_MEM_SEGMENTS) > 0 and len(self.VIDEO_MEM_SEGMENTS[-1].VIDEO_MEM_CLIPS) >= 2:
            LAST_SECOND_CLIP = self.VIDEO_MEM_SEGMENTS[-1].VIDEO_MEM_CLIPS[-2].TIMESPAN.related_to(self.TIME) + ": " + self.VIDEO_MEM_SEGMENTS[-1].VIDEO_MEM_CLIPS[-2].data + "\n"
        #(c) the last clip data
        LAST_ONE_CLIP = ""
        if len(self.VIDEO_MEM_SEGMENTS) > 0 and len(self.VIDEO_MEM_SEGMENTS[-1].VIDEO_MEM_CLIPS) >= 1:
            LAST_ONE_CLIP = self.VIDEO_MEM_SEGMENTS[-1].VIDEO_MEM_CLIPS[-1].TIMESPAN.related_to(self.TIME) + ": " + self.VIDEO_MEM_SEGMENTS[-1].VIDEO_MEM_CLIPS[-1].data + "\n"
        return CURRENT_SEGMENT + LAST_ONE_CLIP + LAST_SECOND_CLIP
        
    @property
    def file_name(self):
        from EgoCL.paths import MEMORY_FILE
        return MEMORY_FILE(self)

    def save(self):
        # from .... import MEMORY_ROOT
        # import os
        # from os.path import join as opj
        # path = opj(MEMORY_ROOT, self.EXPERIENCE.name, self.METHOD.name, f"{int(self.TIME.seconds_experience):06d}", f"{self.EXPERIMENT.name}_memory.json")
        # os.makedirs(os.path.dirname(path), exist_ok=True)
        import json, os
        os.makedirs(os.path.dirname(self.file_name), exist_ok=True)
        with open(self.file_name, 'w') as f:
            json.dump(self.to_dict, f, ensure_ascii=False, indent=4)
        
        if self.encodes_config['pre']: self.ENCODINGS.save()

    def from_dict(self, dict_data):
        self.TIME.from_dict(dict_data['TIME'], None, None)
        self.meta = dict_data['meta']
        self.MemorizeTime = dict_data.get('MemorizeTime', 0)
        self.encode_time = dict_data.get('encode_time', 0.0)
        self.VIDEO_MEM_SEGMENTS = [VideoMemSegment(self).from_dict(segment_dict) for segment_dict in dict_data['VIDEO_MEM_SEGMENTS']]
        return self

    @property
    def fsize_bytes(self):
        import os
        fsize = os.path.getsize(self.file_name) if os.path.exists(self.file_name) else 0
        if self.encodes_config['pre']:
            fsize += self.ENCODINGS.fsize_bytes
        if self.SCREEN_SHOT:
            from EgoCL.paths import SCREENSHOT_DIR
            screenshot_dir = SCREENSHOT_DIR(self)
            if os.path.exists(screenshot_dir):
                for dirpath, dirnames, filenames in os.walk(screenshot_dir):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        fsize += os.path.getsize(fp)
        return fsize

    @property
    def fsize_kB(self):
        return round(self.fsize_bytes / 1024, 2) #FIXME: 未来要引入截屏、预保存的编码的尺寸统计

    def load(self, seconds_experience, experiment_name=None):
        from .... import MEMORY_ROOT
        from os.path import join as opj
        if isinstance(seconds_experience, str) and seconds_experience == "latest":
            import os
            exp_mem_path = opj(MEMORY_ROOT, self.EXPERIENCE.name, self.METHOD.name)
            os.makedirs(exp_mem_path, exist_ok=True)
            available_times = [int(name) for name in os.listdir(exp_mem_path) if name.isdigit() and os.path.exists(opj(exp_mem_path, name, f"{experiment_name if experiment_name is not None else self.EXPERIMENT.name}_memory.json"))]
            if len(available_times) == 0:
                return None
            seconds_experience = max(available_times)
        
        self.TIME.seconds_experience = seconds_experience
        
        # path = opj(MEMORY_ROOT, self.EXPERIENCE.name, self.METHOD.name, f"{int(seconds_experience):06d}", f"{experiment_name if experiment_name is not None else self.EXPERIMENT.name}_memory.json")
        import json, os
        with open(self.file_name, 'r') as f:
            data = json.load(f)


        self.from_dict(data)

        self.ENCODINGS.build()
        self.ENCODINGS.load("%06d" % int(self.TIME.seconds_experience))

        return "%06d" % int(self.TIME.seconds_experience)

    @property
    def screenshot_dir(self):
        from EgoCL.paths import SCREENSHOT_DIR
        return SCREENSHOT_DIR(self)

    def __call__(self, clip, TIMESPAN, summary, meta=None, START_NATURAL=None):
        atom = VideoMemAtom(data=summary, meta=meta if meta is not None else {}, CLIP=None)
        atom.TIMESPAN = TIMESPAN.copy()
        self.TIME.seconds_experience = max(self.TIME.seconds_experience, TIMESPAN.ENDSTAMP.seconds_experience)
        
        atom.meta = meta if meta is not None else {}
        if not self.SCREEN_SHOT:
            atom.data = summary
        else:    
            from ... import SCREEN_SHOOTING
            # from .....paths import MEMORY_ROOT
            from os.path import join as opj
            import os
            from PIL import Image
            images, descriptions, times, summary = SCREEN_SHOOTING(clip, summary, TIMESPAN, START_NATURAL)
            atom.data = summary
            os.makedirs(self.screenshot_dir, exist_ok=True)
            atom.meta['screenshots'] = []
            for i, (img, desc, t) in enumerate(zip(images, descriptions, times)):
                img_path = opj(self.screenshot_dir, f"{t}.png")
                #img is numpy.ndarray
                Image.fromarray(img).save(img_path)
                atom.meta['screenshots'].append({'path': img_path, 'description': desc, 'time': t})
        

        #self.MEMORY.append(clip)
        if len(self.VIDEO_MEM_SEGMENTS) == 0: self.VIDEO_MEM_SEGMENTS.append(VideoMemSegment(self))
        self.VIDEO_MEM_SEGMENTS[-1].append_atom(atom)
        if self.encodes_config['pre']:
            import time
            start_time = time.time()
            self.ENCODINGS.append_atom(atom, len(self.VIDEO_MEM_SEGMENTS[-1].VIDEO_MEM_CLIPS)-1, force_encoding=False)
            self.encode_time += time.time() - start_time
        self.organize()



    def iterate_atoms(self):
        for segment in self.VIDEO_MEM_SEGMENTS:
            for clip in segment.VIDEO_MEM_CLIPS:
                for atom in clip.VIDEO_MEM_ATOMS:
                    yield atom

    def iterate_everything(self):
        for segment in self.VIDEO_MEM_SEGMENTS:
            yield segment
            for clip in segment.VIDEO_MEM_CLIPS:
                yield clip
                for atom in clip.VIDEO_MEM_ATOMS:
                    yield atom

    def adjust(self):
        if len(self.VIDEO_MEM_SEGMENTS) == 1: return []
        #(2.1) 需要考虑这个segment中的clip配置是否合理，就是首先是否需要和上一个segment调整clip的切割位置（memory.adjust）
        from ... import MEMORY_ADJUST_SEGMENT_PROMPT
        SYSTEM_PROMPT, USER_PROMPT = MEMORY_ADJUST_SEGMENT_PROMPT(self.VIDEO_MEM_SEGMENTS[-2], self.VIDEO_MEM_SEGMENTS[-1])
        advice = self.tall({"content": [{"system":SYSTEM_PROMPT},{"user":USER_PROMPT}]})
        import re
        adjustment_match = re.search(r"<adjust>(-?\d+)</adjust>", advice)
        if adjustment_match:
            adjustment = int(adjustment_match.group(1))
        else:
            adjustment = 0
        if adjustment == 0:
            # print("No adjustment needed")
            return []
        elif adjustment > 0:
            if adjustment > len(self.VIDEO_MEM_SEGMENTS[-1].VIDEO_MEM_CLIPS):
                # print("Invalid adjustment value, larger than len(self.VIDEO_MEM_SEGMENTS[-1].VIDEO_MEM_CLIPS)")
                return []
            # print("Adjusting segments by", adjustment)
            #move some clips from latter segment to former segment
            for _ in range(adjustment):
                clip = self.VIDEO_MEM_SEGMENTS[-1].pop_front_clip()
                self.VIDEO_MEM_SEGMENTS[-2].push_back_clip(clip)
            return [len(self.VIDEO_MEM_SEGMENTS)-2, len(self.VIDEO_MEM_SEGMENTS)-1]
        else:
            if -adjustment > len(self.VIDEO_MEM_SEGMENTS[-2].VIDEO_MEM_CLIPS):
                # print("Invalid adjustment value, larger than len(self.VIDEO_MEM_SEGMENTS[-2].VIDEO_MEM_CLIPS)")
                return []
            # print("Adjusting segments by", adjustment)
            #move some clips from former segment to latter segment
            for _ in range(-adjustment):
                clip = self.VIDEO_MEM_SEGMENTS[-2].pop_back_clip()
                self.VIDEO_MEM_SEGMENTS[-1].push_front_clip(clip)
            return [len(self.VIDEO_MEM_SEGMENTS)-2, len(self.VIDEO_MEM_SEGMENTS)-1]
        

    def separate(self):
        #(2.2) 其次是当前这个segment中的clip们是否需要切成两份，后面一份形成新的segment（memory.separate）
        from ... import MEMORY_SEPARATE_SEGMENT_PROMPT
        SEGMENT = self.VIDEO_MEM_SEGMENTS[-1]
        SYSTEM_PROMPT, USER_PROMPT = MEMORY_SEPARATE_SEGMENT_PROMPT(SEGMENT)
        advice = self.tall({"content": [{"system":SYSTEM_PROMPT},{"user":USER_PROMPT}]})
        import re
        separation_match = re.search(r"<separate>(\d+)</separate>", advice)
        if separation_match:
            separation = int(separation_match.group(1))
        else:
            separation = 0
        if separation == 0:
            # print("No separation needed")
            return []
        if separation < 0 or separation >= len(SEGMENT.VIDEO_MEM_CLIPS):
            # print("Invalid separation index")
            return []
        # print("Separating segment, ", separation, "clips will be moved to new segment, remaining ", len(SEGMENT.VIDEO_MEM_CLIPS)-separation, "clips in current segment.")
        new_segment = VideoMemSegment(self)
        for _ in range(separation):
            clip = SEGMENT.pop_back_clip()
            new_segment.push_front_clip(clip)
        self.VIDEO_MEM_SEGMENTS.append(new_segment)
        return [len(self.VIDEO_MEM_SEGMENTS)-2, len(self.VIDEO_MEM_SEGMENTS)-1]

    def separate_force(self):
        SEGMENT = self.VIDEO_MEM_SEGMENTS[-1]
        # print("Separating segment, ", separation, "clips will be moved to new segment, remaining ", len(SEGMENT.VIDEO_MEM_CLIPS)-separation, "clips in current segment.")
        new_segment = VideoMemSegment(self)
        clip = SEGMENT.pop_back_clip()
        new_segment.push_front_clip(clip)
        self.VIDEO_MEM_SEGMENTS.append(new_segment)
        return [len(self.VIDEO_MEM_SEGMENTS)-2, len(self.VIDEO_MEM_SEGMENTS)-1]
    
    def organize(self):
        self.VIDEO_MEM_SEGMENTS[-1].organize()
        seg_id_set, seg_id_sets = [], []
        if self.strategy["adjust"] == "Try":
            seg_id_set = self.adjust()
        if self.strategy["split"] == "Try":
            seg_id_sets = self.separate()
        elif self.strategy["split"] == "Force":
            seg_id_sets = self.separate_force()

        for seg_id in set(seg_id_set+seg_id_sets): self.VIDEO_MEM_SEGMENTS[seg_id].summarize()
    
    @property
    def structure(self):
        return f"{len(self)}[{self.len_clips}({self.len_atoms})] : " + " ".join([seg.structure for seg in self.VIDEO_MEM_SEGMENTS])
    
    def __getitem__(self, index):
        return self.VIDEO_MEM_SEGMENTS[index] if isinstance(index, int) else self.VIDEO_MEM_SEGMENTS[index[0]][index[1:]]

    def get(self,i): #for a dump solution, who only contains one segment of all, and one atom in each clip (such solution actually eliminates the need for segment and clip levels, but keeps them for structure consistency)
        return self.VIDEO_MEM_SEGMENTS[0][i][0]