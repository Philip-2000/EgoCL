from ...Base import Respond
from . import YOG
class VideoRespond(Respond):
    def __init__(self, METHOD, **kwargs):
        super().__init__()
        from . import VideoRetrieve
        from ...VlmBase import QwenVLM, DeepSeekLLM, QwenLLM, MyLLM
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
        
        from .. import RAG_PROMPT
        self.RETRIEVE = VideoRetrieve(self)
        self.VlmBase = MyLLM(kwargs.get("MODEL", "Qwen3-VL-8B-Instruct")) # QwenLLM() # QwenVLM() # DeepSeekLLM() #
        self.RESPOND_PROMPT, self.RAG_PROMPT = RESPOND_PROMPT, RAG_PROMPT
        self.I_Dont_Know = kwargs.get("I_Dont_Know", True) # False)#

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
        import json
        hits = self.RETRIEVE(query)
        hits = json.dumps(hits, ensure_ascii=False)
        YOG.debug(("VideoRespond Hits: ", hits), tag="VideoRespond")
        hits = self.VlmBase.text(self.RAG_PROMPT + hits)
        query = self.VlmBase.text(query)
        
        return self.VlmBase({"content":[{"text":self.RESPOND_PROMPT + hits + "\n\n" + query}]})
        #return self.VlmBase(hits+"\n\n"+query, self.SYSTEM_PROMPT)