import os
import logging
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain_openai import ChatOpenAI

from app.schemas.requisicao import DecisaoAgente

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")

# O OpenRouter segue o contrato da OpenAI, bastando apontar o base_url
llm = ChatOpenAI(
    model=OPENROUTER_MODEL,
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL,
    temperature=0,  # Temperatura 0 reduz alucinação e mantém decisões consistentes
)

SYSTEM_PROMPT = """
Você é o **ME Genius**, um Agente Autônomo de Compras Corporativas B2B do Mercado Eletrônico.
Seu papel é auxiliar solicitantes a consultarem produtos no catálogo e emitirem requisições estruturadas.

Diretrizes:
1. Use as ferramentas do catálogo MCP (`buscar_produtos`, `detalhar_produto`) para obter informações reais.
2. Respeite as restrições orçamentárias e especificações solicitadas pelo usuário.
3. Se o catálogo retornar falha ou timeout, explique amigavelmente a instabilidade momentânea do serviço e retorne a lista de itens vazia.
4. Quando os itens forem aprovados, preencha a lista `itens` na resposta estruturada; caso contrário, deixe `itens` vazia.
"""


async def executar_agente(mensagem_usuario: str) -> DecisaoAgente:
    """Conecta ao servidor MCP com MCPAdapter, cria o agente e retorna a decisão estruturada."""
    logger.info("Conectando ao servidor MCP em %s", MCP_SERVER_URL)

    # MCPAdapter abre a sessão SSE com o servidor MCP e adapta as tools para o formato LangChain
    async with MCPAdapter(MCP_SERVER_URL) as adapter:
        mcp_tools = await adapter.list_tools()
        logger.info("Ferramentas MCP carregadas: %s", [t.name for t in mcp_tools])

        # response_format obriga o agente a devolver um objeto Pydantic (DecisaoAgente) ao final do loop
        agent = create_agent(
            model=llm,
            tools=mcp_tools,
            system_prompt=SYSTEM_PROMPT,
            response_format=DecisaoAgente,
        )

        logger.info("Executando agente para a mensagem: %s", mensagem_usuario)
        resultado = await agent.ainvoke({
            "messages": [{"role": "user", "content": mensagem_usuario}]
        })

    # Com response_format definido, o objeto Pydantic validado fica na chave "structured_response"
    decisao: DecisaoAgente = resultado["structured_response"]
    logger.info("Decisão do agente concluída com %d item(ns)", len(decisao.itens))
    return decisao
