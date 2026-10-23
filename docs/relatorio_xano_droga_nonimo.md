# Relatorio de alteracoes no Xano — DROGA-NONIMO

**Data:** 19/10/2026  
**Workspace:** Renato's Workspace, workspace `169234-0`  
**Branch e fonte de dados exibidos:** `v1` / `live`

## Objetivo

Preparar no Xano a estrutura inicial do banco para o sistema de farmacia DROGA-NONIMO, com dados ficticios para visualizar e testar o catalogo de produtos.

## Tabelas criadas

| Tabela | ID no Xano | Finalidade | Campos principais |
|---|---:|---|---|
| `cliente` | `908187` | Cadastro de clientes | `nome`, `cpf`, `telefone`, `esta_registrado`, `criado_em`, `atualizado_em` |
| `produto` | `908189` | Catalogo e estoque | `nome`, `codigo_barras`, `preco`, `estoque_quantidade`, `imagem_url`, `criado_em`, `atualizado_em` |
| `venda` | `908190` | Vendas processadas por usuarios | `usuario_id`, `cliente_id`, `valor_total`, `desconto_aplicado`, `criado_em`, `atualizado_em` |
| `item_venda` | `908192` | Produtos e quantidades de cada venda | `venda_id`, `produto_id`, `quantidade`, `preco_unitario`, `criado_em` |

Todas as tabelas possuem um campo `id` inteiro gerado pelo Xano.

## Tabelas padrao preservadas

- `user` (`898415`): mantida sem alteracoes. Ja existiam tres contas antes do trabalho; nenhuma conta adicional foi criada.
- `event_log` (`898416`): mantida sem alteracoes. Seus campos existentes (`user_id`, `action`, `metadata`, `created_at`) cobrem a finalidade de registro de eventos descrita na especificacao, portanto nao foi criada uma tabela duplicada `registro_de_evento`.

## Dados de teste

Foram gerados **3 registros ficticios** em `produto` pelo gerador de testes do Xano. Os nomes sao aleatorios e servem somente para teste visual; podem ser substituidos por produtos definidos pelo projeto. Nenhum cliente ou dado pessoal foi criado.

## APIs de autenticacao verificadas e integradas

O grupo `Authentication` (`api:t7Ptjfi3`) ja possuia os endpoints abaixo; nenhum novo endpoint foi criado:

| Metodo e rota | Uso | Contrato confirmado |
|---|---|---|
| `POST /auth/login` | Login | Recebe `email` e `password`; retorna `authToken` e `user_id`. |
| `POST /auth/signup` | Cadastro | Recebe `name`, `email` e `password`; retorna `authToken` e `user_id`. |
| `GET /reset/request-reset-link` | Solicitar recuperacao | Recebe `email` por query string e envia um magic link de uso unico. |
| `POST /reset/magic-link-login` | Validar magic link | Recebe `magic_token` e `email`; troca o token temporario por `authToken`. |
| `POST /reset/update_password` | Redefinir senha | Endpoint privado; exige Bearer token e recebe `password` e `confirm_password`. |

O endpoint `reset/request-reset-link` foi alterado e publicado para que o magic link aponte para `http://localhost:3000/redefinir-senha?magic_token=...&email=...`, em vez da pagina demo padrao do Xano. A rota Reflex troca o magic token por um token de autenticacao e usa esse token apenas no pedido autenticado de redefinicao. A interface de recuperacao agora apresenta uma resposta neutra sem revelar se o e-mail foi localizado. Nenhum cadastro, login, e-mail ou redefinicao foi executado durante esta alteracao.

**Importante para implantacao:** `localhost:3000` serve somente para testes no computador que executa o frontend. Antes de usar a recuperacao em producao, substituir o destino no endpoint Xano pela URL publica do frontend, preservando o caminho `/redefinir-senha` e os parametros `magic_token` e `email`.

**Privacidade do endpoint publico:** a mensagem exibida no Reflex e generica para qualquer status HTTP, mas isso, sozinho, nao impede um cliente de chamar o endpoint publico diretamente e comparar status e respostas. O proprio `reset/request-reset-link` deve ser atualizado para responder de forma equivalente para e-mails existentes e inexistentes. Essa normalizacao do endpoint ainda esta pendente; nao considerar a protecao contra enumeracao completa ate ela ser testada.

## Pendencia importante: referencias entre tabelas

Os campos `venda.usuario_id`, `venda.cliente_id`, `item_venda.venda_id` e `item_venda.produto_id` foram criados como inteiros. A tentativa de declarar referencias de tabela pelo XanoScript foi rejeitada pelo validador da workspace. Por isso, **a estrutura atual ainda nao aplica referencias/relacionamentos de banco nesses campos**; os valores nao sao validados automaticamente contra as tabelas de origem.

Antes de cadastrar vendas reais, configurar esses campos como **Table Reference** no Xano e confirmar os vinculos:

- `venda.usuario_id` → `user`
- `venda.cliente_id` → `cliente`
- `item_venda.venda_id` → `venda`
- `item_venda.produto_id` → `produto`

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
| `POST /produto` | Criar produto |
| `GET /produto/{id}` | Consultar produto |
| `PUT /produto/{id}` | Atualizar produto |
| `DELETE /produto/{id}` | Excluir produto |
| `GET /cliente` | Listar clientes |
| `POST /cliente` | Cadastrar cliente para uso na tela de vendas |
| `GET /venda` | Consultar historico de vendas |
| `POST /venda` | Criar venda |
| `POST /item_venda` | Criar item de venda |

Foi adicionado a `venda` o campo enum `forma_pagamento`, com os valores `dinheiro`, `pix`, `credito` e `debito`.

O frontend usa `GET /produto`, `GET /cliente` e `GET /venda` para carregar estoque e o catalogo/historico da tela de vendas. A tela de estoque envia `POST` e `PUT` para incluir e editar produtos; a rota `DELETE` existe no Xano, mas nao e oferecida na interface. Embora as rotas de gravacao de venda e item estejam preparadas no Xano, o checkout ainda nao as chama: a finalizacao de venda e a baixa de estoque permanecem pendentes de um endpoint transacional e da aprovacao do escopo correspondente. As respostas de listagem devem ser confirmadas como listas JSON no ambiente Xano antes do uso integrado.

Foi criado o endpoint autenticado `POST /cliente` (`4105447`) no grupo `Farmacia` para salvar `nome`, `cpf`, `telefone` e `esta_registrado`. A tela de vendas apresenta os produtos em cartoes com foto, preco e estoque; adicionar um item inicia sua quantidade em 1, permite incluir outros produtos e alterar quantidades dentro do estoque disponivel. Ao selecionar produtos, um botao flutuante no canto inferior direito mostra o total e a quantidade de itens. Ao abrir o carrinho, o operador pode alterar/remover itens, escolher compra sem cadastro ou identificar um cliente cadastrado, ou cadastrar um novo cliente. Clientes com `esta_registrado = true` recebem desconto de 14% no total demonstrativo do carrinho. O historico fica acessivel pelo botao `Historico` no topo da tela, sem ocupar espaco fixo junto ao catalogo; a lista de produtos usa o fluxo normal da pagina em vez de uma area rolavel interna.

O cadastro foi conferido na configuracao do endpoint, sem gravar dados pessoais de teste. A finalizacao permanece desativada; portanto, o desconto ainda e apenas calculado e exibido no carrinho, nao gravado em uma venda.

### Foto do produto

A tabela `produto` possui o campo opcional de texto `imagem_url`, visivel para a API, para armazenar o endereco da imagem do produto. O campo foi configurado nos endpoints de gravacao da workspace `169234-0` (`v1` / `live`):

| Metodo e rota | ID no Xano | Configuracao |
|---|---:|---|
| `POST /produto` | `4103434` | `imagem_url` recebe `input.imagem_url` e e gravado no novo registro. |
| `PUT /produto/{produto_id}` | `4103438` | `imagem_url` recebe `input.imagem_url` e e gravado na atualizacao do registro correspondente. |

O frontend pode enviar a URL tanto na inclusao quanto na edicao; a listagem usa o valor retornado para exibir a foto. Produtos sem URL continuam sem imagem e podem mostrar o espaco reservado da interface. A persistencia foi conferida na configuracao dos endpoints, mas nao foi feita uma chamada de teste que criasse ou alterasse um produto real.
