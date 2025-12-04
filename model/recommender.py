import numpy as np
from model.embedder import EmbedderHF, EmbeddingStore


class Recommender:
    """
    Recomendador baseado em embeddings ONNX pré-normalizados.
    Ideal para ambientes sem GPU e com restrição de memória.
    """
    def __init__(self, embedder: EmbedderHF, category_id: int):
        self.store = EmbeddingStore(embedder, category_id)

        # Mapeia product_id → índice na store
        self.id2index = {
            pid: i for i, (pid, _, _) in enumerate(self.store.store)
        }

        # Matriz de embeddings
        self.embeddings = np.array([emb for _, _, emb in self.store.store])

        # Normalização prévia (L2)
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.normalized = self.embeddings / norms

        # Lista de produtos simplificada
        self.products = [
            {"product_id": pid, "text": text}
            for pid, text, _ in self.store.store
        ]

    def recommend_by_id(self, product_id: str, top_k: int = 5):
        """
        Retorna recomendações com base no produto indicado.
        Usa similaridade de cosseno via dot product (pois já normalizado).
        """
        if product_id not in self.id2index:
            raise KeyError(f"product_id {product_id} não encontrado")

        idx = self.id2index[product_id]

        query_emb = self.normalized[idx]  # (384,)
        sims = self.normalized @ query_emb  # dot product vetorial

        # Ordena por score decrescente
        order = np.argsort(sims)[::-1]

        results = []
        for i in order:
            if i == idx:
                continue  # ignora o próprio produto

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
    recommender = Recommender(embedder, category_id=1)

    print("Produtos carregados e embeddings gerados.")

    # produto inicial
    first_id = recommender.products[0]["product_id"]

    print(f"\nRecomendações para {first_id}:")
    print(recommender.recommend_by_id(first_id))
