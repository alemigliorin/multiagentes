import logging
import concurrent.futures

from agno.tools.tavily import TavilyTools

from config.settings import settings

# Singletons para Lazy Load
_tavily_basic = None
_tavily_advanced = None
_search_executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

def get_tavily_basic():
    global _tavily_basic
    if _tavily_basic is None:
        try:
            if getattr(settings, 'TAVILY_API_KEY', None) is None:
                logging.warning("TAVILY_API_KEY não encontrada nas configurações.")
                return None
            _tavily_basic = TavilyTools(api_key=settings.TAVILY_API_KEY, search_depth="basic", max_tokens=2000)
        except Exception as e:
            logging.error(f"Erro ao inicializar Tavily Basic: {e}")
            return None
    return _tavily_basic

def get_tavily_advanced():
    global _tavily_advanced
    if _tavily_advanced is None:
        try:
            if getattr(settings, 'TAVILY_API_KEY', None) is None:
                logging.warning("TAVILY_API_KEY não encontrada nas configurações.")
                return None
            _tavily_advanced = TavilyTools(api_key=settings.TAVILY_API_KEY, search_depth="advanced")
        except Exception as e:
            logging.error(f"Erro ao inicializar Tavily Advanced: {e}")
            return None
    return _tavily_advanced

def _duckduckgo_fallback(query: str, max_results: int = 5) -> str:
    """Busca de emergência via DuckDuckGo, retornando um bloco de texto legível para o orquestrador/pesquisador."""
    try:
        from duckduckgo_search import DDGS
        logging.info(f"Iniciando busca emergencial DuckDuckGo para: '{query}'")
        
        results = DDGS().text(query, max_results=max_results)
        
        output = ["--- RESULTADOS ALTERNATIVOS (DUCKDUCKGO) ---"]
        for idx, r in enumerate(results):
            title = r.get('title', 'Sem Título')
            link = r.get('href', r.get('link', ''))
            body = r.get('body', '')
            output.append(f"[{idx+1}] Título: {title}\nLink: {link}\nTrecho: {body}\n")
            
        if len(output) <= 1:
            return f"Atenção O Orquestrador: Busca alternativa falhou em encontrar dados para '{query}'."
            
        return "\n".join(output)
    except ImportError:
        return "Erro Crítico: duckduckgo-search não está instalado no sistema para servir de fallback."
    except Exception as e:
        return f"Falha catastrófica: Nem a API primária nem o Fallback DuckDuckGo funcionaram. Erro do gerador: {e}"

def busca_rapida(query: str = None, **kwargs) -> str:
    """Usa a busca rápida e cirúrgica do Tavily para fatos simples, placares, cotações e notícias diárias.
    Extremamente rápida e imune a falhas de timeout com fallback pra DDGS.

    Args:
        query (str, optional): A consulta de pesquisa.
    """
    query = query or kwargs.get("parameters") or kwargs.get("search_query")
    if not query:
        return "Erro: O parâmetro 'query' é obrigatório para a busca."
    
    try:
        basic = get_tavily_basic()
        if not basic:
            return _duckduckgo_fallback(query, max_results=5)
            
        future = _search_executor.submit(basic.web_search_using_tavily, query)
        timeout = getattr(settings, 'TAVILY_TIMEOUT_RAPIDA', 10)
        return future.result(timeout=timeout)
    except concurrent.futures.TimeoutError:
        logging.warning(f"Timeout atingido ({timeout}s) na busca_rapida Tavily. Acionando Fallback DDGS.")
        return _duckduckgo_fallback(query, max_results=5)
    except Exception as e:
        logging.error(f"Erro na busca rápida (Tavily): {e}. Acionando Fallback.")
        return _duckduckgo_fallback(query, max_results=5)

def busca_profunda(query: str = None, **kwargs) -> str:
    """Busca profunda na internet usando Tavily. USE APENAS para pesquisa de conteúdo, análise de concorrentes ou quando precisar ler artigos densos.
    Tem um timeout longo tolerável, com fallback automático pra DDGS caso exceda o tempo.

    Args:
        query (str, optional): A consulta de pesquisa detalhada.
    """
    query = query or kwargs.get("parameters") or kwargs.get("search_query")
    if not query:
        return "Erro: O parâmetro 'query' é obrigatório para a busca."
    
    try:
        advanced = get_tavily_advanced()
        if not advanced:
            return _duckduckgo_fallback(query, max_results=10)
            
        future = _search_executor.submit(advanced.web_search_using_tavily, query)
        timeout = getattr(settings, 'TAVILY_TIMEOUT_PROFUNDA', 20)
        return future.result(timeout=timeout)
    except concurrent.futures.TimeoutError:
        logging.warning(f"Timeout atingido ({timeout}s) na busca_profunda Tavily. Acionando Fallback DDGS.")
        return _duckduckgo_fallback(query, max_results=10)
    except Exception as e:
        logging.error(f"Erro na busca profunda (Tavily): {e}. Acionando Fallback.")
        return _duckduckgo_fallback(query, max_results=10)
