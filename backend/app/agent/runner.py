import os
import logging
from typing import List, Optional
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langchain_openai import ChatOpenAI

from app.schemas.requisicao import DecisaoAgente, MensagemHistorico

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

SYSTEM_PROMPT = """Você é o **ME Genius**, Agente Autônomo de Compras Corporativas B2B do Mercado Eletrônico.
Analise a mensagem do usuário junto com o histórico da conversa e classifique a intenção em uma das 4 categorias abaixo antes de agir:

### 1. Classificação de Intenção e Fluxo de Ação

- **[CATEGORIA 1: PESQUISA / CONSULTA DE CATÁLOGO]**
  Quando o usuário quer apenas consultar produtos, ver opções, checar preços ou especificações (ex: "quais smartphones existem?", "o que tem até US$ 300?").
  - Se o usuário não especificou que tipo de produto procura (ex: falou apenas o preço "o que custa até US$ 300?"), pergunte qual categoria de produto ele deseja buscar (ex: smartphones, laptops, tablets, relógios) antes de listar itens aleatórios.
  - Se especificou o produto, consulte `buscar_produtos` / `detalhar_produto`, filtre estritamente pelo teto de preço (se houver) e apresente apenas os itens que atendem ao critério, perguntando ao final se deseja emitir a requisição.
  - **Importante:** Em pesquisas, **SEMPRE retorne `itens: []`** (não emita requisição até que o usuário peça para comprar).

- **[CATEGORIA 2: PEDIDO / EMISSÃO DE REQUISIÇÃO]**
  Quando o usuário pede para comprar, requisitar ou fechar pedido de itens específicos (ex: "compre 3 laptops até US$ 2.000 cada", "quero requisitar 2 unidades desse modelo").
  - Se faltar informação essencial (como qual é o produto), pergunte ao usuário e retorne `itens: []`.
  - Consulte o catálogo via MCP para obter os dados reais do produto (`id`, `title`, `price`, `category`, `description`, `shippingInformation`).
  - Se encontrar produto compatível dentro do orçamento, preencha a lista `itens` para emitir a requisição e confirme na `mensagem`.
  - Se todos os produtos da categoria pedida custarem acima do teto do usuário, **não emita a requisição (`itens: []`)**, explique que o valor excede o orçamento e informe o preço da opção mais próxima.

- **[CATEGORIA 3: SAUDAÇÃO OU PEDIDO INCOMPLETO]**
  Quando o usuário apenas cumprimenta ("oi", "bom dia") ou envia uma solicitação vaga ("preciso fazer uma compra").
  - Responda de forma cordial e objetiva pedindo o produto desejado, a quantidade e se há limite de orçamento.
  - Retorne `itens: []`.

- **[CATEGORIA 4: FORA DE ESCOPO (GUARDRAIL)]**
  Qualquer pergunta que não seja sobre catálogo de produtos ou compras B2B (ex: contas matemáticas, receitas, programação, curiosidades gerais).
  - **NÃO responda à pergunta.** Recuse educadamente informando que você atua exclusivamente como assistente de compras corporativas do Mercado Eletrônico e retorne `itens: []`.

### 2. Regras de Execução, Formatação e Resiliência
- **Idioma e Moeda:** Responda **100% em português do Brasil (pt-BR)**, sem frases em inglês. Apresente valores em **Dólares (US$)**.
- **Busca no MCP:** Na ferramenta `buscar_produtos`, passe o termo sempre em **inglês e no singular** (ex: `laptop`, `phone`, `tablet`, `watch`, `shirt`, `chair`).
- **Frete:** Preencha o campo `frete` de cada item traduzindo o `shippingInformation` da API para português (ex: "Envio em 2 semanas", "Envio em 3-5 dias úteis").
- **Resiliência:** Se as ferramentas MCP retornarem erro ou timeout, informe amigavelmente a instabilidade temporária do catálogo e retorne `itens: []`.
"""


_agent = None


async def obter_agente():
    """Inicializa o agente e carrega as tools do MCP apenas na primeira execução."""
    global _agent
    if _agent is None:
        # As tools retornadas por list_tools() mantêm a referência ao cliente MCP e continuam funcionais
        mcp_tools = await MCPAdapter(MCP_SERVER_URL).list_tools()
        logger.info("Ferramentas MCP carregadas uma única vez: %s", [t.name for t in mcp_tools])
        _agent = create_agent(
            model=llm,
            tools=mcp_tools,
            system_prompt=SYSTEM_PROMPT,
            response_format=DecisaoAgente,
        )
    return _agent


async def executar_agente(
    mensagem_usuario: str,
    historico: Optional[List[MensagemHistorico]] = None,
) -> DecisaoAgente:
    """Executa o agente em cache e retorna a decisão estruturada."""
    logger.info("[USUÁRIO -> AGENTE] Mensagem recebida: %s", mensagem_usuario)

    mensagens_contexto = [
        {"role": m.role, "content": m.content} for m in (historico or [])
    ]
    mensagens_contexto.append({"role": "user", "content": mensagem_usuario})

    agent = await obter_agente()
    resultado = await agent.ainvoke({"messages": mensagens_contexto})

    for msg in resultado.get("messages", []):
        for tc in getattr(msg, "tool_calls", []) or []:
            if tc.get("name") != "DecisaoAgente":
                logger.info("[TOOL CALL] %s(%s)", tc.get("name"), tc.get("args"))

    # Com response_format definido, o objeto Pydantic validado fica na chave "structured_response"
    decisao: DecisaoAgente = resultado["structured_response"]
    logger.info(
        "[AGENTE -> CHAT] Mensagem final: %s | Itens aprovados: %d",
        decisao.mensagem,
        len(decisao.itens),
    )
    return decisao
