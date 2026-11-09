## ADDED Requirements

### Requirement: Manter o schema de farmácia no Xano

O banco Xano da aplicação MUST manter as tabelas `cliente`, `produto`, `venda`
e `item_venda` com os campos usados pelas APIs e telas de estoque e vendas.
`produto` MUST incluir `imagem_url` como campo opcional para a URL da foto.
`venda` MUST incluir `forma_pagamento` com os valores `dinheiro`, `pix`,
`credito` e `debito`.

#### Scenario: Estrutura do catálogo

- **WHEN** a API lista, cria ou atualiza um produto
- **THEN** os campos usados pelo frontend incluem `nome`, `codigo_barras`,
  `preco`, `estoque_quantidade` e `imagem_url`
- **AND** `imagem_url` pode estar vazia para produtos sem foto

#### Scenario: Estrutura de cliente

- **WHEN** a API cadastra um cliente para uso no carrinho
- **THEN** o registro contém `nome`, `cpf`, `telefone` e `esta_registrado`

#### Scenario: Estrutura de venda e itens

- **WHEN** as APIs consultam ou registram vendas
- **THEN** a venda usa `usuario_id`, `cliente_id`, `valor_total`,
  `desconto_aplicado`, `forma_pagamento` e os campos de data existentes
- **AND** cada item usa `venda_id`, `produto_id`, `quantidade` e
  `preco_unitario`

### Requirement: Expor operações autenticadas de estoque e vendas

As operações de farmácia usadas pelo frontend MUST exigir autenticação e
manter os contratos existentes: `GET /produto`, `POST /produto`,
`GET /produto/{id}`, `PUT /produto/{id}` e `DELETE /produto/{id}`;
`GET /cliente` e `POST /cliente`; e `GET /venda`. Os endpoints de cadastro e
edição de produto MUST aceitar e persistir `imagem_url` quando fornecida.

#### Scenario: Criar ou atualizar produto com foto

- **GIVEN** que o cliente envia `imagem_url` junto aos dados válidos do produto
- **WHEN** `POST /produto` ou `PUT /produto/{produto_id}` conclui a gravação
- **THEN** o registro mantém a URL e a resposta/listagem permite recuperá-la

#### Scenario: Operação sem autenticação

- **WHEN** uma solicitação não autenticada acessa uma operação privada da
  farmácia
- **THEN** o Xano recusa a solicitação sem alterar os registros

### Requirement: Preservar e verificar relacionamentos de banco

Os campos que associam vendas e itens às suas entidades MUST ser referências
de tabela no schema do Xano: `venda.usuario_id` para `user`,
`venda.cliente_id` para `cliente`, `item_venda.venda_id` para `venda` e
`item_venda.produto_id` para `produto`. A documentação MUST refletir os
destinos confirmados no workspace.

#### Scenario: Relacionamentos confirmados

- **WHEN** o schema da aplicação é consultado no Xano
- **THEN** `venda.usuario_id` referencia `user`, `venda.cliente_id` referencia
  `cliente`, `item_venda.venda_id` referencia `venda` e
  `item_venda.produto_id` referencia `produto`
