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
        self._texts = [json.dumps({"meta":atom.meta, "summary":atom.data}) for atom in self.MEMORY.iterate_atoms()]
        
        
        self.matrix = self.model.encode(self._texts)

    def __call__(self, query: str, top_k: int = 3):
        """Return top_k matches as list of {'entry': entry, 'score': float}.

        If no index exists (no texts), falls back to returning the first top_k entries
        with zero scores, similar to DumpRetrieve's weak fallback.
        """
        # if self.matrix is None:
        #     return [{'entry': e, 'score': 0.0} for e in self._texts[:top_k]]
        from . import YOG
        import numpy as np
        YOG.info(("Querying VectorRetrieve with query:", query))
        sims = self.model.similarity(self.model.encode([query]), self.matrix)[0]
        idxs = np.argsort(-sims)[:top_k]
        results = [{'entry': self._texts[int(idx)], 'score': float(sims[int(idx)])} for idx in idxs]
        return results


"""
import re, json
from os.path import join as opj
from .....paths import MEMORY_DIR

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import numpy as np

from ....Base import Retrieve

class VideoRetrieve(Retrieve):
    def __init__(self, RESPOND):
        super().__init__()
        self.name = "VideoRetrieve"
        self.RESPOND = RESPOND

        from ... import VideoMemory
        self.MEMOR = VideoMemory(self.RESPOND.METHOD.MEMORIZER)

        self.vectorizer = None
        self.matrix = None

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
        # collect candidate entries similar to DumpRetrieve's annotations
        self._entries = self._collect_entries()
        self._texts = [self._text_from_entry(e) for e in self._entries]
        self.vectorizer = TfidfVectorizer()
        self.matrix = self.vectorizer.fit_transform(self._texts)

    def _collect_entries(self):
        return [atom.data for atom in self.MEMORY.iterate_everything()]

    def _text_from_entry(self, e: dict) -> str:
        return e

    def __call__(self, query: str, top_k: int = 3):
        if self.matrix is None:
            return [{'entry': e, 'score': 0.0} for e in self._entries[:top_k]]
        from . import YOG
        YOG.info(("Querying VectorRetrieve with query:", query))
        qv = self.vectorizer.transform([query])
        sims = cosine_similarity(qv, self.matrix)[0]
        idxs = np.argsort(-sims)[:top_k]
        results = []
        for idx in idxs:
            results.append({'entry': self._entries[int(idx)], 'score': float(sims[int(idx)])})
        return results

"""