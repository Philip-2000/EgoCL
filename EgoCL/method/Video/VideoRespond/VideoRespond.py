from ...Base import Respond
from . import YOG

class Response():
    def __init__(self, result="", hits="", query=""):
        self.result = result
        self.query = query
        self.hits = hits
    
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
            'query': self.query
        }

class VideoRespond(Respond):
    def __init__(self, METHOD, **kwargs):
        super().__init__()
        from . import VideoRetrieve
        self.name = "VideoRespond"
        self.METHOD = METHOD
        OPTIONAL = METHOD.EXECUTION.OPTIONAL if METHOD.EXECUTION is not None else False
        if OPTIONAL:
            if not self.EXPERIENCE.EGO:
                from .. import RESPOND_PROMPT_SIMPLE_OPTIONAL as RESPOND_PROMPT
            else:
                from .. import RESPOND_PROMPT_OPTIONAL as RESPOND_PROMPT
        else:
            if not self.EXPERIENCE.EGO:
                from .. import RESPOND_PROMPT_SIMPLE as RESPOND_PROMPT
            else:
                from .. import RESPOND_PROMPT as RESPOND_PROMPT
        YOG.info(("OPTIONAL ", OPTIONAL, " EGO ", self.EXPERIENCE.EGO, " VLM Model ", kwargs.get("MODEL", "Qwen3-VL-8B-Instruct")))
        
        # from .. import RAG_PROMPT
        self.RETRIEVE = VideoRetrieve(self)
        self.MODEL = kwargs.get("MODEL", "Qwen3-VL-8B-Instruct")
        self.TEXT = kwargs.get("TEXT", "Qwen3-Ours")
        self.RESPOND_PROMPT = RESPOND_PROMPT
        self.I_Dont_Know = kwargs.get("I_Dont_Know", True) # False)#

    def call(self, *args, **kwargs):
        from MyLm import call
        return call(self.MODEL, *args, **kwargs)

    def tall(self, *args, **kwargs):
        from MyLm import call
        return call(self.TEXT, *args, **kwargs)

    @property
    def TIME(self):
        return self.RETRIEVE.TIME

    @property
    def EXPERIENCE(self):
        return self.METHOD.EXPERIENCE

    @property
    def MEMORY(self):
        return self.METHOD.MEMORY
    
    def load(self, seconds_experience):
        self.RETRIEVE.load(seconds_experience)
    
    def __call__(self, query):
        if self.I_Dont_Know: return "I don't know based on the provided memories."
        # import json
        # hits = json.dumps(self.RETRIEVE(query), ensure_ascii=False)
        
        hits = self.RETRIEVE(query, top_k=3) #hits is a list of strings
        # print("hits", hits)
        YOG.debug(("VideoRespond Hits: ", hits), tag="VideoRespond")
        
        SYSTEM_PROMPT, USER_PROMPT = self.RESPOND_PROMPT(hits, query)
        result = self.tall({"content":[{"system": SYSTEM_PROMPT}, {"user": USER_PROMPT}]})

        return Response(result=result, hits=hits, query=query)
