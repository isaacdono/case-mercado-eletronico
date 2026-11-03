# Melhorias Futuras

Possíveis evoluções para o projeto:

1. **Modelagem de Dados Expandida:** Ampliar as tabelas do banco para incluir dados de usuários/solicitantes e mais informações técnicas dos produtos, conectando com o levantamento feito em [`CONTEXTO_CLIENTE.md`](./CONTEXTO_CLIENTE.md).
2. **Guardrails Avançados:** Uso de um framework dedicado como o **Guardrails AI** para validar entradas e saídas de forma mais robusta, em vez de depender apenas do prompt.
3. **Observabilidade com Langfuse:** Integração com o **Langfuse** para monitorar as chamadas ao LLM, uso das tools do MCP, latência e consumo de tokens.
4. **Adminer:** Inclusão de um container com **Adminer** no Docker Compose para inspecionar e gerenciar as tabelas do PostgreSQL visualmente pelo navegador.
5. **Confirmação em Duas Etapas (Human-in-the-Loop):** Antes de gravar a requisição no banco, apresentar a cotação escolhida e exigir confirmação explícita do usuário para efetivar o pedido.

E há os itens opcionais do enunciado:
6. **Exibição das Ferramentas no Chat:** Mostrar visualmente na interface do chat quais tools do MCP (`buscar_produtos`, `detalhar_produto`) o agente acionou em cada etapa do raciocínio.
7. **Terceira Ferramenta MCP (`criar_requisicao`):** Salvar a requisição diretamente por uma terceira tool no MCP, deixando o próprio agente decidir quando persistir o pedido.
8. **CI/CD com Lint e Testes em Containers de Produção:** Configurar pipeline de CI/CD com lint (`ruff`), execução dos testes automatizados e arquivos `Dockerfile` / `docker-compose.prod.yml` voltados para produção.
