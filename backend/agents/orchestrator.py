from agents.delegation import create_delegation
from agents.factory import create_agent, get_model
from agents.specialists import get_agente_pdf, get_copywriter, get_criador_experts, get_criador_midia, get_juridico, get_pesquisador
from config.settings import settings

# --- FUNÇÕES DE DELEGAÇÃO (LAZY) ---

acionar_pesquisador = create_delegation(
    get_pesquisador, "Pesquisador",
    "Delega uma tarefa de busca de dados reais e atualizados na internet ao Pesquisador. "
    "NÃO USE ESTA FERRAMENTA para buscar informações em PDFs, relatórios corporativos internos, "
    "ou documentos específicos baixados/armazenados no sistema. Nesses casos, prefira SEMPRE acionar_agente_pdf."
)

acionar_copywriter = create_delegation(
    get_copywriter, "Copywriter",
    "Delega a tarefa de escrita persuasiva e criação de roteiros usando a voz do Expert ao Copywriter."
)

acionar_juridico = create_delegation(
    get_juridico, "Jurídico",
    "Delega a tarefa de revisão de compliance e limites legais de uma promessa ou texto ao Jurídico."
)

acionar_criador_experts = create_delegation(
    get_criador_experts, "Criador_Experts",
    "Delega a criação de identidade, big idea ou estratégia visual de um projeto ao Criador_Experts."
)

acionar_criador_midia = create_delegation(
    get_criador_midia, "Criador de Mídia",
    "Delega tarefas de criação audiovisual (imagens e vídeos) ao agente Criador de Mídia."
)

acionar_agente_pdf = create_delegation(
    get_agente_pdf, "Agente PDF",
    "Delega a tarefa de consulta e análise de documentos internos corporativos (PDFs) locais ao Agente PDF. "
    "USE ESTA FERRAMENTA quando o usuário perguntar sobre documentos que já foram carregados internamente no sistema, "
    "ANTES de tentar buscar na internet."
)

# --- ORQUESTRADOR ---

orquestrador = create_agent(
    name="orquestrador",
    description="Você é o Líder da Equipe e principal contato. Você delega tarefas e consolida o resultado final.",
    tools=[
        acionar_pesquisador,
        acionar_copywriter,
        acionar_juridico,
        acionar_criador_experts,
        acionar_criador_midia,
        acionar_agente_pdf,
    ],
    instructions_file="prompts/orquestrador.md",
    db_url=settings.SUPABASE_DB_URL,
    num_history_runs=20,
    model=get_model("openai", id=settings.ORCHESTRATOR_MODEL_ID)
)
