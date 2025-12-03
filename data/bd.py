import psycopg2
from dotenv import load_dotenv
import os
from typing import List, Dict

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")

def get_products_by_category(category_id: int) -> List[Dict[str, str]]:
    """
    Retorna produtos filtrados por category_id.
    Cada produto é um dict: {"id": ..., "text": ...}
    """
    query = """
        SELECT p.id, p.name, p.description, c.name as category_name, s.name as subcategory_name
        FROM product p
        JOIN subcategory s ON p.subcategory_id = s.id
        JOIN category c ON s.category_id = c.id
        WHERE c.id = %s
    """

    product_list = []

    with psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        dbname=DB_NAME,
        port=DB_PORT
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (category_id,))
            for prod_id, name, description, category_name, subcategory_name in cursor.fetchall():
                text_to_embed = f"{name} - {description or ''} - {category_name} - {subcategory_name}"
                product_list.append({"id": prod_id, "text": text_to_embed})

    return product_list


# Teste rápido
if __name__ == "__main__":
    produtos = get_products_by_category(1)
    print(f"Total de produtos: {len(produtos)}")
    print(produtos[:3])
