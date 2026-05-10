from ...Base import Respond
from . import YOG

class Response():
    def __init__(self, result="", hits="", query="", delay_s=None, delay_rate=None, memorize_rate=None, fsize_kB=None, fsize_rate=None):
        self.result = result
        self.query = query
        self.hits = hits
        self.delay_s = delay_s
        self.delay_rate = delay_rate
        self.memorize_rate = memorize_rate
        self.fsize_kB = fsize_kB
        self.fsize_rate = fsize_rate
    
    def __str__(self):
        return self.result
    
    def __repr__(self):
        return f"Response(result={self.result}, hits={self.hits}, query={self.query})"
    
    @property
    def res_dict(self):
        import json
        # hits = self.hits
        # try:
        #     parsed_hits = json.loads(hits)
        #     hits = json.dumps(parsed_hits, ensure_ascii=False, indent=4)
        # except (TypeError, json.JSONDecodeError):
        #     hits = self.hits
        return {
            'result': self.result,
            'hits': [json.loads(h) for h in self.hits], #transform to a list of dicts
            'query': self.query,
            'delay_s': self.delay_s,
            'delay_rate': self.delay_rate,
            'memorize_rate': self.memorize_rate,
            'fsize_kB': self.fsize_kB,
            'fsize_rate': self.fsize_rate
        }

class VideoRespond(Respond):
    def __init__(self, METHOD, **kwargs):
        super().__init__()
        from . import VideoRetrieve
        self.name = "VideoRespond"
        self.METHOD = METHOD
        self.RESPOND_PROMPT = None 
        YOG.info(("option ", self.option, "strong", self.strong, " EGO ", self.EXPERIENCE.EGO, " VLM Model ", kwargs.get("MODEL", "Qwen3-VL-8B-Instruct")))
        
        # from .. import RAG_PROMPT
        self.RETRIEVE = VideoRetrieve(self, **kwargs)
        self.MODEL = kwargs.get("MODEL", "Qwen3-VL-8B-Instruct")
        self.TEXT = kwargs.get("TEXT", "Qwen3-Ours")
        # self.RESPOND_PROMPT = RESPOND_PROMPT
        self.I_Dont_Know = kwargs.get("I_Dont_Know", True) # False)#
        self.Respond_Cant_See = kwargs.get("Respond_Cant_See", True) #False)#

    @property
    def EXECUTION(self):
        return self.METHOD.EXECUTION

    @property
    def option(self):
        return self.EXECUTION.option

    @property
    def strong(self):
        return self.EXECUTION.strong

    def call(self, *args, **kwargs):
        from MyLm import call
        return call(self.MODEL, *args, **kwargs)

    def tall(self, *args, **kwargs):
        from MyLm import call
        return call(self.TEXT, *args, **kwargs)

    @property
    def fsize_kB(self):
        return self.RETRIEVE.fsize_kB

    @property
    def TIME(self):
        return self.RETRIEVE.TIME

    @property
    def EXPERIENCE(self):
        return self.METHOD.EXPERIENCE
    
    @property
    def EXPERIMENT(self):
        return self.METHOD.EXPERIMENT
    
    @property
    def ENCODER(self):
        return self.METHOD.ENCODER
    
    def encode(self, s):
        return self.METHOD.encode(s)

    @property
    def MEMORY(self):
        return self.METHOD.MEMORY
    
    def load(self, seconds_experience):
        self.RETRIEVE.load(seconds_experience)
    
    def __call__(self, query, image=None, opt=True):
        import time
        start_time = time.time()
        if self.I_Dont_Know:
            result = "The responding process is disabled because I_Dont_Know is set to True. This is for saving space (of ENCODER) for LLMs. If you want to enable responding, please set I_Dont_Know to False."
            hits = []
        else:
            from functools import partial
            from .. import RESPOND_PROMPT
            # hits = self.RETRIEVE(query) #hits is a list of strings
            if self.Respond_Cant_See:
                hits = self.RETRIEVE(query, image=None) #HITS is a list of stringsr
            else:
                hits = self.RETRIEVE(query, image=image) #HITS is a list of stringsr
            # print("hits", hits)
            YOG.debug(("VideoRespond Optional Hits: ", hits), tag="VideoRespond")
            
            self.RESPOND_PROMPT = partial(RESPOND_PROMPT, EGO=self.EXPERIENCE.EGO, OPTIONAL=opt)
        
            SYSTEM_PROMPT, USER_PROMPT = self.RESPOND_PROMPT(hits, query)
            result = self.tall({"content":[{"system": SYSTEM_PROMPT}, {"user": USER_PROMPT}]})
        delay_s = time.time() - start_time
        # print("delay_s", delay_s)
        delay_rate = delay_s / max(1.0, self.TIME.seconds_experience)
        memorize_rate = self.MEMORY.MemorizeTime / max(1.0, self.TIME.seconds_experience)

        return Response(result=result, hits=hits, query=query, delay_s=delay_s, delay_rate=delay_rate, memorize_rate=memorize_rate, fsize_kB=self.fsize_kB, fsize_rate=(self.fsize_kB / max(1.0, self.TIME.seconds_experience)) if self.fsize_kB is not None else None)
        