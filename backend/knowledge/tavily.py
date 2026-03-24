import logging

from agno.tools.tavily import TavilyTools

from config.settings import settings

# Singletons para Lazy Load
_tavily_basic = None
_tavily_advanced = None

def get_tavily_basic():
    global _tavily_basic
    if _tavily_basic is None:
        try:
            if not settings.TAVILY_API_KEY:
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
            if not settings.TAVILY_API_KEY:
                logging.warning("TAVILY_API_KEY não encontrada nas configurações.")
                return None
            _tavily_advanced = TavilyTools(api_key=settings.TAVILY_API_KEY, search_depth="advanced")
        except Exception as e:
            logging.error(f"Erro ao inicializar Tavily Advanced: {e}")
            return None
    return _tavily_advanced

def busca_rapida(query: str = None, **kwargs) -> str:
    """Usa a busca rápida e cirúrgica do Tavily para fatos simples, placares, cotações e notícias diárias.
    Extremamente rápida e imune a falhas de timeout.

    Args:
        query (str, optional): A consulta de pesquisa.
    """
    # Flexibilidade para diferentes nomes de parâmetros (ex: gpt-5 enviando 'parameters')
    query = query or kwargs.get("parameters") or kwargs.get("search_query")
    if not query:
        return "Erro: O parâmetro 'query' é obrigatório para a busca."
    try:
        basic = get_tavily_basic()
        if not basic:
            return "Erro: TAVILY_API_KEY não configurada corretamente."
        return basic.web_search_using_tavily(query)
    except Exception as e:
        return f"Erro na busca rápida: {e}"

def busca_profunda(query: str = None, **kwargs) -> str:
    """Busca profunda na internet usando Tavily. USE APENAS para pesquisa de conteúdo, análise de concorrentes ou quando precisar ler artigos densos.
    Atenção: É lenta e tem risco de timeout se usada muitas vezes.

    Args:
        query (str, optional): A consulta de pesquisa detalhada.
    """
    # Flexibilidade para diferentes nomes de parâmetros
    query = query or kwargs.get("parameters") or kwargs.get("search_query")
    if not query:
        return "Erro: O parâmetro 'query' é obrigatório para a busca."
    try:
        advanced = get_tavily_advanced()
        if not advanced:
            return "Erro: TAVILY_API_KEY não configurada corretamente."
        return advanced.web_search_using_tavily(query)
    except Exception as e:
        return f"Erro na busca profunda: {e}"
