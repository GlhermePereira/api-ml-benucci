import psycopg2
from typing import List, Dict
from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")

class ProductRepository:
    def get_all_products(self) -> List[Dict[str, str]]:
        """
        Retorna todos os produtos do banco.
        Cada produto é um dict: {"id": ..., "name": ..., "description": ...}
        """
        query = """
            SELECT p.id, p.name, p.description, c.name as category_name, s.name as subcategory_name
            FROM product p
            JOIN subcategory s ON p.subcategory_id = s.id
            JOIN category c ON s.category_id = c.id
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
                cursor.execute(query)
                for prod_id, name, description, category_name, subcategory_name in cursor.fetchall():
                    product_list.append({
                        "id": prod_id,
                        "name": name,
                        "description": description,
                        "category": category_name,
                        "subcategory": subcategory_name
                    })

        return product_list
