from fastapi import FastAPI, HTTPException, Query
from model.recommender import Recommender

app = FastAPI(title="Recommender API")

recommender = Recommender(data_dir="data")

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/products")
def list_products():
    return recommender.all_products()

@app.get("/recommend/{product_id}")
def recommend(product_id: int, n: int = Query(5, ge=1, le=50)):
    try:
        recs = recommender.recommend_by_id(product_id, n=n)
        return {"product_id": product_id, "recommendations": recs}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
