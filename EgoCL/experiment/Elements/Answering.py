class Answering:
    def __init__(self, name, EXPERIENCE, q_list="all", **kwargs):
        self.EXPERIENCE = EXPERIENCE
        from .Question import Questions
        self.QUESTIONS = Questions(load_style_question="FORCE_LOAD", load_style_respond="FORCE_CREATE")
        self.name = name
        
        self.ckpt = kwargs.get("ckpt", "latest") #("new", "%06d", "latest")
        self.mode = kwargs.get("mode", "normal") #"normal", "strong"
        self.OPTIONAL = kwargs.get("OPTIONAL", False)
        self.EXPERIMENT = kwargs.get("EXPERIMENT", None)
        self.q_list = q_list
        self.METHOD = None
        self.load()

    @property
    def file_name(self):
        from .. import EXPERIMENT_ROOT
        import os
        return os.path.join(EXPERIMENT_ROOT, self.name, self.EXPERIENCE.name, "execution.json")
        
    def load(self, ckpt=""):
        ckpt = ckpt if ckpt != "" else self.ckpt
        import json, os
        if os.path.exists(self.file_name): self.from_dict(json.load( open(self.file_name, 'r') ), load_style_questions="FORCE_LOAD")
        else: raise FileNotFoundError(f"Execution file not found: {self.file_name}")
        from ...paths import MEMORY_DIR
        # self.QUESTIONS.load_res(os.path.join(MEMORY_DIR(self.EXPERIENCE.name, self.METHOD), ts6d))
        self.QUESTIONS.sort_by_time()
        
    def from_dict(self, data: dict, load_style_questions="FORCE_LOAD"):
        self.name = data.get('name', 'Unknown Answering')
        assert self.EXPERIENCE.name == data.get('experience', self.EXPERIENCE.name), "Experience name mismatch in Execution loading."
        # Load QUESTIONS
        from .Question import Questions, Question
        self.QUESTIONS = Questions(load_style_question=load_style_questions, load_style_respond="FORCE_CREATE")
        self.QUESTIONS.EXECUTION = self
        self.QUESTIONS.from_dict(data['questions'], "FORCE_CREATE")
                
    @property
    def to_dict(self):
        return {
            'name': self.name,
            'experience': self.EXPERIENCE.name,
            'questions': self.QUESTIONS.to_dict if self.QUESTIONS is not None else []
        }

    def __call__(self):
        from ...data.elements import TimeStamp
        from ...method import MEMORY_ROOT#, DumpRespond
        from ...paths import MEMORY_DIR
        from . import YOG
        
        import os
        
        for q in [q for q in self.QUESTIONS if (self.q_list == "all") or (q.QID in self.q_list)]:
            ts6d = "%06d" % (min([int(ts) for ts in os.listdir(MEMORY_DIR(self.EXPERIENCE.name, self.METHOD)) if str(ts).isdigit() and int(ts) >= q.TIME.seconds_experience-1.0 ]) )
            self.METHOD.load(ts6d)
            q.respond(self.METHOD.query(q.query if self.mode == "normal" else q.question))
            q.save_res(os.path.join(MEMORY_DIR(self.EXPERIENCE.name, self.METHOD), ts6d), caching_video=True)
            YOG.info(f"Processed Question ID: {q.QID} at TIME: {q.TIME.seconds_experience}s, saved at {os.path.join(MEMORY_DIR(self.EXPERIENCE.name, self.METHOD), ts6d)}")
