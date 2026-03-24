import logging

import psycopg2

from config.settings import settings

logging.basicConfig(level=logging.INFO)
db_url = settings.SUPABASE_DB_URL
print(f"Tentando conectar ao banco: {db_url}")
try:
    conn = psycopg2.connect(db_url, connect_timeout=5)
    print("Conexão bem sucedida!")
    conn.close()
except Exception as e:
    print(f"Erro de conexão: {e}")
print("Fim do teste.")
