# Simulação de Discovery: Grupo 3 Corações

---

##  Por que fiz este documento?

Como **AI Forward Deployed Engineer**, meu papel vai muito além de codificar: eu preciso entender o problema na operação do cliente, por isso, simulo como seria minha atuação nesse processo.

---

## O Cliente & O Cenário Simulado

- **Empresa:** Grupo 3 Corações (grande operação B2B com filiais e força comercial distribuída).
- **Interlocutora:** Mariana Souza — Coordenadora de Operações Comerciais.
- **Demanda:** Contratação de 3 novos executivos de vendas com prazo de 14 dias para estarem equipados.

---

## Como eu conduziria a Entrevista de Discovery com a Mariana

### 1. Entendendo o Perfil e Frequência das Compras
> **Eu (AI FDE):**  
> *"Mariana, que tipos de compras a sua área faz habitualmente pela plataforma? É algo pontual ou compras em lotes recorrentes?"*  
>  
> **Mariana:**  
> *"Compramos muito material de suporte e equipamentos para equipe de campo (smartphones, tablets e notebooks). No caso de TI, compramos lotes de 2 a 10 unidades sempre que entram novas contratações ou ciclos de renovação."*

### 2. Condições Comerciais e Faturamento
> **Eu:**  
> *"Como funciona a liquidação dessas compras? Vocês pagam com cartão corporativo, à vista ou faturado a prazo?"*  
>  
> **Mariana:**  
> *"Aqui é 100% faturamento corporativo a prazo (geralmente boleto a 30 dias contra o CNPJ da filial), após aprovação do centro de custo. O agente precisa gerar a requisição estruturada, não um checkout de e-commerce comum."*

### 3. Histórico, Políticas e Planilha de Referência
> **Eu:**  
> *"Você teria uma planilha, histórico de compras anteriores ou a política de TI interna para eu analisar o padrão do que vocês aprovam?"*  
>  
> **Mariana:**  
> *"Tenho a diretriz da TI: máquinas rápidas para CRM/apresentações, boa bateria e leves para viagem. O principal limitador da política é o teto orçamentário: máximo US$ 2.000 por unidade. Se passar de US$ 2.000, o sistema barra e a requisição é reprovada."*

### 4. SLA e Criticidade da Entrega
> **Eu:**  
> *"Qual é a urgência dessa entrega? Quão crítico é esse equipamento para a rotina deles?"*  
>  
> **Mariana:**  
> *"É crítico. Os executivos começam em duas semanas. Sem laptop, eles não conseguem acessar o ERP, fazer treinamentos ou atender clientes. O prazo máximo para o produto chegar na filial é de 10 a 14 dias."*

---

## Como eu traduzo essas respostas em Requisitos Técnicos para o Agente

Tudo o que for apresentado no frontend precisa estar estruturado e persistido no backend e no banco de dados.

### Frontend
- **Categorias de equipamentos:** Exibição clara do tipo/categoria do produto.
- **Quantidade de chamadas de tools:** Contador visível de quantas ferramentas o agente acionou.
- **Informações essenciais do produto:** Ficha técnica com bateria (mAh), peso, perfil de uso indicado e valor.
- **Aviso de limite orçamentário:** Alerta explícito caso o preço passe de um valor limite (teto de US$ 2.000).
- **Logística e entrega:** Informações de frete, prazo estimado e data de entrega.

### Banco de Dados:

1. **Dados do Produto / Item:**
   - Nome e descrição do produto
   - Categoria do equipamento
   - Características técnicas: capacidade de bateria (mAh), peso e indicação de uso
   - Preço unitário e moeda
   - Fornecedor / Dono atual do produto (empresa vendedora B2B no marketplace)

2. **Dados da Requisição de Compra:**
   - Número da requisição
   - Solicitante / Quem está comprando (nome da pessoa, cargo e filial/centro de custo)
   - Itens comprados e suas respectivas quantidades
   - Informações de frete e logística: valor do frete, prazo, local de origem (onde o produto está hoje) e local de destino (para onde vai / filial recebedora)
   - Valor total consolidado


## Outros requisitos

Os requisitos essenciais e opcionais do case estão descritos no PDF, os que coloquei acima são simulando uma etapa de arquitetura pós-discovery com o cliente.