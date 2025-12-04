# services/product_service.py
from typing import List, Dict
from data.product_repository import ProductRepository

class ProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    def list_all_products(self) -> List[Dict[str, str]]:
        """
        Retorna todos os produtos do banco.
        """
        return self.repository.get_all_products()
