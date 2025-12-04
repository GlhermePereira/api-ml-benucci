import json
import numpy as np
import os
from model.embedder import EmbedderHF


# ---------------------------------------------------------------------------
# Carregamento de Produtos
# ---------------------------------------------------------------------------
def carregar_produtos(path: str):
    """Carrega produtos de múltiplos formatos possíveis de produtos_raw.json."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    with open(path, "r", encoding="utf-8") as f:
        dados = json.load(f)

    # Caso: [ { "products": [...] } ]
    if isinstance(dados, list) and dados and isinstance(dados[0], dict):
        if "products" in dados[0]:
            return dados[0]["products"]

    # Caso: { "products": [...] }
    if isinstance(dados, dict) and "products" in dados:
        return dados["products"]

    # Caso: lista direta de produtos
    if isinstance(dados, list) and all(isinstance(p, dict) and "product_id" in p for p in dados):
        return dados

    raise ValueError(
        "Formato inválido em produtos_raw.json. "
        "Esperado: { 'products': [...] } ou lista de objetos contendo 'product_id'."
    )


# ---------------------------------------------------------------------------
# Montagem de Texto para Embedding
# ---------------------------------------------------------------------------
def montar_texto_produto(produto: dict) -> str:
    """Concatena campo relevantes do produto para gerar o texto do embedding."""
    nome = produto.get("product_name", "")
    desc = produto.get("description", "")
    subcat = produto.get("subcategory", {}).get("name", "")

    return f"{nome} - {desc} - subcategoria: {subcat}"


# ---------------------------------------------------------------------------
# Processamento principal
# ---------------------------------------------------------------------------
def gerar():
    print("Iniciando geração de embeddings...\n")

    # Diretório de saída
    os.makedirs("data", exist_ok=True)

    # Modelo transformes leve
    embedder = EmbedderHF(model_name="sentence-transformers/all-MiniLM-L6-v2")

    produtos_raw = "data/produtos_raw.json"
    produtos = carregar_produtos(produtos_raw)

    total = len(produtos)
    print(f"Total de produtos carregados: {total}\n")

    produtos_index = []
    embeddings = []

    for idx, produto in enumerate(produtos, start=1):
        texto = montar_texto_produto(produto)
        emb = embedder.embed_text(texto)

        embeddings.append(emb)

        produtos_index.append({
            "product_id": produto.get("product_id"),
            "product_name": produto.get("product_name"),
            "price": produto.get("price"),
            "description": produto.get("description"),
            "subcategory": produto.get("subcategory"),
            "theme_ids": produto.get("theme_ids", []),
            "image_urls": produto.get("image_urls", []),
        })

        if idx % 20 == 0 or idx == total:
            print(f"{idx}/{total} produtos processados...")

    print("\nSalvando arquivos...")

    # Salva embeddings
    embeddings_np = np.array(embeddings, dtype=np.float32)
    np.save("data/embeddings.npy", embeddings_np)

    # Salva índice dos produtos
    with open("data/produtos_index.json", "w", encoding="utf-8") as f:
        json.dump(produtos_index, f, indent=4, ensure_ascii=False)

    print("Processo finalizado com sucesso.")
    print("Arquivos gerados: data/embeddings.npy e data/produtos_index.json\n")


if __name__ == "__main__":
    gerar()
