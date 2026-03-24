import logging
import time


def _delegate(agent, input_text: str, label: str) -> str:
    """
    Função privada para padronizar execução, logging e tratamento de erros na delegação.
    """
    start_time = time.time()
    try:
        logging.info(f"--- Iniciando tarefa em {label}: {input_text[:50]}... ---")
        response = agent.run(input_text)
        duration = time.time() - start_time
        logging.info(f"--- Tarefa em {label} concluída em {duration:.2f}s ---")
        return response.content
    except Exception as e:
        logging.error(f"Erro na delegação para {label}: {e}")
        return f"Desculpe, ocorreu um erro ao processar sua solicitação com o {label}."

def create_delegation(agent_or_factory, label: str, docstring: str):
    """
    Cria uma função de delegação para o Orquestrador.
    Suporta instâncias de Agent ou callables (para lazy loading).
    """
    def delegate(input_text: str, **kwargs) -> str:
        # Resolve o agente: se for função, chama; se não, usa a instância
        agent = agent_or_factory() if callable(agent_or_factory) else agent_or_factory
        return _delegate(agent, input_text, label)

    # Define o nome da função (remove 'get_' se for factory para seguir padrão)
    name = agent_or_factory.__name__ if callable(agent_or_factory) else agent_or_factory.name
    if name.startswith("get_"):
        name = name[4:]

    delegate.__doc__ = docstring
    delegate.__name__ = f"acionar_{name}"
    return delegate
