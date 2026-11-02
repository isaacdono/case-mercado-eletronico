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
  Quando o usuário faz uma pergunta ou quer ver opções (ex: "quais smartphones existem?", "não tem samsung?", "o que tem até US$ 300?").
  - Se o usuário não especificou que tipo de produto procura (ex: falou apenas o preço "o que custa até US$ 300?"), pergunte qual categoria de produto ele deseja buscar antes de listar itens aleatórios.
  - Se especificou o produto ou marca, consulte `buscar_produtos` / `detalhar_produto`, filtre pelo teto de preço (se houver) e apresente as opções (nome, preço e prazo de entrega, **sem mostrar o ID interno no texto**), perguntando se deseja fechar o pedido.
  - **Importante:** Em perguntas/pesquisas, **SEMPRE retorne `itens: []`**.

- **[CATEGORIA 2: PEDIDO / EMISSÃO DE REQUISIÇÃO]**
  Quando o usuário pede diretamente para comprar ou confirma a escolha de um item (ex: "compre 3 laptops até US$ 2.000 cada", "quero 2 s10", "confirmado", "pode fechar").
  - Se faltar informação essencial (como qual é o produto), pergunte ao usuário e retorne `itens: []`.
  - Consulte o catálogo via MCP para obter os dados reais do produto (`id`, `title`, `price`, `category`, `description`, `shippingInformation`).
  - Se encontrar produto compatível dentro do orçamento, preencha a lista `itens` para emitir a requisição imediatamente e informe na `mensagem` que a requisição foi emitida (**não peça confirmação novamente quando já tiver preenchido `itens`, nem mostre o ID no texto**).
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
- **Busca no MCP:** Na ferramenta `buscar_produtos`, passe sempre **UMA ÚNICA PALAVRA** em inglês e no singular (ex: `samsung`, `s10`, `iphone`, `laptop`, `phone`, `tablet`, `watch`). **Nunca** passe duas palavras juntas (como `samsung s10` ou `samsung phone`), pois a busca faz match de substring contígua e retorna vazio.
- **Frete:** Preencha o campo `frete` de cada item traduzindo o `shippingInformation` da API para português (ex: "Envio em 2 semanas", "Envio em 3-5 dias úteis").
- **Erros:** Se as ferramentas MCP retornarem erro ou timeout, informe amigavelmente a instabilidade temporária do catálogo e retorne `itens: []`.
"""


async def executar_agente(
    mensagem_usuario: str,
    historico: Optional[List[MensagemHistorico]] = None,
) -> DecisaoAgente:
    """Conecta ao servidor MCP com MCPAdapter, cria o agente e retorna a decisão estruturada."""
    logger.info("[USUÁRIO -> AGENTE] Mensagem recebida: %s", mensagem_usuario)

    mensagens_contexto = [
        {"role": m.role, "content": m.content} for m in (historico or [])
    ]
    mensagens_contexto.append({"role": "user", "content": mensagem_usuario})

    async with MCPAdapter(MCP_SERVER_URL) as adapter:
        mcp_tools = await adapter.list_tools()

        # response_format obriga o agente a devolver um objeto Pydantic (DecisaoAgente) ao final do loop
        agent = create_agent(
            model=llm,
            tools=mcp_tools,
            system_prompt=SYSTEM_PROMPT,
            response_format=DecisaoAgente,
        )

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
