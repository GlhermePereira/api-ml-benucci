import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer
from data.bd import get_products_by_category


def normalize(v: np.ndarray) -> np.ndarray:
    """
    Normaliza o vetor para norma L2 (evita problemas na similaridade)
    e garante que seja um vetor 1D.
    """
    v = np.ravel(v)  # transforma em 1D
    norm = np.linalg.norm(v)
    return v / norm if norm > 0 else v


class EmbedderHF:
    """
    Embedder leve utilizando ONNX Runtime + Tokenizers,
    compatível com Python 3.11 e deploys sem GPU.
    """

    def __init__(
        self,
        model_path: str = "model/all-MiniLM-L6-v2.onnx",
        tokenizer_path: str = "model/tokenizer.json",
        max_length: int = 384
    ):
        print("Inicializando Embedder ONNX...")
        self.session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
        self.tokenizer = Tokenizer.from_file(tokenizer_path)
        self.max_length = max_length

    def embed_text(self, text: str) -> np.ndarray:
        tok = self.tokenizer.encode(text)

        # padding / truncamento
        input_ids = np.array([tok.ids[:self.max_length] + [0]*(self.max_length - len(tok.ids[:self.max_length]))], dtype=np.int64)
        attention_mask = np.array([tok.attention_mask[:self.max_length] + [0]*(self.max_length - len(tok.attention_mask[:self.max_length]))], dtype=np.int64)
        token_type_ids = np.zeros_like(input_ids, dtype=np.int64)

        inputs = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "token_type_ids": token_type_ids
        }

        outputs = self.session.run(None, inputs)
        emb = outputs[0][0]
        return normalize(np.array(emb, dtype=np.float32))


class EmbeddingStore:
    """
    Armazena textos/embeddings em memória e executa busca por similaridade.
    Pode carregar automaticamente produtos do banco.
    """

    def __init__(self, embedder: EmbedderHF, category_id: int = None):
        self.embedder = embedder
        self.store = []  # lista de tuplas (id, text, embedding)

        if category_id is not None:
            self._load_from_db(category_id)

    def _load_from_db(self, category_id: int):
        print(f"Carregando produtos da categoria {category_id}...")
        products = get_products_by_category(category_id)

        if not products:
            print("Nenhum produto encontrado no banco.")
            return

        for p in products:
            text = p.get("text") or p.get("description") or ""
            self.add(p["id"], text)

        print(f"Carregados {len(self.store)} produtos.")

    def add(self, item_id: str, text: str):
        emb = self.embedder.embed_text(text)
        self.store.append((item_id, text, emb))
        print(f"Produto {item_id} indexado.")

    def get_embedding(self, item_id: str):
        for stored_id, _, emb in self.store:
            if stored_id == item_id:
                return emb
        return None

    def search_similar(self, query_text: str, top_k: int = 5):
        if not self.store:
            return []

        q_emb = self.embedder.embed_text(query_text)

        sims = []
        for item_id, _, emb in self.store:
            # garante flatten para evitar erros de array
            sim = float(np.dot(q_emb.flatten(), emb.flatten()))
            sims.append((item_id, sim))

        sims.sort(key=lambda x: x[1], reverse=True)
        return sims[:top_k]


if __name__ == "__main__":
    embedder = EmbedderHF()
    store = EmbeddingStore(embedder, category_id=1)

    print("\nBusca de exemplo:")
    print(store.search_similar("Texto de exemplo"))
