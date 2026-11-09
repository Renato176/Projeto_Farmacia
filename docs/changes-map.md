# Mapa de Changes, telas e funções

Este documento organiza o que foi construído por **Change** (mudança OpenSpec).
Ele é um índice de navegação: os contratos detalhados continuam nos arquivos da
pasta [`openspec/`](../openspec), as regras de domínio em
[`domain-model.md`](./domain-model.md) e a implementação Reflex em
[`farmaciaFinal/`](../farmaciaFinal).

## Como ler este mapa

- **Change** descreve uma entrega funcional e seu limite de responsabilidade.
- **Tela** identifica uma rota Reflex visível ao usuário.
- **Estado** identifica a classe que mantém dados e eventos da tela.
- **Cliente/API** identifica as funções de integração com o Xano.
- **Placeholder** é uma rota protegida existente, mas ainda sem funcionalidade
  operacional completa.
- Quando uma função aparece em mais de uma Change, ela é uma integração
  compartilhada; a responsabilidade principal está indicada na primeira
  ocorrência.

## Visão geral das Changes

| Change | Status | Entrega principal | Referência |
|---|---|---|---|
| Backend e APIs da farmácia | Em manutenção | Tabelas, contratos REST, pedidos, estoque e relatórios no backend | [`backend-e-apis-da-farmacia/`](../openspec/changes/backend-e-apis-da-farmacia/) |
| Catálogo e gestão de estoque | Concluída | Categorias, produtos, consulta de estoque e operações de catálogo | [`proposal.md`](../openspec/changes/catalogo-e-gestao-de-estoque/proposal.md) |
| Autenticação de funcionários | Concluída | Login, sessão, proteção de rotas e cadastro autenticado | [`proposal.md`](../openspec/changes/autenticacao-de-funcionarios/proposal.md) |
| Cadastro público de funcionários | Concluída | Cadastro sem sessão e ativação imediata | [`proposal.md`](../openspec/changes/cadastro-publico-de-funcionarios/proposal.md) |
| Cargos no cadastro de funcionários | Concluída | Lista dinâmica de cargos ativos no cadastro | [`proposal.md`](../openspec/changes/cargos-no-cadastro-de-funcionarios/proposal.md) |
| Tela de categorias | Implementada; integração pendente | Catálogo local protegido com busca hierárquica, sem CRUD ou vínculo persistente no Xano | [`proposal.md`](../openspec/changes/droga-nonimo-categories-screen/proposal.md) |
| Reorganização do catálogo de categorias | Implementada; integração pendente | Taxonomia em departamentos e subcategorias com busca local; também usada como atalho em Estoque e Vendas | [`proposal.md`](../openspec/changes/droga-nonimo-category-catalog-redesign/proposal.md) |
| Atalhos de busca por categoria | Implementada | Departamentos e subcategorias preenchem a busca textual em Estoque e Vendas | [`proposal.md`](../openspec/changes/droga-nonimo-category-search-shortcuts/proposal.md) |
| Dashboard operacional | Em aberto | Dashboard protegido, navegação e resumo operacional | [`proposal.md`](../openspec/changes/dashboard-operacional/proposal.md) |

## Backend e APIs da farmácia

**Responsabilidade:** contrato e integridade do backend. Esta Change não possui
uma tela Reflex própria.

### Funções do domínio

- Autenticação de funcionário.
- Cadastro e busca de clientes por CPF.
- Categorias e produtos.
- Abertura, alteração, remoção e fechamento de pedidos.
- Desconto de 15% quando há cliente e subtotal superior a R$ 100,00.
- Baixa atômica de estoque e relatórios diário, semanal e mensal.

### Implementação

- Tabelas namespaced: `farmacia_final_funcionario`,
  `farmacia_final_cliente`, `farmacia_final_categorias`,
  `farmacia_final_produtos`, `farmacia_final_pedido` e
  `farmacia_final_item_pedido`.
- Scripts de tabelas em [`xano/table/`](../xano/table).
- Scripts de API em [`xano/api/farmacia/farmacia_final/`](../xano/api/farmacia/farmacia_final).
- Referência técnica em [`reference.md`](../openspec/changes/backend-e-apis-da-farmacia/reference.md).

## Catálogo e gestão de estoque

**Responsabilidade:** tela operacional de estoque e integração de categorias e
produtos.

### Tela

| Rota | Tela | Situação |
|---|---|---|
| `/estoque` | Gestão de Estoque | Implementada e protegida |

### Estado e funções Reflex

Arquivo [`stock_state.py`](../farmaciaFinal/stock_state.py), classe
`StockState`:

- `load_inventory`: carrega categorias e produtos.
- `filtered_medicines`: aplica busca, status e categoria.
- `total_items`, `low_stock_count`, `total_stock_value`: calcula os cards.
- `open_create`, `open_edit`, `close_form`: controla o formulário.
- `save_product`: cria ou edita produto.
- `request_delete`, `close_delete`, `delete_product`: desativa produto.
- `set_search_term`, `set_status_filter`, `set_category_filter`: controla filtros.
- `set_form_nome`, `set_form_descricao`, `set_form_preco`,
  `set_form_estoque`, `set_form_categoria`: controla campos.

### Cliente Xano

Arquivo [`xano_client.py`](../farmaciaFinal/xano_client.py):

- `get_categories` e `get_products`.
- `create_product` e `update_product`.
- Conversão e validação por `Category` e `Product`.

## Autenticação de funcionários

**Responsabilidade:** sessão, login, proteção das rotas e provisionamento
autenticado.

### Telas

| Rota | Tela | Situação |
|---|---|---|
| `/login` | Acesso do funcionário | Implementada |
| `/cadastro` | Cadastro de funcionário | Posteriormente ampliada pela Change de cadastro público |

### Estado e funções Reflex

Arquivo [`auth_state.py`](../farmaciaFinal/auth_state.py), classe
`AuthState`:

- `login`: valida credenciais e inicia a sessão.
- `require_auth`: protege páginas operacionais.
- `redirect_authenticated`: evita que uma sessão válida volte ao login.
- `logout`: encerra a sessão.
- `is_authenticated`: expõe o estado calculado da sessão.
- `_session_is_valid` e `_clear_session`: controle interno de validade e limpeza.
- `login_error_message` e `registration_error_message`: mensagens de domínio.

### Cliente Xano

- `login`.
- `register_employee` para o fluxo autenticado original.
- `Employee` e `LoginResult`.

## Cadastro público de funcionários

**Responsabilidade:** permitir criação de conta sem sessão, com conta ativa
definida pelo backend e sem expor credenciais.

### Tela

| Rota | Tela | Situação |
|---|---|---|
| `/cadastro` | Criar conta de funcionário | Pública e implementada |

### Estado e funções

No arquivo [`auth_state.py`](../farmaciaFinal/auth_state.py):

- `register_employee`: valida nome, e-mail, senha e cargo, chama o endpoint
  público e preserva os campos não sensíveis em caso de falha.
- `set_registration_nome`, `set_registration_email` e
  `set_registration_cargo`: atualizam o formulário.
- `registration_submit_disabled`: impede envio durante carregamento ou sem
  cargo válido.

Na tela [`farmaciaFinal.py`](../farmaciaFinal/farmaciaFinal.py):

- `register_page`: formulário público, feedback e navegação de retorno.

No cliente [`xano_client.py`](../farmaciaFinal/xano_client.py):

- `register_employee` sem credencial.

## Cargos no cadastro de funcionários

**Responsabilidade:** restringir o cargo a opções ativas fornecidas pelo Xano.
Esta é uma extensão do cadastro público, não uma tela independente.

### Estado e funções

- `load_cargos`: carrega cargos quando `/cadastro` é aberta.
- `set_registration_cargo`: aceita somente uma opção carregada.
- `registration_cargo_select_disabled`: bloqueia o Select durante carregamento
  ou quando não há opções.

### Cliente Xano e backend

- `get_cargos` valida a resposta `{ "cargos": [...] }`.
- Tabela [`farmacia_final_cargo.xs`](../xano/table/farmacia_final_cargo.xs).
- Endpoint público de cargos em
  [`xano/api/farmacia/farmacia_final/`](../xano/api/farmacia/farmacia_final).
- A validação do cargo no cadastro permanece no backend.

## Dashboard operacional

**Responsabilidade:** ponto de entrada operacional após o login.

### Telas e rotas

| Rota | Tela | Situação |
|---|---|---|
| `/` | Visão Geral | Dashboard protegido |
| `/dashboard` | Visão Geral | Dashboard protegido |
| `/estoque` | Gestão de Estoque | Tela real da Change de catálogo; inclui atalhos locais de busca |
| `/vendas` | Vendas | Tela operacional com catálogo e atalhos locais de busca |
| `/categorias` | Categorias | Catálogo hierárquico local, protegido; sem integração de persistência no Xano |
| `/funcionarios` | Funcionários | Placeholder protegido |
| `/configuracoes` | Configurações | Placeholder protegido |

### Componentes de tela

Arquivo [`farmaciaFinal.py`](../farmaciaFinal/farmaciaFinal.py):

- `_brand_header`, `_language_selector` e `_feedback`: elementos
  compartilhados pelas telas de autenticação.
- `_dashboard_sidebar` e `_sidebar_link`: navegação operacional e logout.
- `_dashboard_content`, `_metric_card`, `_category_bars` e `_quick_actions`:
  composição do dashboard.
- `index`: página protegida do dashboard.
- `module_placeholder`: tela comum dos módulos ainda não implementados.
- `stock_page`, `_stock_summary_card` e `_stock_row`: composição da tela de
  estoque, usando `StockState`.
- `login_page` e `register_page`: telas de autenticação/cadastro.

Arquivo [`dashboard_state.py`](../farmaciaFinal/dashboard_state.py), classe
`DashboardState`:

- Indicadores `vendas_hoje`, `vendas_semana`, `vendas_mes` e
  `itens_estoque`.
- Contextos auxiliares dos indicadores.
- `load_dashboard`: ponto de extensão para integração dos indicadores com o
  Xano.

### Limite atual do dashboard

Os cards e barras exibidos no dashboard ainda são dados estáticos de
apresentação; `load_dashboard` não consulta o Xano. As rotas de Funcionários
e Configurações são placeholders protegidos. Estoque e Vendas oferecem
atalhos de busca textual por departamentos e subcategorias.

## Registro de rotas atual

As rotas são registradas no final de
[`farmaciaFinal.py`](../farmaciaFinal/farmaciaFinal.py):

| Rota | Função | Guarda/carregamento |
|---|---|---|
| `/` | `index` | `AuthState.require_auth` |
| `/login` | `login_page` | `AuthState.redirect_authenticated` |
| `/cadastro` | `register_page` | `AuthState.load_cargos` |
| `/dashboard` | `index` | `AuthState.require_auth` |
| `/estoque` | `stock_page` | `LoginState.require_login`, `LoginState.load_stock` |
| `/vendas` | `sales_page` | `LoginState.require_login`, `LoginState.load_sales` |
| `/categorias` | `categories_page` | `LoginState.require_login`, `CategoryState.clear_search` |
| `/funcionarios` | `module_placeholder("Funcionários")` | `AuthState.require_auth` |
| `/configuracoes` | `module_placeholder("Configurações")` | `AuthState.require_auth` |

## Estrutura das Changes

Todas as Changes ficam diretamente dentro de
[`openspec/changes/`](../openspec/changes/), cada uma em uma pasta independente,
mesmo quando já estiver concluída. A pasta `archive/` não é usada nesta
organização para evitar misturar Changes com documentos soltos ou estruturas
diferentes.

## Regra para próximas Changes

Toda nova tela ou função deve:

1. ter uma pasta própria em `openspec/changes/<nome-da-change>/`;
2. declarar telas, estados, cliente/API e limites no `proposal.md`;
3. registrar cenários verificáveis em `specs/`;
4. atualizar este mapa somente depois da implementação;
5. indicar explicitamente se a rota é real, placeholder ou apenas backend.
