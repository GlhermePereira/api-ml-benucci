from fastapi import FastAPI, HTTPException, Query
from model.recommender import Recommender
from model.embedder import EmbedderHF
from service.product_service import ProductService
from data.product_repository import ProductRepository

# cria instância do repository
repository = ProductRepository()

# injeta o repository no service
service = ProductService(repository)

app = FastAPI(title="Recommender API")

embedder = EmbedderHF()

@app.get("/products", tags=["Produtos"])
def get_all_products():
    """
    Retorna todos os produtos do banco.
    """
    try:
        products = service.list_all_products()
        return {"total": len(products), "products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/", tags=["Home"])
def home():
    """
    Rota principal da API, retorna mensagem de boas-vindas e total de produtos.
    """
    return {
        "message": "Bem-vindo à API de Recomendação de Produtos do Benucci Artes!",
    }

@app.get("/recommend/{product_id}/{category_id}")
def recommend(product_id: int, category_id: int, n: int = Query(10, ge=1, le=50)):
    try:
        # Instancia o recommender só com produtos da categoria desejada
        recommender = Recommender(embedder, category_id=category_id)
        recs = recommender.recommend_by_id(product_id, top_k=n)
        return {"product_id": product_id, "recommendations": recs}

    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
