import json
import numpy as np
import time
import os
from model.embedder import EmbedderHF

def gerar():
    os.makedirs("data", exist_ok=True)
    embedder = EmbedderHF(model_name="sentence-transformers/all-MiniLM-L6-v2")  # troque se quiser outro

    with open("data/produtos_raw.json", "r", encoding="utf-8") as f:
        dados = json.load(f)

    # suporta os formatos que você usou: 
    # [ { "products": [...] } ]  OR  { "products": [...] }  OR  [ {...}, {...} ] (lista direta)
    if isinstance(dados, list) and len(dados) > 0 and "products" in dados[0]:
        produtos = dados[0]["products"]
    elif isinstance(dados, dict) and "products" in dados:
        produtos = dados["products"]
    elif isinstance(dados, list) and all(isinstance(i, dict) and "product_id" in i for i in dados):
        produtos = dados
    else:
        raise Exception("Formato de produtos_raw.json não reconhecido. Verifique o arquivo em data/.")

    produtos_index = []
    embeddings = []

    for p in produtos:
        texto = (
            f"{p.get('product_name','')} - {p.get('description','')} - subcategoria: {p.get('subcategory',{}).get('name','')}"
        )

        emb = embedder.embed_text(texto)
        embeddings.append(emb)

        produtos_index.append({
            "product_id": p.get("product_id"),
            "product_name": p.get("product_name"),
            "price": p.get("price"),
            "description": p.get("description"),
            "subcategory": p.get("subcategory"),
            "theme_ids": p.get("theme_ids", []),
            "image_urls": p.get("image_urls", []),
        })

        time.sleep(0.02)

    embeddings_arr = np.array(embeddings, dtype=np.float32)
    np.save("data/embeddings.npy", embeddings_arr)

    with open("data/produtos_index.json", "w", encoding="utf-8") as f:
        json.dump(produtos_index, f, indent=4, ensure_ascii=False)

    print("Treinamento finalizado. Arquivos gerados em data/: embeddings.npy e produtos_index.json")

if __name__ == "__main__":
    gerar()
