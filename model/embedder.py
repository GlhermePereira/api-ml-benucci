import numpy as np
from sentence_transformers import SentenceTransformer
from data.bd import get_products_by_category  # sua função do bd.py que retorna produtos filtrados
from sklearn.metrics.pairwise import cosine_similarity

class EmbedderHF:
    def __init__(self, model_name: str = "sentence-transformers/all-mpnet-base-v2"):
        print("Carregando modelo local (sentence-transformers). Isso pode levar alguns segundos...")
        self.model = SentenceTransformer(model_name)

    def embed_text(self, text: str):
        emb = self.model.encode([text], show_progress_bar=False)[0]
        return emb.tolist()

class EmbeddingStore:
    def __init__(self, embedder: EmbedderHF, category_id: int = None):
        self.store = []  # lista de tuplas (id, text, embedding)
        self.embedder = embedder
        if category_id is not None:
            self._load_from_db(category_id)

    def _load_from_db(self, category_id: int):
        products = get_products_by_category(category_id)  # retorna lista de dicts com id e text
        for p in products:
            self.add(p["id"], p["text"])

    def add(self, id: str, text: str):
        embedding = np.array(self.embedder.embed_text(text))
        self.store.append((id, text, embedding))
        print(f"Adicionado: {id}")

    def get_embedding(self, id: str):
        for item in self.store:
            if item[0] == id:
                return item[2]
        return None

    def search_similar(self, query_text: str, top_k: int = 5):
        query_embedding = np.array(self.embedder.embed_text(query_text))
        similarities = [
            (item[0], np.dot(query_embedding, item[2]) / (np.linalg.norm(query_embedding) * np.linalg.norm(item[2])))
            for item in self.store
        ]
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

# Exemplo de uso
if __name__ == "__main__":
    embedder = EmbedderHF()
    store = EmbeddingStore(embedder, category_id=1)  # já carrega produtos da categoria 1

    print("Produtos carregados e embeddings gerados.")
    results = store.search_similar("Texto de exemplo")
    print(results)
