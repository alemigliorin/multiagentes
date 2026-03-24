
import logging
import sys
import time

from agno.tools.tavily import TavilyTools
from dotenv import load_dotenv


# Forçar UTF-8 no print para evitar erros de charmap no Windows
def safe_print(*args, **kwargs):
    content = " ".join(map(str, args))
    try:
        sys.stdout.buffer.write((content + "\n").encode('utf-8'))
        sys.stdout.flush()
    except Exception:
        print(content)
# Carregar variáveis de ambiente
load_dotenv()

# Importar depois do env para garantir que variáveis de ambiente estejam carregadas
from agents.orchestrator import acionar_pesquisador, orquestrador

# Habilitar logs para ver as chamadas de ferramentas
logging.basicConfig(level=logging.INFO)

def test_tavily_direct():
    safe_print("--- Testando Tavily diretamente ---")
    try:
        tavily = TavilyTools(search_depth="basic", max_tokens=2000)
        result = tavily.web_search_using_tavily("Previsão do tempo em São Paulo hoje")
        safe_print("Resultado Tavily:", result[:300] + "...")
        return True
    except Exception as e:
        safe_print(f"Erro no Tavily direto: {e}")
        return False

def test_agent_search():
    safe_print("\n--- Testando Agente Pesquisador ---")
    try:
        t_start = time.time()
        result = acionar_pesquisador("Quem ganhou o Oscar de melhor filme em 2024?")
        duration = time.time() - t_start
        safe_print(f"Resultado do Agente ({duration:.2f}s):", result[:300] + "...")
        return True
    except Exception as e:
        safe_print(f"Erro no Agente: {e}")
        return False

def test_orchestrator():
    safe_print("\n--- Testando Orquestrador ---")
    try:
        t_start = time.time()
        # Pergunta que obriga o orquestrador a chamar o pesquisador
        response = orquestrador.run("Quais as 3 notícias mais quentes de hoje sobre IA? Pesquise agora.")
        duration = time.time() - t_start
        safe_print(f"Resposta do Orquestrador ({duration:.2f}s):", response.content)
        return True
    except Exception as e:
        safe_print(f"Erro no Orquestrador: {e}")
        return False

if __name__ == "__main__":
    start_total = time.time()

    if test_tavily_direct():
        t0 = time.time()
        if test_agent_search():
            t1 = time.time()
            test_orchestrator()
            safe_print(f"\nTempo Orquestrador Final: {time.time() - t1:.2f}s")

    safe_print(f"\nTempo total de execução: {time.time() - start_total:.2f}s")
