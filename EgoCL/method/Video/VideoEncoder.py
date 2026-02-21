import os, json, numpy as np
class VideoEncoder:
    def __init__(self, ENCODER_PATH):
        self.ENCODER_PATH = ENCODER_PATH
    
    def __call__(self, *args, **kwargs):
        raise NotImplementedError("VideoEncoder is an abstract class. Please implement the forward method.")
    
    def sim(self, *args, **kwargs):
        raise NotImplementedError("VideoEncoder is an abstract class. Please implement the similarity method.")

class Qwen3VLEmbedder(VideoEncoder):
    def __init__(self, ENCODER_PATH):
        super().__init__(ENCODER_PATH)
        from models.qwen3_vl_embedding import Qwen3VLEmbedder
        self.model = Qwen3VLEmbedder(model_name_or_path=ENCODER_PATH)

    def call(self, *args, **kwargs):
        result = self.model.process(*args, **kwargs)
        if hasattr(result, "detach"):
            result = result.detach().cpu().numpy()
        return result

    def __call__(self, query):
        if isinstance(query, str):
            query = [query]
        if isinstance(query, list):
            for i, q in enumerate(query):
                if isinstance(q, str):
                    query[i] = {"image": q} if os.path.exists(q) and q.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')) else {"text": q}
                elif isinstance(q, dict):
                    assert "text" in q or "image" in q and len(q)==1, "Each query dict must contain either 'text' or 'image' key."
                    assert "text" not in q or isinstance(q["text"], str), "The 'text' value must be a string."
                    assert "image" not in q or (isinstance(q["image"], str) and os.path.exists(q["image"]) and q["image"].endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))), "The 'image' value must be a valid image file path."
                else:
                    raise ValueError("Unsupported query type in list: {}".format(type(q)))
            query_embeddings = self.call(query)
        elif isinstance(query, np.ndarray):
            query_embeddings = query
        else:
            raise ValueError("Unsupported query type: {}".format(type(query)))
        return query_embeddings
        
    def sim(self, query, document):
        query_embeddings, document_embeddings = self(query), self(document)
        return (query_embeddings @ document_embeddings.T)
    
class SentenceTransformerEncoder(VideoEncoder):
    def __init__(self, ENCODER_PATH):
        super().__init__(ENCODER_PATH)
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(ENCODER_PATH)

    def call(self, *args, **kwargs):
        return self.model.encode(*args, **kwargs)

    def __call__(self, query):
        if isinstance(query, str):
            query = [query]

        if isinstance(query, list):
            query_embeddings = self.call(query)
        elif isinstance(query, np.ndarray):
            query_embeddings = query
        else:
            raise ValueError("Unsupported query type: {}".format(type(query)))
        return query_embeddings

    def sim(self, query, document):
        query_embeddings, document_embeddings = self(query), self(document)
        return self.model.similarity(query_embeddings, document_embeddings)
    
def VideoEncoderFactory(name):
    n = os.path.basename(name).lower()
    if n.find('vl') != -1 and n.find('qwen3') != -1:
        return Qwen3VLEmbedder(name)
    else:
        return SentenceTransformerEncoder(name)