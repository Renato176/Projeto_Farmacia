# Documento de Visão Geral do Projeto (Project Overview)
**Projeto:** Sistema de Gestão de Farmácia (`farmaciaFinal`)  
**Metodologia:** Context-First com OpenSpec  

---

## 1. Contexto e Justificativa
As farmácias físicas de pequeno e médio porte enfrentam desafios no controlo simultâneo de inventário, dinamismo de preços por categoria e retenção de clientes. Este sistema surge para centralizar a operação no ponto de venda (PDV), permitindo que o funcionário realize o atendimento guiado (adicionando itens ao pedido do cliente em tempo real), aplique regras automáticas de fidelização e acompanhe o desempenho financeiro do estabelecimento.

---

## 2. Escopo do Sistema

### 2.1. Dentro do Escopo (In-Scope)
- **Módulo de Autenticação de Funcionários:** Gestão de credenciais com e-mail e palavra-passe.
- **Módulo de Clientes:** Registo e identificação de clientes via CPF no momento da venda.
- **Módulo de Catálogo e Estoque:** CRUD de produtos e atalhos locais de busca por departamentos e subcategorias.
- **Módulo de Vendas (PDV Guiado):** Interface operacional onde o funcionário cria pedidos, adiciona/remove itens e visualiza o cálculo do total.
- **Motor de Regras de Negócio (Descontos):** Cálculo e aplicação automática de 15% de desconto para compras acima de R$ 100,00 associadas a clientes identificados.
- **Módulo de Métricas e Relatórios:** Agregação de faturamento diário, semanal e mensal.

### 2.2. Fora do Escopo (Out-of-Scope)
- Processamento real de pagamentos via Gateways/Adquirentes (Pix, Cartão de Crédito/Débito) no Backend (será apenas simulado visualmente no Front-End).
- Aplicação móvel nativa para o cliente final realizar compras diretas (autoatendimento/e-commerce).
- Integração com sistemas de prescrição médica digital ou órgãos governamentais (SNGPC/Anvisa).

---

## 3. Requisitos Funcionais (RF)

| ID | Nome do Requisito | Descrição Detalhada |
| :--- | :--- | :--- |
| **RF01** | Autenticação de Funcionário | O sistema deve permitir o login de funcionários via e-mail e palavra-passe codificada. |
| **RF02** | Cadastro de Funcionário | O sistema deve permitir o registo de novos funcionários no sistema. |
| **RF03** | Identificação/Cadastro de Cliente | O sistema deve permitir pesquisar clientes por CPF e registar novos clientes com Nome e CPF. |
| **RF04** | Atendimento Sem Identificação | O sistema deve permitir a abertura e finalização de pedidos sem a associação de um CPF. |
| **RF05** | Gestão de Produtos e Estoque | O sistema deve permitir que o funcionário cadastre, edite preço, atualize a quantidade em estoque e altere a categoria de um produto. |
| **RF06** | Montagem de Pedido | O sistema deve permitir ao funcionário adicionar produtos ao carrinho, definir quantidades e remover itens antes do encerramento. |
| **RF07** | Aplicação Automática de Desconto | O sistema deve verificar o valor subtotal e a presença de cliente identificado, aplicando 15% de desconto se $\text{subtotal} > 100{,}00$ e `cliente_id` for válido. |
| **RF08** | Baixa Automática de Estoque | Ao concluir uma venda, o sistema deve deduzir as quantidades vendidas do estoque correspondente no banco de dados. |
| **RF09** | Relatório de Vendas | O sistema deve fornecer um painel com o somatório de vendas concluídas no Dia, na Semana e no Mês corrente. |

---

## 4. Requisitos Não Funcionais (RNF)

- **RNF01 (Segurança):** As palavras-passe dos funcionários devem ser armazenadas utilizando algoritmos de hashing seguros no backend (Xano).
- **RNF02 (Integridade de Dados):** O sistema não deve permitir a finalização de vendas de produtos cuja quantidade solicitada seja superior ao estoque disponível.
- **RNF03 (Desempenho):** As consultas de métricas e busca por CPF devem responder em menos de 1 segundo.
- **RNF04 (Usabilidade):** A interface de montagem de pedidos deve ser otimizada para o funcionário realizar a venda de forma ágil, em fluxo contínuo.

---

## 5. Arquitetura da Solução
- **Front-End:** Aplicação Web (Simulação do Checkout e Pagamento).
- **Back-End (API/Database):** Xano (Bases de dados relacionais e endpoints via XanoScript).
- **Assistência de IA & Especificação:** OpenSpec + Xano Developer MCP.

## 6. Painel de Métricas / Dashboard:**
   - Visualização do total faturado no dia, na semana e no mês.
   - O dashboard principal protegido apresenta sidebar operacional, identificação do funcionário, métricas resumidas, vendas por categoria e ações rápidas.

## 7. Frontend: Reflex   
    - Reflex será utilizado como tecnologia exclusiva para implementação do frontend da aplicação.
    - O frontend chama o Xano pelo servidor Reflex. `XANO_API_BASE_URL` aceita a URL da instância ou do grupo Farmácia; o cliente usa o grupo `/api:hVU-wK41` do workspace `149200` por padrão e acrescenta as rotas `/farmacia-final/*`. Após o login, o `authToken` é armazenado em um `rx.Cookie` com validade de 24 horas; a expiração do cookie e a validação do Xano encerram sessões inválidas.
    - O autocadastro público de funcionários cria contas ativas imediatamente (`ativo=true` definido no backend), sem verificação de e-mail ou aprovação. Esse risco de criação aberta de contas ativas deve ser considerado antes da disponibilização pública.
    - As páginas protegidas de Gestão de Estoque e Vendas oferecem atalhos de departamentos e subcategorias que preenchem a busca por nome ou código de barras. O catálogo do Xano ainda não confirma vínculo persistente entre produtos e categorias; por isso, os atalhos são termos de busca local, não uma classificação dos produtos.

## 8. Organização por Change

O inventário de telas, estados, funções Reflex, integrações Xano, rotas
placeholder e limites de cada entrega está em
[`docs/changes-map.md`](./changes-map.md). Use esse mapa para localizar a
responsabilidade de cada funcionalidade sem misturar backend, autenticação,
catálogo e dashboard.
 