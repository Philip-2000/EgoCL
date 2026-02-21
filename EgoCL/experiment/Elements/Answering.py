class Answering:
    def __init__(self, name, EXPERIENCE, q_list="all", encode_only=False, **kwargs):
        self.EXPERIENCE = EXPERIENCE
        from .Question import Questions
        self.QUESTIONS = Questions(load_style_question="FORCE_LOAD", load_style_respond="FORCE_CREATE")
        self.name = name

        self.ckpt = kwargs.get("ckpt", "latest") #("new", "%06d", "latest")
        # self.mode = kwargs.get("mode", "normal") #"normal", "strong"
        # self.OPTIONAL = kwargs.get("OPTIONAL", False)
        
        self.option = kwargs.get("option", True)
        self.strong = kwargs.get("strong", False)

        self.EXPERIMENT = kwargs.get("EXPERIMENT", None)
        self.q_list = q_list
        self.encode_only = encode_only
        self.METHOD = None
        
        self.load()

        self.ENCODER = None
        self.ENCODER_PATH = kwargs.get("ENCODER_PATH", None)
        self.MODEL = kwargs.get("MODEL", "Qwen3-VL-8B-Instruct") 
        self.TEXT = kwargs.get("TEXT", "Qwen3-Ours")

    def call(self, *args, **kwargs):
        from MyLm import call
        return call(self.MODEL, *args, **kwargs)

    def tall(self, *args, **kwargs): #text call, when you sure that this calling contains no video or image input, so that we can use a pure text model ( which is larger and faster ) to process it
        from MyLm import call
        return call(self.TEXT, *args, **kwargs)

    def encode(self, s):
        if hasattr(self.METHOD, "ENCODER") and self.METHOD.ENCODER is not None and self.METHOD.ENCODER_PATH is not None and self.ENCODER_PATH == self.METHOD.ENCODER_PATH: #prefer to use the method's encoder
            self.ENCODER = self.METHOD.ENCODER
            return self.METHOD.ENCODER.encode(s)
        elif self.ENCODER is not None:
            return self.ENCODER.encode(s)
        elif self.ENCODER_PATH is not None:
            from sentence_transformers import SentenceTransformer
            self.ENCODER = SentenceTransformer(self.ENCODER_PATH)
            return self.ENCODER.encode(s)
        else:
            raise ValueError("No ENCODER is set in Execution.")

    @property
    def file_name(self):
        # from .. import EXPERIMENT_ROOT
        # return os.path.join(EXPERIMENT_ROOT, self.name, self.EXPERIENCE.name, "execution.json")
        from EgoCL.paths import EXECUTION_FILE
        return EXECUTION_FILE(self)
        
    def load(self, ckpt=""):
        self.EXPERIMENT.name = self.EXPERIMENT.input_name
        
        ckpt = ckpt if ckpt != "" else self.ckpt
        import json, os
        if os.path.exists(self.file_name): self.from_dict(json.load( open(self.file_name, 'r') ), load_style_questions="FORCE_LOAD")
        else: raise FileNotFoundError(f"Execution file not found: {self.file_name}")
        from ...paths import MEMORY_DIR
        # self.QUESTIONS.load_res(os.path.join(MEMORY_DIR(self.EXPERIENCE.name, self.METHOD), ts6d))
        self.QUESTIONS.sort_by_time()

        self.EXPERIMENT.name = self.EXPERIMENT.output_name

    @property
    def encodes_config(self):
        return self.METHOD.MEMORY.encodes_config
        
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

    @property
    def RESPOND(self):
        return self.METHOD.RESPOND
    
    @property
    def MEMORY(self):
        return self.RESPOND.RETRIEVE.MEMORY

    @property
    def ENCODINGS(self):
        return self.MEMORY.ENCODINGS

    def __call__(self):
        from ...data.elements import TimeStamp
        from ...method import MEMORY_ROOT#, DumpRespond
        from ...paths import MEMORY_DIR
        from . import YOG
        
        import os
        
        for q in [q for q in self.QUESTIONS if (self.q_list == "all") or (q.QID in self.q_list)]:
            ts6d = "%06d" % (min([int(ts) for ts in os.listdir(MEMORY_DIR(self.EXPERIENCE.name, self.METHOD)) if str(ts).isdigit() and int(ts) >= q.TIME.seconds_experience-1.0 ]) )
            
            if self.encode_only: k, self.encodes_config['load_not'] = self.encodes_config['load_not'], True
            self.EXPERIMENT.name, p = self.EXPERIMENT.input_name, self.EXPERIMENT.name
            self.RESPOND.load(ts6d)
            self.METHOD.TIME.seconds_experience = int(ts6d)
            self.EXPERIMENT.name = p
            if self.encode_only: self.encodes_config['load_not'] = k
            
            if self.encode_only:
                YOG.info(f"Encoded Question ID: {q.QID} at TIME: {q.TIME.seconds_experience}s, skipped responding as encode_only is set.")
                if not os.path.exists(self.ENCODINGS.file_name):
                    self.ENCODINGS.encode_all()
                    self.ENCODINGS.save()
                continue
            q.respond(self.METHOD.query(q.query,opt=True) if self.option else None, self.METHOD.query(q.question,opt=False) if self.strong else None)
            
            q.save_res(caching_video=True)

            if self.encodes_config["save"]: self.ENCODINGS.save()
            YOG.info(f"Processed Question ID: {q.QID} at TIME: {q.TIME.seconds_experience}s, saved at {q.file_name}.")