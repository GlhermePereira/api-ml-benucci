import os
from dotenv import load_dotenv
import psycopg2

# Carrega variáveis do .env
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode='require'  # Supabase requer SSL
    )
    cursor = conn.cursor()
    print("Conexão bem-sucedida!")

    # Exemplo: buscar produtos
    cursor.execute("SELECT * FROM product;")
    produtos = cursor.fetchall()
    for produto in produtos:
        print(produto)

    cursor.close()
    conn.close()
    print("Conexão encerrada.")

except Exception as e:
    print(f"Erro ao conectar: {e}")
