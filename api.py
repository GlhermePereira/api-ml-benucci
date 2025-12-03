from fastapi import FastAPI, HTTPException, Query
from model.recommender import Recommender
from model.embedder import EmbedderHF

app = FastAPI(title="Recommender API")

embedder = EmbedderHF()

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
