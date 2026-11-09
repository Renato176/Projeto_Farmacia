# Especificação do Projeto: Sistema de Farmácia (Impacta 2026)
**Desenvolvimento Assistido por Inteligência Artificial e Arquitetura No-Code/Low-Code**

## 1. Arquitetura do Ambiente e Ferramentas
O ambiente de desenvolvimento foi estruturado com foco em sincronização local, documentação automatizada e suporte a agentes de IA:
- **Frontend:** Reflex (Framework em Python para interfaces reativas)
- **Backend:** Xano (Plataforma Backend-as-a-Service / Low-Code em nuvem)
- **Documentação e Governança:** OpenSpec
- **Ferramentas de Desenvolvimento e Sincronização:**
  - Node.js / Xano CLI (`@xano/cli`)
  - XanoScript Language Server
  - Xano Developer MCP (`@xano/mcp`) para integração de agentes de IA

---

## 2. Modelagem do Banco de Dados (Xano)
O banco de dados do sistema é composto por 5 tabelas principais:

1. **`cliente`**
   - *Descrição:* Armazena registros de clientes do sistema farmacêutico.
   - *Campos:* `id` (Integer), `nome` (Text), `cpf` (Text), `telefone` (Text), `está_registrado` (Boolean), `criado_em` (Timestamp), `atualizado_em` (Timestamp).

2. **`produto`**
   - *Descrição:* Armazena inventário de produtos e detalhes de preços.
   - *Campos:* `id` (Integer), `nome` (Text), `código de barras` (Text), `preço` (Numeric), `estoque_quantidade` (Integer), `criado_em` (Timestamp), `atualizado_em` (Timestamp).

3. **`venda`**
   - *Descrição:* Armazena transações de vendas processadas por funcionários.
   - *Campos:* `id` (Integer), `ID_usuário` (Reference -> `usuário`), `cliente_id` (Reference -> `cliente`), `valor_total` (Numeric), `desconto_aplicado` (Boolean), `criado_em` (Timestamp), `atualizado_em` (Timestamp).

4. **`usuário`**
   - *Descrição:* Armazena informações do usuário e permissões de autenticação.
   - *Campos:* `id` (Integer), `nome` (Text), `e-mail` (Text), `senha` (Password), `papel` (Integer), `senha_reset` (JSON), `criado_em` (Timestamp), `atualizado_em` (Timestamp).

5. **`registro_de_evento`**
   - *Descrição:* Armazena logs de atividades e eventos do sistema.
   - *Campos:* `id` (Integer), `ID_usuário` (Reference -> `usuário`), `ação` (Text), `metadados` (JSON), `criado_em` (Timestamp).

---

## 3. Endpoints de API (Autenticação)
- **`POST /autenticacao/acesso`** — Autenticação de usuários existentes por e-mail e senha, retornando token de acesso.
- **`POST /autenticacao/login`** — Realiza login e recupera token de autenticação.
- **`POST /authpassword-reset`** — Processo de redefinição de senha.
- **`POST /esquici-senha`** — Fluxo dedicado para recuperação de senha.