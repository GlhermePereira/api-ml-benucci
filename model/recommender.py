import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from model.embedder import EmbedderHF, EmbeddingStore 

class Recommender:
    def __init__(self, embedder: EmbedderHF, category_id: int):
        self.store = EmbeddingStore(embedder, category_id)
        self.id2index = {id_: i for i, (id_, _, _) in enumerate(self.store.store)}
        self.embeddings = np.array([item[2] for item in self.store.store])
        # normaliza embeddings para usar similaridade de cosseno direto
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.normalized = self.embeddings / norms
        self.products = [{"product_id": item[0], "text": item[1]} for item in self.store.store]

    def recommend_by_id(self, product_id: str, top_k: int = 5):
        if product_id not in self.id2index:
            raise KeyError(f"product_id {product_id} não encontrado")
        idx = self.id2index[product_id]
        query = self.normalized[idx].reshape(1, -1)
        sims = cosine_similarity(query, self.normalized)[0]
        order = sims.argsort()[::-1]

        results = []
        for i in order:
            if i == idx:
                continue
            p = self.products[i].copy()
            p["_score"] = float(sims[i])
            results.append(p)
            if len(results) >= top_k:
                break
        return results

    def all_products(self):
        return self.products


# Exemplo de uso
if __name__ == "__main__":
    embedder = EmbedderHF()
    recommender = Recommender(embedder, category_id=1)  # carrega produtos da categoria 1

    print("Produtos carregados e embeddings gerados.")

    # recomendação pelo id do produto
    first_product_id = recommender.products[0]["product_id"]
    recommendations = recommender.recommend_by_id(first_product_id)
    print(f"Recomendações para {first_product_id}:")
    print(recommendations)
