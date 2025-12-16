from ...Base import Respond
class DumpRespond(Respond):
    def __init__(self, METHOD):
        super().__init__()
        self.name = "DumpRespond"
        self.METHOD = METHOD
        
        from . import DumpRetrieve
        self.RETRIEVE = DumpRetrieve(self)

        from ...VlmBase import QwenVLM, DeepSeekLLM, QwenLLM
        self.VlmBase = QwenLLM() # DeepSeekLLM() #QwenVLM() #
        self.SYSTEM_PROMPT="You are a egocentric memory assistant that helps users to recall past events based on their stored memories.\
              You will be provided with retrieved relevant memories and a user query.\
              Your task is to generate a concise and informative response that accurately addresses the user's question using the provided memories.\
              If the memories do not contain sufficient information to answer the query, respond with 'I don't know based on the provided memories.'\
              Always ensure your answers are grounded in the retrieved content."
        
        self.RAG_PROMPT="The following are some of your retrieved memories, each one is provided in a dict format with timestamp, text, images or other useful information:\n"
        

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
        import json
        hits = self.RETRIEVE(query)
        hits = json.dumps(hits, ensure_ascii=False)
        # print("hits", type(hits))
        # print(hits)
        hits = self.VlmBase.text(self.RAG_PROMPT + hits)
        # print("query", type(query))
        # print(query)
        query = self.VlmBase.text(query)
        
        return self.VlmBase(hits+"\n\n"+query, self.SYSTEM_PROMPT)