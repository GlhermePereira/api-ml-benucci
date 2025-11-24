from sentence_transformers import SentenceTransformer

class EmbedderHF:
    def __init__(self, model_name: str = "sentence-transformers/all-mpnet-base-v2"):
        print("Carregando modelo local (sentence-transformers). Isso pode levar alguns segundos...")
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str):
        # garante lista -> vetor numpy
        emb = self.model.encode([text], show_progress_bar=False)[0]
        return emb.tolist()
