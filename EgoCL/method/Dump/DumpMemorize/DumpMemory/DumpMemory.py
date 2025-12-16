from ....Base import Memory

class DumpMemory(Memory):
    def __init__(self, MEMORIZER):
        super().__init__()
        self.name = "DumpMemory"
        self.MEMORIZER = MEMORIZER

        from .....data.elements import TimeStamp
        self.TIME = TimeStamp()
        self.TIME.EXPERIENCE = self.EXPERIENCE
        self.TIME.seconds_experience = 0
        self.MEMORY = []

    @property
    def EXPERIENCE(self):
        return self.MEMORIZER.EXPERIENCE
    
    @property
    def METHOD(self):
        return self.MEMORIZER.METHOD
    
    @property
    def to_dict(self):
        return {
            "name": self.name,
            "TIME": self.TIME.to_dict,
            "memory": [anno.to_dict for anno in self.MEMORY]
        }

    #/mnt/data/yl/W/EgoCL/Memory/bin_1/CheatMemorize/001681/memory.json

    def save(self):
        from .... import MEMORY_ROOT
        import os
        from os.path import join as opj
        path = opj(MEMORY_ROOT, self.EXPERIENCE.name, self.METHOD.name, f"{int(self.TIME.seconds_experience):06d}", "memory.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        import json
        with open(path, 'w') as f:
            json.dump(self.to_dict, f)
    
    def from_dict(self, data):
        from .....data.elements import TimeStamp, Anno
        self.TIME = TimeStamp()
        self.TIME.from_dict(data_dict=data["TIME"], Video=None, Activity=None)
        for anno_dict in data["memory"]:
            ANNO = Anno({})
            ANNO.from_dict(anno_dict)
            self.MEMORY.append(ANNO)
        self.name = data["name"]

    def load(self, seconds_experience):
        from .... import MEMORY_ROOT
        from os.path import join as opj
        path = opj(MEMORY_ROOT, self.EXPERIENCE.name, self.METHOD.name, f"{int(seconds_experience):06d}", "memory.json")
        import json
        with open(path, 'r') as f:
            data = json.load(f)
        self.from_dict(data)

    def __call__(self, anno):
        self.MEMORY.append(anno)
        self.TIME.seconds_experience = max(self.TIME.seconds_experience, anno.TIMESPAN.ENDSTAMP.seconds_experience)