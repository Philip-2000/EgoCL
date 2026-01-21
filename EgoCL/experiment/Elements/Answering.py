class Answering:
    def __init__(self, name, EXPERIENCE, q_list="all", load_style="FORCE_LOAD", load_style_questions="FORCE_LOAD", load_style_respond="FORCE_CREATE", **kwargs): #Under some circumstances, load_style_respond might be FORCE_LOAD, but that means that the experiment is done. In such case, we no longer need to instantiate Execution class. So generally speaking, load_style_respond is FORCE_CREATE
        self.EXPERIENCE = EXPERIENCE
        from .Question import Questions
        self.QUESTIONS = Questions(load_style_question=load_style_questions, load_style_respond=load_style_respond)
        self.name = name
        self.load_style = load_style
        self.load_style_questions = load_style_questions
        self.load_style_respond = load_style_respond
        self.ckpt = kwargs.get("ckpt", "latest") #("new", "%06d", "latest")
        self.mode = kwargs.get("mode", "normal") #"normal", "strong"
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
        load_style = self.load_style
        assert load_style == "FORCE_LOAD"
        if os.path.exists(self.file_name): self.from_dict(json.load( open(self.file_name, 'r') ), load_style_questions=self.load_style_questions)
        else: raise FileNotFoundError(f"Execution file not found: {self.file_name}")
        from ...paths import MEMORY_DIR
        # self.QUESTIONS.load_res(os.path.join(MEMORY_DIR(self.EXPERIENCE.name, self.METHOD), ts6d))
        self.QUESTIONS.sort_by_time()
        
    def from_dict(self, data: dict, load_style_questions="FORCE_LOAD"):
        self.name = data.get('name', 'Unknown Execution')
        assert self.EXPERIENCE.name == data.get('experience', self.EXPERIENCE.name), "Experience name mismatch in Execution loading."
        # Load QUESTIONS
        from .Question import Questions, Question
        self.QUESTIONS = Questions(load_style_question=load_style_questions, load_style_respond=self.load_style_respond)
        self.QUESTIONS.EXECUTION = self
        assert self.load_style_questions == "FORCE_LOAD"
        self.QUESTIONS.from_dict(data['questions'], self.load_style_respond)
                
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
