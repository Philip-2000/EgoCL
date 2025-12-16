import re, json
from os.path import join as opj
from .....paths import MEMORY_DIR

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

import numpy as np

from ....Base import Retrieve

class DumpRetrieve(Retrieve):
    def __init__(self, RESPOND):
        super().__init__()
        self.name = "DumpRetrieve"
        self.RESPOND = RESPOND

        from ... import DumpMemory
        self.MEMOR = DumpMemory(self.RESPOND.METHOD.MEMORIZER)

        # collect candidate entries similar to DumpRetrieve's annotations
        # self._entries = self._collect_entries()
        # self._texts = [self._text_from_entry(e) for e in self._entries]

        # if len(self._texts) > 0:
        #     self.vectorizer = TfidfVectorizer()
        #     self.matrix = self.vectorizer.fit_transform(self._texts)
        # else:
        #     self.vectorizer = None
        #     self.matrix = None

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
        return self.METHOD.MEMORY
        #such self.METHOD.MEMORY is the original MEMORY of DumpMethod
        #which is the place for the memory to write into
        #actually, we can use that object to retrieve from as well
        #the reason why we create a new attribute self.MEMOR
        #is to test the "save" and "load" function runs properly
        #so I "save" the things from self.METHOD.MEMORY into disk file
        #and then "load" them back into self.MEMOR,
        #and then retrieve from self.MEMOR
        #In the Future, if we set self.MEMORY = self.METHOD.MEMORY,
        #then the time of DumpRetrieve will be exactly the same as that of DumpMemorize
        #which is also the time of DumpMethod
        #so that two part will always be synchronized in time, so no "save" and "load" sync is needed


    def load(self, seconds_experience):
        self.MEMOR.load(seconds_experience)
        # collect candidate entries similar to DumpRetrieve's annotations
        self._entries = self._collect_entries()
        self._texts = [self._text_from_entry(e) for e in self._entries]

        self.vectorizer = TfidfVectorizer()
        self.matrix = self.vectorizer.fit_transform(self._texts)

    # def __call__(self, question):
    #     # In DumpRetrieve, we do not retrieve any experience
    #     return None

    def _collect_entries(self):
        return [anno.to_dict for anno in self.MEMORY.MEMORY]

    def _text_from_entry(self, e: dict) -> str:
        return e['information']['text']
        # prefer structured information.text
        txt = ''
        info = e.get('information') if isinstance(e.get('information'), dict) else {}
        txt = info.get('text', '') if info else ''
        if txt:
            return txt

        # otherwise gather all string fields (shallow)
        parts = []
        for k, v in e.items():
            if isinstance(v, str):
                parts.append(v)
            elif isinstance(v, dict):
                for vv in v.values():
                    if isinstance(vv, str):
                        parts.append(vv)
        return ' '.join(parts)

    def __call__(self, query: str, top_k: int = 3):
        """Return top_k matches as list of {'entry': entry, 'score': float}.

        If no index exists (no texts), falls back to returning the first top_k entries
        with zero scores, similar to DumpRetrieve's weak fallback.
        """
        if self.matrix is None:
            return [{'entry': e, 'score': 0.0} for e in self._entries[:top_k]]
        print("Querying VectorRetrieve with query:", query)
        qv = self.vectorizer.transform([query])
        sims = cosine_similarity(qv, self.matrix)[0]
        idxs = np.argsort(-sims)[:top_k]
        results = []
        for idx in idxs:
            results.append({'entry': self._entries[int(idx)], 'score': float(sims[int(idx)])})
        return results