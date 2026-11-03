# ME Genius — Agente de Compras B2B

Aplicação desenvolvida para o case técnico de **AI Forward Deployed Engineer (AI FDE)** no **Mercado Eletrônico**.

---

## Como Rodar

1. Crie o arquivo `.env` a partir do template e preencha sua `OPENROUTER_API_KEY`:
   ```bash
   cp .env.example .env
   ```
**OBS**: a chave que recebi no PDF do case não funcionou (erro de limite atingido), criei uma própria e usei um modelo gratuito da OpenRouter (NVIDIA: Nemotron 3 Nano Omni)


2. Suba os quatro serviços (`postgres`, `mcp_server`, `backend`, `frontend`):
   ```bash
   docker compose up --build
   # ou: make up
   ```

3. Acesse:
   - **Chat B2B (Frontend React):** [http://localhost:5173](http://localhost:5173)
   - **API FastAPI (Docs / Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

### Rodando os Testes do Servidor MCP (sem chave de LLM)
```bash
docker compose exec mcp_server pytest
# ou: make test
```

---

## Arquitetura e Principais Decisões

- **4 Serviços Desacoplados (`docker-compose.yaml`):**
  - **`mcp_server`:** Servidor isolado com `FastMCP` (transporte SSE) expondo `buscar_produtos(termo)` e `detalhar_produto(id)` integrados à API DummyJSON com timeout e tratamento de erros HTTP.
  - **`backend`:** FastAPI + SQLAlchemy (`POST /requisicoes` e `GET /requisicoes`), com criação automática das tabelas no startup (`lifespan`) e gerenciador de pacotes `uv`.
  - **`postgres`:** PostgreSQL 16 persistindo `requisicoes` e `itens_requisicao` em relacionamento `1:N`.
  - **`frontend`:** Interface em React + Vite seguindo a identidade visual institucional do Mercado Eletrônico
- **Tool Calling Dinâmico + Persistência Determinística:**
  - O agente utiliza `langchain[mcp]` (`MCPAdapter` + `create_agent` via OpenRouter) para descobrir as ferramentas do servidor MCP e decidir autonomamente quando buscar ou detalhar produtos, sem fluxo fixo no código.
  - O uso de `response_format` (`DecisaoAgente`) separa o raciocínio não-determinístico do LLM da gravação determinística no PostgreSQL (realizada na rota FastAPI apenas quando há itens aprovados).
- **Falhas e Guardrails:**
  - Falhas ou timeouts na DummyJSON são capturados no servidor MCP e tratados pelo agente com mensagens claras, sem inventar produtos ou quebrar a aplicação.
  - Respostas fora do escopo do agente são respondidas de forma educada.

---

## Uso de IA no Desenvolvimento

Utilizei assistente de IA como **motor principal de escrita de código e debugging**:
- **Geração de código:** Escrita dos endpoints FastAPI, integração do `langchain[mcp]` (`MCPAdapter` e `create_agent`), construção da interface React/CSS e configuração do Docker Compose.
- **Debugging e Refinamento:** Investigação de comportamentos da API DummyJSON (como a busca exigir termos em inglês no singular), ajustes de hot reload/cache do MCP e limpeza de redundâncias/overengineering.
- **Meu papel:** Direcionamento das escolhas técnicas e de arquitetura, checagem de documentação das tecnologias utilizadas, escrita parcial do MCP Server, revisão do código gerado, definição das regras de negócio/prompt e testes manuais de ponta a ponta.

