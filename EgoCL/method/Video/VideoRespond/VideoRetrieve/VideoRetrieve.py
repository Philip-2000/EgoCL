import re, json
from os.path import join as opj
from .....paths import MEMORY_DIR


from ....Base import Retrieve

class VideoRetrieve(Retrieve):
    def __init__(self, RESPOND):
        super().__init__()
        self.name = "VideoRetrieve"
        self.RESPOND = RESPOND

        from ... import VideoMemory
        self.MEMOR = VideoMemory(self.RESPOND.METHOD.MEMORIZER)

        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer("/mnt/data/models/Qwen3-Embedding-0.6B")
        self.matrix = []

    @property
    def EXPERIENCE(self):
        return self.RESPOND.EXPERIENCE

    @property
    def METHOD(self):
        return self.RESPOND.METHOD

    @property
    def TIME(self):
        return self.MEMORY.TIME

    @property
    def MEMORY(self):
        return self.MEMOR

    def load(self, seconds_experience):
        self.MEMOR.load(seconds_experience)
        
        #self._texts = [atom.data for atom in self.MEMORY.iterate_everything()]
        self._texts = [json.dumps({"meta":atom.meta, "summary":atom.data}, ensure_ascii=False) for atom in self.MEMORY.iterate_atoms()]
        
        
        self.matrix = self.model.encode(self._texts)

    def __call__(self, query: str, top_k: int = 3):
        from . import YOG
        import numpy as np
        YOG.info(("Querying VectorRetrieve with query:", query))
        sims = self.model.similarity(self.model.encode([query]), self.matrix)[0]
        idxs = np.argsort(-sims)[:top_k]
        # results = [{'entry': self._texts[int(idx)], 'score': float(sims[int(idx)])} for idx in idxs]
        results = [ self._texts[int(idx)] for idx in idxs]
        # print("results", results)
        return results

