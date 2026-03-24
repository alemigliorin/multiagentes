import logging
import os
import sys

# Ajustar path para importar do backend
sys.path.append(os.getcwd())

from knowledge.pdf_knowledge import get_pdf_knowledge

logging.basicConfig(level=logging.INFO)
print("Tentando inicializar pdf_knowledge...")
try:
    knowledge = get_pdf_knowledge()
    print(f"Sucesso: {knowledge}")
except Exception as e:
    print(f"Erro: {e}")
print("Fim do teste.")
