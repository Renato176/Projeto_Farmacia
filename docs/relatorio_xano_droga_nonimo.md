# Relatorio de alteracoes no Xano — DROGA-NONIMO

**Data inicial:** 19/10/2026

**Atualizacao:** 08/11/2026
**Workspace:** Renato's Workspace, workspace `169234-0`  
**Branch e fonte de dados exibidos:** `v1` / `live`

## Objetivo

Preparar no Xano a estrutura inicial do banco para o sistema de farmacia DROGA-NONIMO, com dados ficticios para visualizar e testar o catalogo de produtos.

## Tabelas criadas

| Tabela | ID no Xano | Finalidade | Campos principais |
|---|---:|---|---|
| `cliente` | `908187` | Cadastro de clientes | `nome`, `cpf`, `telefone`, `esta_registrado`, `criado_em`, `atualizado_em` |
| `produto` | `908189` | Catalogo e estoque | `nome`, `codigo_barras`, `preco`, `estoque_quantidade`, `imagem_url`, `categoria_id` (referencia opcional), `criado_em`, `atualizado_em` |
| `venda` | `908190` | Vendas processadas por usuarios | `usuario_id`, `cliente_id`, `valor_total`, `desconto_aplicado`, `criado_em`, `atualizado_em` |
| `item_venda` | `908192` | Produtos e quantidades de cada venda | `venda_id`, `produto_id`, `quantidade`, `preco_unitario`, `criado_em` |
| `categoria` | `913434` | Catalogo hierarquico | `nome`, `descricao`, `categoria_pai_id`, `ativo`, `cor` |

Todas as tabelas possuem um campo `id` inteiro gerado pelo Xano.

## Tabelas padrao preservadas

- `user` (`898415`): mantida sem alteracoes. Ja existiam tres contas antes do trabalho; nenhuma conta adicional foi criada.
- `event_log` (`898416`): mantida sem alteracoes. Seus campos existentes (`user_id`, `action`, `metadata`, `created_at`) cobrem a finalidade de registro de eventos descrita na especificacao, portanto nao foi criada uma tabela duplicada `registro_de_evento`.

## Dados de teste

Foram gerados **3 registros ficticios** em `produto` pelo gerador de testes do Xano. Os nomes sao aleatorios e servem somente para teste visual; podem ser substituidos por produtos definidos pelo projeto. Nenhum cliente ou dado pessoal foi criado.

## Catalogo persistido de categorias

Em 08/11/2026, no workspace `169234-0`, branch `v1` e fonte `live`, foi criada
a tabela `categoria` (`913434`) e importados 58 registros: 9 departamentos e
49 subcategorias. `categoria_pai_id` referencia opcionalmente outro registro
da tabela. O campo opcional `produto.categoria_id` referencia `categoria`.

Os cinco endpoints abaixo pertencem ao grupo `Farmacia` (`437376`), exigem
autenticacao de usuario e estao publicados:

| Metodo e rota | ID no Xano | Uso |
|---|---:|---|
| `GET /categoria` | `4119595` | Listar categorias |
| `POST /categoria` | `4119596` | Criar categoria |
| `GET /categoria/{categoria_id}` | `4119594` | Consultar categoria |
| `PATCH /categoria/{categoria_id}` | `4119597` | Atualizar categoria |
| `DELETE /categoria/{categoria_id}` | `4119593` | Excluir categoria |

O mapeamento de `POST /categoria` foi corrigido para persistir `nome`,
`descricao`, `categoria_pai_id`, `ativo` e `cor`; `ativo` esta ligado como
booleano, nao como texto. O endpoint `POST /produto` (`4103434`) foi corrigido
e publicado para gravar `imagem_url` e `categoria_id` junto aos demais campos.
O endpoint `PATCH /produto/{produto_id}` (`4103437`), usado para edicao pelo
frontend, ja aceita `categoria_id`.

A tela `/categorias` e o formulário e filtros de Estoque/Vendas carregam
categorias pelo `GET /categoria`. O formulario de produto envia a referencia
selecionada na criacao e edicao; o filtro por departamento tambem considera
subcategorias. A interface de `/categorias` oferece criacao e edicao de
departamentos e subcategorias, ativacao/desativacao, alem de exclusao com
confirmacao. Erros de validacao e do Xano sao apresentados sem remover o
registro da lista em caso de falha.

Os mapeamentos finais foram revisados no diff de publicacao antes de publicar
cada endpoint separadamente. Nao foi executada uma gravacao de teste em `live`,
e nenhum registro temporario de categoria ou produto foi criado. Os drafts
preexistentes `POST /cliente` (`4105447`) e `PUT /produto/{produto_id}`
(`4103438`) foram deixados intactos; o frontend usa `PATCH` para editar
produtos.

## APIs de autenticacao verificadas e integradas

O grupo `Authentication` (`api:t7Ptjfi3`) ja possuia os endpoints abaixo; nenhum novo endpoint foi criado:

| Metodo e rota | Uso | Contrato confirmado |
|---|---|---|
| `POST /auth/login` | Login | Recebe `email` e `password`; retorna `authToken` e `user_id`. |
| `POST /auth/signup` | Cadastro | Recebe `name`, `email` e `password`; retorna `authToken` e `user_id`. |
| `GET /reset/request-reset-link` | Solicitar recuperacao | Recebe `email` por query string e envia um magic link de uso unico. |
| `POST /reset/magic-link-login` | Validar magic link | Recebe `magic_token` e `email`; troca o token temporario por `authToken`. |
| `POST /reset/update_password` | Redefinir senha | Endpoint privado; exige Bearer token e recebe `password` e `confirm_password`. |

O endpoint `reset/request-reset-link` foi alterado e publicado para que o magic link aponte para `http://localhost:3000/redefinir-senha?magic_token=...&email=...`, em vez da pagina demo padrao do Xano. A rota Reflex troca o magic token por um token de autenticacao e usa esse token apenas no pedido autenticado de redefinicao. A interface de recuperacao agora apresenta uma resposta neutra sem revelar se o e-mail foi localizado. Nenhum cadastro, login ou redefinicao foi executado; o endpoint foi testado com um endereco `.invalid` e nao enviou e-mail.

**Escopo atual:** o frontend sera usado localmente e nao precisa de URL publica. Portanto, `localhost:3000` e o destino intencional do magic link neste ambiente. Se a aplicacao for publicada futuramente, sera necessario configurar uma origem acessivel externamente no endpoint Xano antes de habilitar recuperacao nesse ambiente.

**Privacidade do endpoint publico:** em 08/11/2026, `GET /reset/request-reset-link` foi atualizado e publicado para retornar a mesma mensagem generica quando a geracao do link ou o envio do e-mail falha. O endpoint publicado foi executado com um endereco reservado `.invalid`; a resposta foi bem-sucedida e generica, sem envio de e-mail. O teste com conta real e caixa postal acessivel continua pendente.

**Escopo fora desta etapa:** publicacao do frontend, configuracao de URL publica e teste ponta a ponta com conta/caixa postal reais. A recuperacao local continua usando `http://localhost:3000`.

## Referencias entre tabelas

Em 08/11/2026, no workspace `169234-0`, branch `v1` e fonte `live`, os
seguintes campos foram configurados como **Table Reference** e conferidos
individualmente no schema do Xano:

- `venda.usuario_id` → `user` (`898415`)
- `venda.cliente_id` → `cliente` (`908187`)
- `item_venda.venda_id` → `venda` (`908190`)
- `item_venda.produto_id` → `produto` (`908189`)

Os índices ascendentes (`index`) de cada um desses campos também foram
restaurados e verificados em **Manage Indexes**. As tabelas `venda` e
`item_venda` continuam sem registros; nenhum dado de venda ou item foi criado
ou alterado durante a configuração. As referências garantem o vínculo no
schema, mas não implementam por si só uma operação transacional de checkout
nem a baixa de estoque.

## Escopo nao incluido

- Na etapa inicial de modelagem, nenhum endpoint novo foi criado; somente o destino do magic link em `reset/request-reset-link` foi alterado.
- Nenhuma tabela ou registro de dados da farmacia foi alterado durante aquela etapa inicial.
- Nenhuma tabela ou conta preexistente foi apagada.
- O Xano e a fonte de dados remota; qualquer arquivo SQLite local anterior nao faz parte desta estrutura nem sincroniza com a workspace.

## APIs de estoque e vendas preparadas

Foi criado o grupo privado `Farmacia` (`api:M6el3Cg8`) para as operacoes de estoque e vendas. As rotas abaixo usam autenticacao do usuario:

| Metodo e rota | Uso |
|---|---|
| `GET /produto` | Listar produtos |
| `POST /produto` | Criar produto (publicado, `4103434`) |
| `GET /produto/{produto_id}` | Consultar produto |
| `PATCH /produto/{produto_id}` | Atualizar produto usado pelo frontend (`4103437`) |
| `PUT /produto/{produto_id}` | Endpoint legado em draft (`4103438`), nao usado pelo frontend |
| `DELETE /produto/{id}` | Excluir produto |
| `GET /cliente` | Listar clientes |
| `POST /cliente` | Cadastro de cliente (`4105447`, draft nao publicado) |
| `GET /venda` | Consultar historico de vendas |
| `POST /venda` | Criar venda |
| `POST /venda/finalizar` | Endpoint autenticado `4119638`, draft vazio e nao publicado |
| `POST /item_venda` | Criar item de venda |

Foi adicionado a `venda` o campo enum `forma_pagamento`, com os valores `dinheiro`, `pix`, `credito` e `debito`.

O frontend usa `GET /produto`, `GET /cliente` e `GET /venda` para carregar estoque e o catalogo/historico da tela de vendas. A tela de estoque envia `POST /produto` para criar e `PATCH /produto/{produto_id}` para editar; a rota `DELETE` existe no Xano, mas nao e oferecida na interface. O frontend envia `POST /venda/finalizar` com IDs e quantidades dos produtos, cliente opcional e forma de pagamento; nao envia precos nem totais como fonte confiavel. So limpa o carrinho quando recebe `success: true` e um `venda.id` inteiro valido, e atualiza catalogo e historico apos essa confirmacao. O endpoint `4119638`, entretanto, segue sem inputs, funcoes ou resposta configurados e nao foi publicado. Portanto, o checkout nao pode concluir vendas no ambiente live; transacao, baixa de estoque e protecao contra concorrencia permanecem pendentes.

Foi criado o endpoint autenticado `POST /cliente` (`4105447`) no grupo `Farmacia` para salvar `nome`, `cpf`, `telefone` e `esta_registrado`; ele permanece em draft e nao esta publicado no ambiente live. A tela de vendas apresenta os produtos em cartoes com foto, preco e estoque; adicionar um item inicia sua quantidade em 1, permite incluir outros produtos e alterar quantidades dentro do estoque disponivel. Ao selecionar produtos, um botao flutuante no canto inferior direito mostra o total e a quantidade de itens. Ao abrir o carrinho, o operador pode alterar/remover itens, escolher compra sem cadastro ou identificar um cliente cadastrado, ou cadastrar um novo cliente. Clientes com `esta_registrado = true` recebem desconto de 14% no total demonstrativo do carrinho. O historico fica acessivel pelo botao `Historico` no topo da tela, sem ocupar espaco fixo junto ao catalogo; a lista de produtos usa o fluxo normal da pagina em vez de uma area rolavel interna.

O cadastro foi conferido na configuracao do endpoint, sem gravar dados pessoais de teste. O botao de finalizacao fica habilitado quando o carrinho tem itens, mas o endpoint correspondente continua vazio e nao publicado; nao foi criada nenhuma venda. O desconto de 14% continua apenas calculado e exibido no carrinho, nao persistido.

### Foto do produto

A tabela `produto` possui o campo opcional de texto `imagem_url`, visivel para a API, para armazenar o endereco da imagem do produto. O campo foi configurado nos endpoints de gravacao da workspace `169234-0` (`v1` / `live`):

| Metodo e rota | ID no Xano | Configuracao |
|---|---:|---|
| `POST /produto` | `4103434` | `imagem_url` recebe `input.imagem_url` e e gravado no novo registro. |
| `PATCH /produto/{produto_id}` | `4103437` | O endpoint usado pelo frontend atualiza os campos recebidos; inclui `categoria_id`. |
| `PUT /produto/{produto_id}` | `4103438` | Endpoint legado em draft, nao usado pelo frontend. |

O frontend pode enviar a URL na inclusao e na edicao; o `PATCH` usa os campos presentes no corpo da requisicao. A listagem usa o valor retornado para exibir a foto. Produtos sem URL continuam sem imagem e podem mostrar o espaco reservado da interface. A persistencia foi conferida na configuracao dos endpoints, mas nao foi feita uma chamada de teste que criasse ou alterasse um produto real.
