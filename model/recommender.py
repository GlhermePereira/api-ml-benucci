import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import os

class Recommender:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self._load()

    def _load(self):
        idx_path = os.path.join(self.data_dir, "produtos_index.json")
        emb_path = os.path.join(self.data_dir, "embeddings.npy")

        with open(idx_path, "r", encoding="utf-8") as f:
            self.products = json.load(f)

        self.embeddings = np.load(emb_path).astype("float32")

        # normalizar embeddings para usar cosine similarity de forma direta
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.normalized = self.embeddings / norms

        # mapa id -> index
        self.id2idx = {p["product_id"]: i for i, p in enumerate(self.products)}

    def recommend_by_id(self, product_id, n=5):
        if product_id not in self.id2idx:
            raise KeyError(f"product_id {product_id} não encontrado")

        idx = self.id2idx[product_id]
        query = self.normalized[idx].reshape(1, -1)
        sims = cosine_similarity(query, self.normalized)[0]  # entre -1 e 1

        # ordena decrescente (maior similaridade primeiro), ignora o próprio
        order = sims.argsort()[::-1]
        results = []
        for i in order:
            if i == idx:
                continue
            p = self.products[i].copy()
            # converte similaridade em score decimal coerente (quanto maior = mais similar)
            p["_score"] = float(sims[i])
            results.append(p)
            if len(results) >= n:
                break

        return results

    def all_products(self):
        return self.products
