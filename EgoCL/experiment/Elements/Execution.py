
import os
from . import YOG

class QuestionGenerator:
    def __init__(self, **kwargs):
        self.Retriever = None
        from ...method.VlmBase import QwenVLM, DeepSeekLLM, QwenLLM, MyLLM
        self.VlmBase = MyLLM(kwargs.get("MODEL", "Qwen3-VL-8B-Instruct")) #QwenLLM() # DeepSeekLLM() #QwenVLM() #
        from .. import QUESTION_GENERATOR_PROMPT
        self.SYSTEM_PROMPT= QUESTION_GENERATOR_PROMPT
        self.replace = kwargs.get("replace", True) #For Ego4D annotations, we need to replace "C" with "I", and "X" with "a person"

    def __call__(self, query):
        query = self.VlmBase.text(query)
        import re
        s = self.VlmBase({"content":[{"text":self.SYSTEM_PROMPT + "\n" + query}]})
        #s = self.VlmBase(query, self.SYSTEM_PROMPT)
        q_a = re.split(r"<\|.*?\|>", s, maxsplit=1, flags=re.S)
        try:
            if len(q_a) != 2:
                raise ValueError(f"Generated question and answer format is incorrect. Expected a single <|...|> separator but got: {repr(s)}")
            q_a = [part.strip() for part in q_a]
            if len(q_a) != 2:
                raise ValueError("Generated question and answer format is incorrect.")
            if self.replace:
                #change the "C" to "I", and "X" to a "a person"
                q_a[0] = q_a[0].replace("#C ", "I ").replace("C ", "I ").replace("#X ", "a person").replace("X ", "a person")
                q_a[1] = q_a[1].replace("#C ", "I ").replace("C ", "I ").replace("#X ", "a person").replace("X ", "a person")
            return q_a[0], q_a[1]
        except Exception as e:
            return query, query

class Execution:
    def __init__(self, name, load_style, load_style_questions, load_style_respond="FORCE_CREATE", N=5, SAMPLES=5, **kwargs): #Under some circumstances, load_style_respond might be FORCE_LOAD, but that means that the experiment is done. In such case, we no longer need to instantiate Execution class. So generally speaking, load_style_respond is FORCE_CREATE
        self.EXPERIENCE = None
        from .Question import Questions
        self.QUESTIONS = Questions(load_style_question=load_style_questions, load_style_respond=load_style_respond)
        self.name = name
        self.QUESTION_GENERATOR = QuestionGenerator(**kwargs)
        self.load_style = load_style
        self.load_style_questions = load_style_questions
        self.load_style_respond = load_style_respond
        self.ckpt = kwargs.get("ckpt", "latest") #("new", "%06d", "latest")
        # self.mode = kwargs.get("mode", "normal") #"normal", "strong"
        self.option = kwargs.get("option", True)
        self.strong = kwargs.get("strong", False)
        
        self.EXPERIMENT = kwargs.get("EXPERIMENT", None)
        # self.OPTIONAL = kwargs.get("OPTIONAL", False)
        self.N = N
        self.SAMPLES = SAMPLES
        self.METHOD = None

        self._ENCODER = None
        self.ENCODER_PATH = kwargs.get("ENCODER_PATH", None)
        self.MODEL = kwargs.get("MODEL", "Qwen3-VL-8B-Instruct") 
        self.TEXT = kwargs.get("TEXT", "Qwen3-Ours")
    
    @property
    def I_Dont_Know(self):
        return self.METHOD.I_Dont_Know if hasattr(self.METHOD, "I_Dont_Know") else False

    def call(self, *args, **kwargs):
        from MyLm import call
        return call(self.MODEL, *args, **kwargs)

    def tall(self, *args, **kwargs): #text call, when you sure that this calling contains no video or image input, so that we can use a pure text model ( which is larger and faster ) to process it
        from MyLm import call
        return call(self.TEXT, *args, **kwargs)

    @property
    def ENCODER(self):
        if hasattr(self.METHOD, "ENCODER") and self.METHOD.ENCODER is not None and self.METHOD.ENCODER_PATH is not None and self.ENCODER_PATH == self.METHOD.ENCODER_PATH: #prefer to use the method's encoder
            self._ENCODER = self.METHOD.ENCODER
        elif self._ENCODER is not None:
            return self._ENCODER
        elif self._ENCODER is None and self.ENCODER_PATH is not None:
            from ... import VideoEncoderFactory
            self._ENCODER = VideoEncoderFactory(self.ENCODER_PATH)
        else:
            raise ValueError("No ENCODER is set in Execution.")
        return self._ENCODER

    def encode(self, s):
        return self.ENCODER(s)
        # if hasattr(self.METHOD, "ENCODER") and self.METHOD.ENCODER is not None and self.METHOD.ENCODER_PATH is not None and self.ENCODER_PATH == self.METHOD.ENCODER_PATH: #prefer to use the method's encoder
        #     self.ENCODER = self.METHOD.ENCODER
        #     return self.METHOD.ENCODER(s)
        # elif self.ENCODER is not None:
        #     return self.ENCODER(s)
        # elif self.ENCODER_PATH is not None:
        #     from sentence_transformers import SentenceTransformer
        #     self.ENCODER = SentenceTransformer(self.ENCODER_PATH)
        #     return self.ENCODER(s)
        # else:
        #     raise ValueError("No ENCODER is set in Execution.")

    @property
    def file_name(self):
        # from .. import EXPERIMENT_ROOT
        # return os.path.join(EXPERIMENT_ROOT, self.name, self.EXPERIENCE.name, "execution.json")
        from EgoCL.paths import EXECUTION_FILE
        return EXECUTION_FILE(self)

    def random_execution(self):
        import random
        from ...data.elements import TimeStamp
        from .Question import Question
        E_start_s = self.EXPERIENCE.start_s
        E_end_s = self.EXPERIENCE.start_s + self.EXPERIENCE.duration_s
        N,SAMPLES = self.N, self.SAMPLES
        Q_time_s_es = [(Q_i+1)*(E_end_s - E_start_s)/N + E_start_s for Q_i in range(N)]
        QID=0
        #print all the things above out
        print(f"E_start_s: {E_start_s}, E_end_s: {E_end_s}, N: {N}, SAMPLES: {SAMPLES}")
        print(f"Q_time_s_es: {Q_time_s_es}")
        for Q_i, Q_time_s in enumerate(Q_time_s_es):
            T = TimeStamp()
            T.EXPERIENCE = self.EXPERIENCE
            T.seconds_experience = Q_time_s
            annos = []
            for _anno in [A.ANNOS for A in self.EXPERIENCE.ACTIVITIES]:
                for category, anno_list in _anno.ANNOS.items():
                    annos.extend([anno for anno in anno_list if anno.TIMESPAN.STARTSTAMP.seconds_experience <= Q_time_s])
            mm = random.sample(annos, min(len(annos), (Q_i+1)*SAMPLES))
            for ann in mm:
                q, a = self.QUESTION_GENERATOR(ann.info)
                print("Generated Question:", q, "Answer:", a)
                self.QUESTIONS += Question(TIME=T.copy(), question=q, ref_time=ann.TIMESPAN.copy(), answer=a, QID = f"Q{QID:03d}")
                print("Generated Question:", self.QUESTIONS.QUESTIONS[-1].question, "Answer:", self.QUESTIONS.QUESTIONS[-1].answer, "QID:", self.QUESTIONS.QUESTIONS[-1].QID)
                QID+=1
        
    def load(self, ckpt=""):
        ckpt = ckpt if ckpt != "" else self.ckpt
        import json, os
        load_style = self.load_style
        if load_style == "FORCE_CREATE":
            self.random_execution()
        elif load_style == "FORCE_LOAD":
            if os.path.exists(self.file_name): self.from_dict(json.load(open(self.file_name, 'r')), EXPERIENCE=self.EXPERIENCE, load_style_questions=self.load_style_questions)
            else: raise FileNotFoundError(f"Execution file not found: {self.file_name}")
            if ckpt == "new": return
            ts6d = self.METHOD.load(ckpt)
            if ts6d is None: return #no memory found, handle it as "new"
            from ...paths import MEMORY_DIR
            # self.QUESTIONS.load_res(os.path.join(MEMORY_DIR(self.EXPERIENCE, self.METHOD), ts6d))
            self.QUESTIONS.sort_by_time()
        else:
            raise ValueError(f"Unknown load_style: {load_style}")

    def from_dict(self, data: dict, EXPERIENCE = None, load_style_questions="FORCE_LOAD"):
        self.name = data.get('name', 'Unknown Execution')
        self.EXPERIENCE = EXPERIENCE
        assert self.EXPERIENCE.name == data.get('experience', self.EXPERIENCE.name), "Experience name mismatch in Execution loading."
        # Load QUESTIONS
        from .Question import Questions, Question
        self.QUESTIONS = Questions(load_style_question=load_style_questions, load_style_respond=self.load_style_respond)
        self.QUESTIONS.EXECUTION = self
        if self.load_style_questions == "FORCE_LOAD":
            if 'questions' not in data or len(data['questions']) == 0:
                raise ValueError("No questions found in execution data.")
            self.QUESTIONS.from_dict(data['questions'], self.load_style_respond)
        elif self.load_style_questions == "FORCE_CREATE":
            #collect the time of the questions from data as Q_time_s_es
            QUESTIONS = data.get('questions', [])
            Q_time_s_es = set([q['TIME']['seconds_experience'] for q in QUESTIONS])
            Q_time_s_es = sorted(list(Q_time_s_es))
            SAMPLES = self.SAMPLES
            
            QID=0
            for Q_i, Q_time_s in enumerate(Q_time_s_es):
                T = TimeStamp()
                T.EXPERIENCE = self.EXPERIENCE
                T.seconds_experience = Q_time_s
                annos = []
                for _anno in [A.ANNOS for A in self.EXPERIENCE.ACTIVITIES]:
                    for category, anno_list in _anno.ANNOS.items():
                        annos.extend([anno for anno in anno_list if anno.TIMESPAN.STARTSTAMP.seconds_experience <= Q_time_s])
                mm = random.sample(annos, min(len(annos), (Q_i+1)*SAMPLES))
                for ann in mm:
                    q, a = self.QUESTION_GENERATOR(ann.info)
                    print("Generated Question:", q, "Answer:", a)
                    self.QUESTIONS += Question(TIME=T.copy(), question=q, ref_time=ann.TIMESPAN.copy(), answer=a, QID = f"Q{QID:03d}")
                    print("Generated Question:", self.QUESTIONS.QUESTIONS[-1].question, "Answer:", self.QUESTIONS.QUESTIONS[-1].answer, "QID:", self.QUESTIONS.QUESTIONS[-1].QID)
                    QID+=1
        
    @property
    def to_dict(self):
        return {
            'name': self.name,
            'experience': self.EXPERIENCE.name,
            'questions': self.QUESTIONS.to_dict if self.QUESTIONS is not None else []
        }

    def save(self):
        import json, os
        os.makedirs(os.path.dirname(self.file_name), exist_ok=True)
        with open(self.file_name, 'w') as f:
            json.dump(self.to_dict, f, indent=4)

    def __call__(self, caching_video=True):
        from ...data.elements import TimeStamp
        from ...method import MEMORY_ROOT#, DumpRespond
        from ...paths import MEMORY_DIR
        
        METHOD = self.METHOD
        
        for q in self.QUESTIONS:
            if q.TIME.seconds_experience < METHOD.TIME.seconds_experience - 1e-1: continue

            if METHOD.TIME.seconds_experience < q.TIME.seconds_experience - 1e-1:
                YOG.info(self.QUESTIONS.short_report(METHOD.TIME))
                YOG.debug("Progressing METHOD TIME from %.2f to %.2f" % (METHOD.TIME.seconds_experience, q.TIME.seconds_experience))
                METHOD.progress(start_s=METHOD.TIME.seconds_experience, end_s=q.TIME.seconds_experience)

            YOG.debug(f"Processing Question ID: {q.QID} at TIME: {q.TIME.seconds_experience}s")
            
            q.respond(METHOD.query(q.query,image=q.Image,opt=True) if self.option else None, METHOD.query(q.question,image=q.Image,opt=False) if self.strong else None)
            
            q.save_res(caching_video=caching_video)
        
        YOG.info(self.QUESTIONS.short_report(METHOD.TIME))